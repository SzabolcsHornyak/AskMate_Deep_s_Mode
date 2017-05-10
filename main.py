from flask import Flask, render_template, url_for, redirect
import base64
import time
app = Flask(__name__, static_url_path='/static')


FIELDNAMES = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image', 'edit', 'delete']


def decode_this(string):
    return base64.b64decode(string).decode('utf-8')


def encode_this(string):
    return base64.b64encode(string.encode('utf-8')).decode('utf-8')


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

# ask a question: 1000
# post an answer: 1000
# edit a question: 400
# delete an answer: 400
# add image: 500


# list questions: 1000
# sort questions: 600
@app.route('/')
@app.route('/list')
def list():
    data_set = read_and_decode('./static/data/question.csv')
    return render_template('list.html', data_set=data_set, fieldnames=FIELDNAMES)


# display a question: 1000
@app.route('/question/<int:id>')
def question(id):
        line = read_and_decode('./static/data/question.csv')[id]
        with open('./static/data/answer.csv', 'r') as file:
            all_answers = [line.split(',') for line in file]

        answers = [line for line in all_answers if line[3] == id]

        for ans in answers:
            ans[4] = decode_this(ans[4])
            ans[5] = decode_this(ans[5])

        return render_template('display.html', line=line, fieldnames=FIELDNAMES, answers=answers)


# delete question: 600
@app.route('/question/<int:question_id>/del', methods=["GET", "POST"])
def delete(question_id):
    if request.method == "POST":
        with open('./static/data/question.csv', 'r') as qcsvfile:
            data_set = [line for line in qcsvfile if int(line[0]) != question_id]
        with open('./static/data/question.csv', 'w') as qcsvfile:
            for line in data_set:
                qcsvfile.write(line)
        return redirect(url_for('list'))


# vote: 700
@app.route('/question/<question_id>/<vote>')
def vote(question_id, vote):
    question_id = int(question_id)

    with open('./static/data/question.csv', 'r+') as file:
        data = [line.split(',') for line in file.readlines()]

        if vote == 'vote-up':
            data[question_id][3] = str(int(data[question_id][3]) + 1)
        elif vote == 'vote-down':
            data[question_id][3] = str(int(data[question_id][3]) - 1)

        file.seek(0)
        for line in data:
            file.write(','.join(line))

    return redirect(url_for('question', id=question_id))


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()