from flask import Flask, render_template
import base64
import time
app = Flask(__name__, static_url_path='/static')


def decode_this(string):
    return base64.b64decode(string).decode('utf-8')


@app.route('/question/<int:question_id>')
def question(question_id):
    fieldnames = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image', 'edit', 'delete']
    with open('./static/data/question.csv', 'r') as qcsvfile:
        data_set = [line.split(',') for line in qcsvfile.readlines()]
        for line in data_set:
            line[1] = time.ctime(int(line[1]))
            line[4] = decode_this(line[4])
            line[5] = decode_this(line[5])
            line[6] = decode_this(line[6])

        line = data_set[question_id]

        return render_template('display.html', line=line, fieldnames=fieldnames)


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
