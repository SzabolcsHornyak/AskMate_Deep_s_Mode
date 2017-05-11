from flask import Flask, render_template, url_for, redirect, request
from werkzeug.utils import secure_filename
import time
import os
import constants
import utilities
app = Flask(__name__, static_url_path='/static')


app.config['UPLOAD_FOLDER'] = constants.UPLOAD_FOLDER


@app.route('/')
@app.route('/list')
def list():
    '''
    # list questions: 1000
    There should be a page which can display every asked question (/, the root of the app and /list).
    They are sorted by time (most recently asked one at the top). Also you should display an "ask a
    question" link here.
    # sort questions: 600
    The list of questions should be sortable according to: date, votes, number of views
    (both in ascending and descending order) (/list?time=asc;title=desc,...)
    '''
    list_from_query_string = request.query_string.decode('utf-8').split('=')  # refract this if we have some time later
    data_set = utilities.read_and_decode('./static/data/question.csv')
    sort_direction = 'asc'
    try:
        pos = constants.FIELDNAMES.index(list_from_query_string[0])
    except ValueError:
        pos = 1
    try:
        if str(list_from_query_string[1]) == 'asc':
            reverse_boolean = False  # The value of this variable defines the direction
            sort_direction = 'dsc'
        elif str(list_from_query_string[1]) == 'dsc':
            reverse_boolean = True
            sort_direction = 'asc'
        else:
            return render_template('list.html', data_set=data_set, fieldnames=constants.FIELDNAMES, dir=sort_direction)
    except ValueError:
        reverse_boolean = True
    except IndexError:
        return render_template('list.html', data_set=data_set, fieldnames=constants.FIELDNAMES, dir=sort_direction)

    try:
        data_set = sorted(data_set, key=lambda x: int(x[pos]), reverse=reverse_boolean)
    except ValueError:
        pass
    return render_template('list.html', data_set=data_set, fieldnames=constants.FIELDNAMES, dir=sort_direction)


@app.route('/newquestion', methods=['POST', 'GET'])
def new_question():
    '''
    ask a question: 1000
    There should be a page where I can ask a question (/new-question). 
    The question must be at least 10 characters long. 
    After the question is posted it should be displayed.
    '''
    if request.method == 'POST':
        question_data_list = []
        new_id = utilities.id_generator('./static/data/question.csv')
        question_data_list.append(new_id)
        question_data_list.append(str(round(time.time())))  # submission time
        question_data_list.append('0')  # view_number
        question_data_list.append('0')  # vote_number
        question_title = utilities.encode_this(str(request.form['question_title']))
        question_data_list.append(str(question_title))  # question title
        question_message = utilities.encode_this(str(request.form['question_text']))
        question_data_list.append(str(question_message))  # question message
        img_file = ''
        filex = request.files['file']
        if filex.filename != '':
            if filex:
                filex.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filex.filename)))
                img_file = 'images/'+secure_filename(filex.filename)
        question_image = utilities.encode_this(img_file)
        question_data_list.append(str(question_image))  # question image

        question_data_string = ','.join(question_data_list)+','  # PICTURE PROBLEM!
        utilities.append_to_csv(question_data_string[:-1])
        return redirect(url_for('list'))
    return render_template('question.html', data=[])


@app.route('/question/<int:question_id>')
def question(question_id):
        '''
        display a question: 1000
        There should be a page that displays a single question,
        all its data and all its answers (/question/<question_id>).
        '''
        # Update view number
        data_set = utilities.just_read('./static/data/question.csv')
        question_line = utilities.find_line_by_id(data_set, question_id)
        data_set[data_set.index(question_line)][2] = str(int(data_set[data_set.index(question_line)][2]) + 1)
        utilities.write_to_csv(data_set, './static/data/question.csv')

        data_set = utilities.read_and_decode('./static/data/question.csv')
        question_line = utilities.find_line_by_id(data_set, question_id)

        all_answers = utilities.just_read('./static/data/answer.csv')
        answers = [line for line in all_answers if int(line[3]) == question_id]
        for answer in answers:
            answer[1] = time.ctime(int(answer[1]))
            answer[4] = utilities.decode_this(answer[4])  # answer title
            answer[5] = utilities.decode_this(answer[5])  # answer message
        return render_template('display.html',
                               line=question_line,
                               fieldnames=constants.FIELDNAMES,
                               answers=answers,
                               question_id=question_id)


@app.route("/question/<question_id>/new-answer", methods=['GET', 'POST'])
def post_answer(question_id):
    '''
    post an answer: 1000
    There should be a page where I can post an answer to an existing question.
    The answer must be at least 10 characters long. (/question/<question_id>/new-answer).
    There should be a link at each question detail page that leads to this page.
    '''
    if request.method == 'GET':
        data_set = utilities.read_and_decode('./static/data/question.csv')
        question_line = utilities.find_line_by_id(data_set, question_id)
        return render_template('answer.html',
                               question_id=question_id,
                               question_title=question_line[4],
                               question_msg=question_line[5])

    if request.method == 'POST':
        answer_id = utilities.id_generator('./static/data/answer.csv')
        submission_time = str(round(time.time()))
        vote_number = '0'  # can it be minus?
        message = str(utilities.encode_this(request.form['answer_message']))
        image = ''  # TODO
        answer_data_list = [answer_id, submission_time, vote_number, question_id, message, image]
        answer_data_string = ','.join(answer_data_list)
        utilities.append_to_csv(answer_data_string, './static/data/answer.csv')
        return redirect(url_for('question', question_id=question_id))


@app.route('/question/<int:question_id>/<int:answer_id>/del', methods=["POST"])
def delete_answer(question_id, answer_id):
    '''
    delete an answer: 400
    The site should allow to delete posted answers. (/answer/<answer_id>/delete)
    '''
    with open('./static/data/answer.csv', 'r') as acsvfile:
        data_set = [line for line in acsvfile if int(line[0]) != answer_id]
    with open('./static/data/answer.csv', 'w') as acsvfile:
        for line in data_set:
            acsvfile.write(line)

    return redirect(url_for('question', question_id=question_id))


@app.route('/question/<int:question_id>/del', methods=["POST"])
def delete_question(question_id):
    '''
    delete question: 600
    There should be a "delete" button for each question.
    This deletes the question and all its answers (if any),
    and then displays the list of questions.(/question/<question_id>/delete).
    '''
    # Delete question
    with open('./static/data/question.csv', 'r') as qcsvfile:
        data_set = [line for line in qcsvfile if int(line[0]) != question_id]
    with open('./static/data/question.csv', 'w') as qcsvfile:
        for line in data_set:
            qcsvfile.write(line)

    # Delete answers to that question
    all_answers = utilities.just_read('./static/data/answer.csv')
    remaining_answers = [answer for answer in all_answers if int(answer[3]) != question_id]
    utilities.write_to_csv(remaining_answers, './static/data/answer.csv')
    return redirect(url_for('list'))


@app.route('/question/<int:question_id>/<int:answer_id>/<vote>')
def vote_answer(question_id, answer_id, vote):
    '''
    vote: 700
    There should be a "vote up" and a "vote down" button besides each question and answer.
    Each one increases/decreases the vote count for them respectively.
    After sending a vote the page should reload to display the updated vote count.
    '''
    with open('./static/data/answer.csv', 'r+') as file:
        data = [line.split(',') for line in file.readlines()]
        answer_line = utilities.find_line_by_id(data, answer_id)

        if vote == 'vote-up':
            answer_line[2] = str(int(answer_line[2]) + 1)
        elif vote == 'vote-down':
            answer_line[2] = str(int(answer_line[2]) - 1)

    utilities.write_to_csv(data, './static/data/answer.csv')

    return redirect(url_for('question', question_id=question_id))


@app.route('/question/<int:question_id>/vote/<vote>')
def vote_question(question_id, vote):
    '''
    vote: 700
    There should be a "vote up" and a "vote down" button besides each question and answer.
    Each one increases/decreases the vote count for them respectively.
    After sending a vote the page should reload to display the updated vote count.
    (/question/<question_id>/vote-up and vote-down)
    '''
    with open('./static/data/question.csv', 'r+') as file:
        data = [line.split(',') for line in file.readlines()]
        question_line = utilities.find_line_by_id(data, question_id)

        if vote == 'vote-up':
            question_line[3] = str(int(question_line[3]) + 1)
        elif vote == 'vote-down':
            question_line[3] = str(int(question_line[3]) - 1)

    utilities.write_to_csv(data, './static/data/question.csv')

    return redirect(url_for('question', question_id=question_id))


@app.route('/question/<int:question_id>/edit', methods=['POST', 'GET'])
def edit_question(question_id):
    if request.method == 'POST':
        data = utilities.just_read('./static/data/question.csv')
        data_line = utilities.find_line_by_id(data, question_id)

        data_index = data.index(data_line)
        data_line[1] = str(round(time.time()))
        data_line[4] = utilities.encode_this(request.form['question_title'])
        data_line[5] = utilities.encode_this(request.form['question_text'])
        data_line[6] = utilities.encode_this(request.form['question_img'])

        data[data_index] = data_line
        utilities.write_to_csv(data, './static/data/question.csv')

        return redirect(url_for('question', question_id=question_id))

    data = utilities.read_and_decode('./static/data/question.csv')
    data = utilities.find_line_by_id(data, question_id)

    return render_template("question.html", data=data, question_id=question_id, get_type='edit')


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()