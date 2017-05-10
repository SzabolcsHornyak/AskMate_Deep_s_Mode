from flask import Flask, render_template, request, redirect, url_for
import base64
import time
app = Flask(__name__, static_url_path='/static')


def decode_this(string):
    return base64.b64decode(string).decode('utf-8')


FIELDNAMES = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image', 'edit', 'delete']


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


@app.route('/question/<int:question_id>')
def question(question_id):
    line = read_and_decode('./static/data/question.csv')[question_id]
    return render_template('display.html', line=line, fieldnames=FIELDNAMES)


@app.route('/question/<int:question_id>/del', methods=["GET", "POST"])
def delete(question_id):
    if request.method == "POST":
        with open('./static/data/question.csv', 'r') as qcsvfile:
            data_set = [line for line in qcsvfile if int(line[0]) != question_id]
        with open('./static/data/question.csv', 'w') as qcsvfile:
            for line in data_set:
                qcsvfile.write(line)
        return redirect(url_for('list'))


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
