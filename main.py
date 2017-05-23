from flask import Flask, render_template, url_for, redirect, request
from werkzeug.utils import secure_filename
import time
from datetime import datetime
import os
import constants
import psycopg2
from utilities import execute_sql_statement

app = Flask(__name__, static_url_path='/static')


app.config['UPLOAD_FOLDER'] = constants.UPLOAD_FOLDER


@app.route('/')
@app.route('/list')
def list():
    list_from_query_string = request.query_string.decode('utf-8').split('=')  # refract this if we have some time later
    data_set = execute_sql_statement('SELECT * FROM question;')
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
        data_set = sorted(data_set, key=lambda x: int(x[pos]), reverse=reverse_boolean)  # SQL ORDER_BY query
    except ValueError:
        pass
    return render_template('list.html', data_set=data_set, fieldnames=constants.FIELDNAMES, dir=sort_direction)


@app.route('/newquestion', methods=['POST', 'GET'])
def new_question():
    if request.method == 'POST':
        q_time = datetime.now()  # round this bitch or something
        q_view_number = 0
        q_vote_number = 0
        q_title = str(request.form['question_title'])
        q_message = str(request.form['question_text'])
        filex = request.files['file']
        if filex.filename != '':
            if filex:
                filex.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filex.filename)))
                q_img = 'images/'+secure_filename(filex.filename)
        else:
            q_img = ''
        try:  # refactor this
            # setup connection string
            connect_str = "dbname='szabadon' user='szabadon' host='localhost' password='pringles'"
            # use our connection values to establish a connection
            conn = psycopg2.connect(connect_str)
            # set autocommit option, to do every query when we call it
            conn.autocommit = True
        except Exception as e:
            print("Uh oh, can't connect. Invalid dbname, user or password?")
            print(e)
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
                       VALUES (%s, %s, %s, %s, %s, %s);
                       """, (q_time, q_view_number, q_vote_number, q_title, q_message, q_img))
        return redirect(url_for('list'))
    return render_template('question.html', data=[])


@app.route('/question/<int:question_id>')
def question(question_id):
        # Update view number
        question_line = execute_sql_statement("SELECT * FROM question WHERE id ="+str(question_id)+";")[0]
        answers = execute_sql_statement("SELECT * FROM answer WHERE question_id ="+str(question_id)+";")
        return render_template('display.html',
                               line=question_line,
                               fieldnames=constants.FIELDNAMES,
                               answers=answers,
                               question_id=question_id)


@app.route("/question/<question_id>/new-answer", methods=['GET', 'POST'])
def post_answer(question_id):
    if request.method == 'GET':
        question_line = execute_sql_statement("SELECT * FROM question WHERE id ="+str(question_id)+";")[0]
        return render_template('answer.html',
                               question_id=question_id,
                               question_title=question_line[4],
                               question_msg=question_line[5])

    if request.method == 'POST':
        # refactor this??????
        filex = request.files['file']
        if filex.filename != '':
            if filex:
                filex.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filex.filename)))
                img_file = 'images/'+secure_filename(filex.filename)
                answer_image = utilities.encode_this(img_file)
        else:
            answer_image = ""

        a_time = datetime.now()  # round this bitch or something
        a_vote_number = 0
        a_message = str(request.form['answer_message'])
        try:  # refactor this
            # setup connection string
            connect_str = "dbname='szabadon' user='szabadon' host='localhost' password='pringles'"
            # use our connection values to establish a connection
            conn = psycopg2.connect(connect_str)
            # set autocommit option, to do every query when we call it
            conn.autocommit = True
        except Exception as e:
            print("Uh oh, can't connect. Invalid dbname, user or password?")
            print(e)
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO answer (submission_time, vote_number, question_id, message, image)
                       VALUES (%s, %s, %s, %s, %s);
                       """, (a_time, a_vote_number, question_id, a_message, answer_image))
        return redirect(url_for('question', question_id=question_id))


@app.route('/question/<int:question_id>/<int:answer_id>/del', methods=["POST"])
def delete_answer(question_id, answer_id):
    execute_sql_statement("DELETE FROM answer WHERE id="+str(answer_id)+";")
    return redirect(url_for('question', question_id=question_id))


@app.route('/question/<int:question_id>/del', methods=["POST"])
def delete_question(question_id):
    # LATER! TODO
    '''
    # Delete image if exist
    data_set = utilities.read_and_decode('./static/data/question.csv')
    question_line = utilities.find_line_by_id(data_set, question_id)
    print(question_line[6])
    if question_line[6] != '':
        if os.path.isfile('static/' + question_line[6]):
            os.remove('static/' + question_line[6])
    '''
    execute_sql_statement("DELETE FROM question WHERE id="+str(question_id)+";")
    return redirect(url_for('list'))


@app.route('/question/<int:question_id>/<int:answer_id>/<vote>')
def vote_answer(question_id, answer_id, vote):
    vote_nr = execute_sql_statement("SELECT vote_number FROM answer WHERE id ="+str(answer_id)+";")[0][0]

    if vote == 'vote-up':
        vote_nr += 1
    elif vote == 'vote-down':
        vote_nr -= 1

    execute_sql_statement("UPDATE answer SET vote_number="+str(vote_nr)+"WHERE id ="+str(answer_id)+";")

    return redirect(url_for('question', question_id=question_id))


@app.route('/question/<int:question_id>/vote/<vote>')
def vote_question(question_id, vote):
    vote_nr = execute_sql_statement("SELECT vote_number FROM question WHERE id ="+str(question_id)+";")[0][0]

    if vote == 'vote-up':
        vote_nr += 1
    elif vote == 'vote-down':
        vote_nr -= 1

    execute_sql_statement("UPDATE question SET vote_number="+str(vote_nr)+"WHERE id ="+str(question_id)+";")

    return redirect(url_for('question', question_id=question_id))


@app.route('/question/<int:question_id>/edit', methods=['POST', 'GET'])
def edit_question(question_id):
    if request.method == 'POST':
        q_time = datetime.now()  # round this bitch or something
        q_view_number = 0
        q_vote_number = 0
        q_title = str(request.form['question_title'])
        q_message = str(request.form['question_text'])
        filex = request.files['file']
        if filex.filename != '':
            if filex:
                filex.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filex.filename)))
                q_img = 'images/'+secure_filename(filex.filename)
        else:
            q_img = ''
        try:  # refactor this
            # setup connection string
            connect_str = "dbname='szabadon' user='szabadon' host='localhost' password='pringles'"
            # use our connection values to establish a connection
            conn = psycopg2.connect(connect_str)
            # set autocommit option, to do every query when we call it
            conn.autocommit = True
        except Exception as e:
            print("Uh oh, can't connect. Invalid dbname, user or password?")
            print(e)
        cursor = conn.cursor()
        cursor.execute("""
                       UPDATE question
                       SET
                       submission_time=%s,view_number=%s,vote_number=%s,title=%s,message=%s,image=%s
                       WHERE id=%s;""",
                       (q_time, q_view_number, q_vote_number, q_title, q_message, q_img, question_id))
        return redirect(url_for('question', question_id=question_id))

    data = execute_sql_statement("SELECT * FROM question WHERE id ="+str(question_id)+";")[0]

    return render_template("question.html", data=data, question_id=question_id, get_type='edit')


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()