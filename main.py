from flask import Flask, render_template, url_for, redirect, request
import base64
import time
app = Flask(__name__, static_url_path='/static')


FIELDNAMES = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image', 'edit', 'delete']


def decode_this(string):
    return base64.b64decode(string).decode('utf-8')


def encode_this(string):
    return base64.b64encode(string.encode('utf-8')).decode('utf-8')


def just_read(file):
    with open(file, 'r') as qcsvfile:
        return [line.split(',') for line in qcsvfile]


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


def write_qcsv(question_data):
    with open('./static/data/question.csv', 'a') as qcsvfile:
        qcsvfile.write(question_data+'\n')


def id_gen(file_path):
    data_set = just_read(file_path)
    return str(int(data_set[-1][0]) + 1)

# TODO
# overall testing and bugfixes
# edit a question: 400
# delete an answer: 400
# add image: 500


# list questions: 1000
# sort questions: 600
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


# ask a question: 1000
@app.route('/newquestion', methods=['POST', 'GET'])
def new_question():
    if request.method == 'POST':
        question_data = []
        new_id = id_gen('./static/data/question.csv')
        question_data.append(new_id)
        question_data.append(str(round(time.time())))
        question_data.append('0')  # view_number
        question_data.append('0')  # vote_number
        question_title = encode_this(str(request.form['q_title']))
        question_data.append(str(question_title))
        question_message = encode_this(str(request.form['q_text']))
        question_data.append(str(question_message))
        question_data = ','.join(question_data)+','  # PICTURE PROBLEM!
        write_qcsv(question_data)
        return redirect(url_for('list'))
    return render_template('new_quest.html', data=[])


# display a question: 1000
@app.route('/question/<int:id_>')
def question(id_):
        content = read_and_decode('./static/data/question.csv')
        i = 0
        while i < len(content) - 1 and content[i][0] != str(id_):
            i += 1
        line = content[i]

        with open('./static/data/answer.csv', 'r') as file:
            all_answers = [line.split(',') for line in file]

        answers = [line for line in all_answers if int(line[3]) == id_]

        for ans in answers:
            ans[4] = decode_this(ans[4])
            ans[5] = decode_this(ans[5])

        return render_template('display.html', line=line, fieldnames=FIELDNAMES, answers=answers, question_id=id_)


# post an answer: 1000
@app.route("/question/<question_id>/new-answer", methods=['GET', 'POST'])
def post_answer(question_id):

    if request.method == 'GET':
        with open('./static/data/question.csv', 'r') as file:
            question_ = [line.split(',') for line in file if line.split(',')[0] == question_id][0]
            question_title = base64.b64decode(question_[4]).decode('utf-8')
            question_msg = base64.b64decode(question_[5]).decode('utf-8')

        return render_template('a_answer.html', question_id=question_id, question_title=question_title, question_msg=question_msg)

    if request.method == 'POST':
        with open('./static/data/answer.csv', 'a+') as file:
            answer_id = id_gen('./static/data/answer.csv')
            submission_time = str(round(time.time()))
            vote_number = '0'  # can it be minus?
            message = str(encode_this(request.form['answer_message']))
            image = ''  # TODO
            # question_id = str(question_id)

            x = [answer_id, submission_time, vote_number, question_id, message, image]

            # x = list(map(str, y))
            answer_data = ','.join(x)
            file.write(answer_data + "\n")

        return redirect(url_for('question', id_=question_id))


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

    return redirect(url_for('question', id_=question_id))


@app.route('/question/<int:question_id>/edit')
def edit_question(question_id):
    data = read_and_decode('./static/data/question.csv')
    i = 0
    while question_id != int(data[i][0]):
        i += 1
    data = data[i]

    return render_template("new_quest.html", data=data)

def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()