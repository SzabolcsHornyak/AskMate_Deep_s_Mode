from flask import Flask, render_template
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
    data_set = read_and_decode('./static/data/question.csv')
    return render_template('list.html', data_set=data_set, fieldnames=FIELDNAMES)


@app.route('/question/<int:id>')
def question(id):
        line = read_and_decode('./static/data/question.csv')[id]
        return render_template('display.html', line=line, fieldnames=FIELDNAMES)


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()