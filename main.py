from flask import Flask, render_template, url_for, redirect, request
import base64
import time
app = Flask(__name__, static_url_path='/static')


FIELDNAMES = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message',
              'image', 'edit', 'delete', 'vote']


def decode_this(string):
    '''Takes a base64 string and decodes it to human-readable value.'''
    return base64.b64decode(string).decode('utf-8')


def encode_this(string):
    '''Takes a human-readable string and encodes it to a base64 value.'''
    return base64.b64encode(string.encode('utf-8')).decode('utf-8')


def just_read(file_path):
    '''Takes a csv file and makes a raw 2d table from it.'''
    with open(file_path, 'r') as csvfile:
        return [line.split(',') for line in csvfile]


def read_and_decode(file_path):
    '''
    Sorts by second value, then decodes
    the second, fifth, sixth and seventh values
    to a human-readable format and returns it
    in a 2d table (list of list).
    '''
    data_set = just_read(file_path)
    data_set = sorted(data_set, key=lambda x: x[1], reverse=True)
    for line in data_set:
        line[1] = time.ctime(int(line[1]))
        line[4] = decode_this(line[4])
        line[5] = decode_this(line[5])
        line[6] = decode_this(line[6])
    return data_set


def append_to_csv(data_string, file_path='./static/data/question.csv'):
    '''
    Takes a string and appends to the file.
    '''
    with open(file_path, 'a') as csvfile:
        csvfile.write(data_string+'\n')


def write_to_csv(data_list, file_path):
    '''
    Takes a list and writes it to the file.
    '''
    with open(file_path, 'w') as csvfile:
        for line in data_list:
            line = ','.join(line)
            csvfile.write(line)


def id_generator(file_path):
    '''
    Takes the first value of the last line from the file,
    adds 1 to it and returns the value as a string.
    '''
    data_set = just_read(file_path)
    return str(int(data_set[-1][0]) + 1)


def find_line_by_id(data_set, question_id):
        '''
        Finds question data line by question_id in 2d table (list in list) and returns it.
        '''
        i = 0
        while i < len(data_set) - 1 and data_set[i][0] != str(question_id):
            i += 1
        return data_set[i]

# TODO
# overall testing and bugfixes
# edit a question: 400
# add image: 500


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
    data_set = read_and_decode('./static/data/question.csv')
    sort_direction = 'asc'
    try:
        pos = FIELDNAMES.index(list_from_query_string[0])
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
            return render_template('list.html', data_set=data_set, fieldnames=FIELDNAMES, dir=sort_direction)
    except ValueError:
        reverse_boolean = True
    except IndexError:
        return render_template('list.html', data_set=data_set, fieldnames=FIELDNAMES, dir=sort_direction)

    try:
        data_set = sorted(data_set, key=lambda x: int(x[pos]), reverse=reverse_boolean)
    except ValueError:
        pass
    return render_template('list.html', data_set=data_set, fieldnames=FIELDNAMES, dir=sort_direction)


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
        new_id = id_generator('./static/data/question.csv')
        question_data_list.append(new_id)
        question_data_list.append(str(round(time.time())))  # submission time
        question_data_list.append('0')  # view_number
        question_data_list.append('0')  # vote_number
        question_title = encode_this(str(request.form['q_title']))
        question_data_list.append(str(question_title))  # question title
        question_message = encode_this(str(request.form['q_text']))
        question_data_list.append(str(question_message))  # question message
        question_data_string = ','.join(question_data_list)+','  # PICTURE PROBLEM!
        append_to_csv(question_data_string)
        return redirect(url_for('list'))
    return render_template('question.html', data=[])


@app.route('/question/<int:question_id>')
def question(question_id):
        '''
        display a question: 1000
        There should be a page that displays a single question, 
        all its data and all its answers (/question/<question_id>).
        '''
        data_set = read_and_decode('./static/data/question.csv')
        question_line = find_line_by_id(data_set, question_id)
        all_answers = just_read('./static/data/answer.csv')
        answers = [line for line in all_answers if int(line[3]) == question_id]
        for answer in answers:
            answer[1] = time.ctime(int(answer[1]))
            answer[4] = decode_this(answer[4])  # answer title
            answer[5] = decode_this(answer[5])  # answer message
        return render_template('display.html',
                               line=question_line,
                               fieldnames=FIELDNAMES,
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
        data_set = read_and_decode('./static/data/question.csv')
        question_line = find_line_by_id(data_set, question_id)
        return render_template('answer.html',
                               question_id=question_id,
                               question_title=question_line[4],
                               question_msg=question_line[5])

    if request.method == 'POST':
        answer_id = id_generator('./static/data/answer.csv')
        submission_time = str(round(time.time()))
        vote_number = '0'  # can it be minus?
        message = str(encode_this(request.form['answer_message']))
        image = ''  # TODO
        answer_data_list = [answer_id, submission_time, vote_number, question_id, message, image]
        answer_data_string = ','.join(answer_data_list)
        append_to_csv(answer_data_string, './static/data/answer.csv')
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
    all_answers = just_read('./static/data/answer.csv')
    remaining_answers = [answer for answer in all_answers if int(answer[3]) != question_id]
    write_to_csv(remaining_answers, './static/data/answer.csv')
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
        answer_line = find_line_by_id(data, answer_id)

        if vote == 'vote-up':
            answer_line[2] = str(int(answer_line[2]) + 1)
        elif vote == 'vote-down':
            answer_line[2] = str(int(answer_line[2]) - 1)

    write_to_csv(data, './static/data/answer.csv')

    return redirect(url_for('question', question_id=question_id))


@app.route('/question/<int:question_id>/<vote>')
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
        question_line = find_line_by_id(data, question_id)

        if vote == 'vote-up':
            question_line[3] = str(int(question_line[3]) + 1)
        elif vote == 'vote-down':
            question_line[3] = str(int(question_line[3]) - 1)

    write_to_csv(data, './static/data/question.csv')

    return redirect(url_for('question', question_id=question_id))


@app.route('/question/<int:question_id>/edit')
def edit_question(question_id):
    data = read_and_decode('./static/data/question.csv')
    i = 0
    while question_id != int(data[i][0]):
        i += 1
    data = data[i]

    return render_template("question.html", data=data)


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
