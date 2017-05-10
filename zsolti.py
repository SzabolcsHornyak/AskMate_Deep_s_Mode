from flask import Flask, render_template, request
import base64
import time
app = Flask(__name__, static_url_path='/static')


FIELDNAMES = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image', 'edit', 'delete']


def decode_this(string):
    return base64.b64decode(string).decode('utf-8')


def read_and_decode(file):
    with open(file, 'r') as qcsvfile:
        data_set = [line.split(',') for line in qcsvfile]
        data_set = sorted(data_set, key=lambda x: x[1], reverse=True)
        for line in data_set:
            line[1] = time.ctime(int(line[1]))
            line[4] = decode_this(line[4])
            line[5] = decode_this(line[5])
            line[6] = decode_this(line[6])
    return data_set


@app.route('/')
@app.route('/list')
def list():
    query_string = request.query_string.decode('utf-8').split('=')
    data_set = read_and_decode('./static/data/question.csv')
    next_ = 'asc'
    try:
        pos = FIELDNAMES.index(query_string[0])
    except ValueError:
        pos = 1
    try:
        if str(query_string[1]) == 'asc':
            dir_ = False
            next_ = 'dsc'
        elif str(query_string[1]) == 'dsc':
            dir_ = True
            next_ = 'asc'
        else:
            return '404.html'
    except ValueError:
        dir_ = True
    except IndexError:
        return render_template('list.html', data_set=data_set, fieldnames=FIELDNAMES, dir=next_)

    try:
        data_set = sorted(data_set, key=lambda x: int(x[pos]), reverse=dir_)
    except ValueError:
        pass
    return render_template('list.html', data_set=data_set, fieldnames=FIELDNAMES, dir=next_)


@app.route('/list?<item>=<direction>')
def sort_dataset(item, direction):
    try:
        pos = FIELDNAMES.index(item)
    except ValueError:
        return '404.html'

    if direction == 'asc':
        dir_ = False
    elif direction == 'dsc':
        dir_ = True
    else:
        return '404.html'

    data_set = read_and_decode('./static/data/question.csv')
    data_set = sorted(data_set, key=lambda x: x[pos], reverse=dir_)
    return render_template('list.html', data_set=data_set, fieldnames=FIELDNAMES)


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()

