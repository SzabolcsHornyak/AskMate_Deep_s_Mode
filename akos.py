from flask import Flask, render_template, url_for, redirect, request
from werkzeug.utils import secure_filename
import time
from datetime import datetime
import os
import constants
import psycopg2
from utilities import encode_this
from utilities import execute_sql_statement

app = Flask(__name__, static_url_path='/static')

app.config['UPLOAD_FOLDER'] = constants.UPLOAD_FOLDER

@app.route('/')
def get_list_5():
    data_set = execute_sql_statement("SELECT * FROM question order by submission_time DESC limit 5;")
    sort_direction = 'asc' 
    return render_template('list.html', data_set=data_set, fieldnames=constants.FIELDNAMES, dir=sort_direction)


@app.route('/list')
def list():
    data_set = execute_sql_statement("SELECT * FROM question order by submission_time DESC;")
    sort_direction = 'asc' 
    '''
    list_from_query_string = request.query_string.decode('utf-8').split('=')
    if len(list_from_query_string) == 2:
        b = list_from_query_string[0]
        if str(list_from_query_string[1]) == 'asc':
            sort_direction = 'dsc'
            execute_sql_statement("SELECT * FROM question ORDER BY %s DESC;", (b,))
        elif str(list_from_query_string[1]) == 'dsc':
            sort_direction = 'asc'
            execute_sql_statement("SELECT * FROM question ORDER BY %s ASC;", (b,))
    except IndexError:
        pass'''
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
        execute_sql_statement("""
                       INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
                       VALUES (%s, %s, %s, %s, %s, %s);
                       """, (q_time, q_view_number, q_vote_number, q_title, q_message, q_img))
        return redirect(url_for('list'))
    return render_template('question.html', data=[])


@app.route('/question/<int:question_id>')
def question(question_id):
        question_line = execute_sql_statement("SELECT * FROM question WHERE id =  %s;", (question_id,))[0]
        answers = execute_sql_statement("SELECT * FROM answer WHERE question_id = %s;", (question_id,))
        question_comments = execute_sql_statement("SELECT * FROM comment WHERE question_id = %s;", (question_id,))
        answer_ids = [answer[0] for answer in answers]

        answer_comments = []
        for answer_id in answer_ids:
            answer_comments.append(execute_sql_statement("SELECT * FROM comment WHERE answer_id = %s", (answer_id,)))

        return render_template('display.html',
                               line=question_line,
                               fieldnames=constants.FIELDNAMES,
                               answers=answers,
                               question_comments=question_comments,
                               answer_comments=answer_comments,
                               question_id=question_id)


@app.route("/question/<question_id>/new-answer", methods=['GET', 'POST'])
def post_answer(question_id):
    if request.method == 'GET':
        question_line = execute_sql_statement("SELECT * FROM question WHERE id = %s;", (question_id,))[0]
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
                answer_image = 'images/'+secure_filename(filex.filename)
        else:
            answer_image = ""

        a_time = datetime.now()  # round this bitch or something
        a_vote_number = 0
        a_message = str(request.form['answer_message'])
        execute_sql_statement("""
                       INSERT INTO answer (submission_time, vote_number, question_id, message, image)
                       VALUES (%s, %s, %s, %s, %s);
                       """, (a_time, a_vote_number, question_id, a_message, answer_image))
        return redirect(url_for('question', question_id=question_id))


@app.route('/question/<int:question_id>/<int:answer_id>/del', methods=["POST"])
def delete_answer(question_id, answer_id):
    execute_sql_statement("DELETE FROM answer WHERE id= %s;", (answer_id,))
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
    execute_sql_statement("DELETE FROM question WHERE id=%s;", (question_id,))
    return redirect(url_for('list'))


@app.route('/question/<int:question_id>/<int:answer_id>/<vote>')
def vote_answer(question_id, answer_id, vote):
    vote_nr = execute_sql_statement("SELECT vote_number FROM answer WHERE id = %s;", (answer_id,))[0][0]

    if vote == 'vote-up':
        vote_nr += 1
    elif vote == 'vote-down':
        vote_nr -= 1

    execute_sql_statement("UPDATE answer SET vote_number= %s WHERE id = %s;", (vote_nr, answer_id))

    return redirect(url_for('question', question_id=question_id))


@app.route('/question/<int:question_id>/vote/<vote>')
def vote_question(question_id, vote):
    vote_nr = execute_sql_statement("SELECT vote_number FROM question WHERE id = %s;", (question_id,))[0][0]

    if vote == 'vote-up':
        vote_nr += 1
    elif vote == 'vote-down':
        vote_nr -= 1

    execute_sql_statement("UPDATE question SSET vote_number= %s WHERE id = %s;", (vote_nr, question_id))

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
        execute_sql_statement("""
                              UPDATE question
                              SET
                              submission_time=%s,view_number=%s,vote_number=%s,title=%s,message=%s,image=%s
                              WHERE id=%s;
                              """,
                              (q_time, q_view_number, q_vote_number, q_title, q_message, q_img, question_id))
        return redirect(url_for('question', question_id=question_id))

    data = execute_sql_statement("SELECT * FROM question WHERE id ="+str(question_id)+";")[0]

    return render_template("question.html", data=data, question_id=question_id, get_type='edit')


@app.route('/search')
def search_results():
    search_phrase = '%'+str(request.query_string.decode('utf-8'))[2:]+'%'
    search_result = execute_sql_statement("""SELECT * FROM question
                                          WHERE (message LIKE %s
                                          OR title LIKE %s);""", (search_phrase, search_phrase))
    return render_template('list.html', data_set=search_result, fieldnames=constants.FIELDNAMES, dir='asc')


###############################################################################################################
#                                               ANSWER                                                        #
###############################################################################################################
@app.route('/answer/<int:answer_id>')
def display_answer(answer_id):
    answer_line = execute_sql_statement("SELECT * FROM answer WHERE id =  %s;", (answer_id,))[0]
    comments = execute_sql_statement("SELECT * FROM comment WHERE answer_id = %s;", (answer_id,))

    return render_template("display_answer.html", line=answer_line, comments=comments)


###############################################################################################################
#                                               COMMENTS                                                      #
###############################################################################################################
@app.route("/question/<question_id>/new-comment", methods=['GET', 'POST'])
def post_question_comment(question_id):
    if request.method == 'GET':
        question_line = execute_sql_statement("SELECT * FROM question WHERE id = %s;", (question_id,))[0]
        return render_template('new_question_comment.html',
                               question_id=question_id,
                               question_title=question_line[4],
                               question_msg=question_line[5])

    if request.method == 'POST':
        comment_time = datetime.now()
        comment_message = request.form['comment_message']
        comment_edits = 0
        question_line = execute_sql_statement("""INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count)
                                                VALUES (%s, NULL, %s, %s, %s);""",
                                              (question_id, comment_message, comment_time, comment_edits))

        return redirect(url_for('question', question_id=question_id))


@app.route("/answer/<int:answer_id>/new-comment", methods=['GET', 'POST'])
def post_answer_comment(answer_id):
    answer_line = execute_sql_statement("SELECT * FROM answer WHERE id = %s;", (answer_id,))[0]
    if request.method == 'GET':
        return render_template('new_answer_comment.html',
                               answer_id=answer_id,
                               answer_message=answer_line[4],)

    if request.method == 'POST':
        comment_time = datetime.now()
        comment_message = request.form['comment_message']
        comment_edits = 0
        execute_sql_statement("""INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count)
                                 VALUES (NULL, %s, %s, %s, %s);""",
                              (answer_id, comment_message, comment_time, comment_edits))

        return redirect(url_for('question', question_id=answer_line[3]))


@app.route('/comments/<int:comment_id>/del', methods=["POST"])
def delete_comment(comment_id):
    comment = execute_sql_statement("""SELECT * FROM comment WHERE id = %s;""", (comment_id,))[0]

    if comment[1] is not None:
        question_id = execute_sql_statement("""SELECT question_id FROM comment WHERE id = %s;""", (comment_id,))[0][0]
    else:
        answer_id = execute_sql_statement("""SELECT answer_id FROM comment WHERE id = %s;""", (comment_id,))[0][0]
        question_id = execute_sql_statement("""SELECT question_id FROM answer WHERE id = %s;""", (answer_id,))[0][0]

    execute_sql_statement("DELETE FROM comment WHERE id= %s;", (comment_id,))
    return redirect(url_for('question', question_id=question_id))


@app.route('/comments/<int:comment_id>/edit', methods=["POST", "GET"])
def edit_comment(comment_id):
    comment = execute_sql_statement("""SELECT * FROM comment WHERE id=%s;""", (comment_id,))[0]
    comment_message = comment[3]
    
    if request.method == 'GET':
        if comment[1] is not None:
            question_id = comment[1]
            question_line = execute_sql_statement("SELECT * FROM question WHERE id = %s;", (question_id,))[0]
            return render_template('new_question_comment.html',
                                comment_id=comment_id,
                                comment_message=comment_message,
                                question_id=question_id,
                                question_title=question_line[4],
                                question_msg=question_line[5])
        else:
            answer_id = execute_sql_statement("""SELECT answer_id FROM comment WHERE id = %s;""", (comment_id,))[0][0]
            data = execute_sql_statement("""SELECT message FROM answer WHERE id = %s;""", (answer_id,))[0]

            return render_template('new_answer_comment.html',
                                   answer_message=data[0],
                                   answer_id=answer_id,
                                   comment_id=comment_id,
                                   comment_message=comment_message)

    if request.method == "POST":
        # update sql
        if comment[1] is not None:
            question_id = comment[1]
            execute_sql_statement("""
                                  UPDATE comment
                                  SET
                                  message=%s, submission_time=%s
                                  WHERE id=%s;
                                  """,
                                  (request.form['comment_message'], datetime.now(), comment_id))

            return redirect(url_for('question', question_id=question_id))

        else:
            answer_id = execute_sql_statement("""SELECT answer_id FROM comment WHERE id = %s;""", (comment_id,))[0][0]
            execute_sql_statement("""
                                  UPDATE comment
                                  SET
                                  message=%s, submission_time=%s
                                  WHERE id=%s;
                                  """,
                                  (request.form['comment_message'], datetime.now(), comment_id))
            return redirect(url_for('display_answer', answer_id=answer_id))

###############################################################################################################
#                                               TAGs                                                          #
###############################################################################################################
@app.route('/question/<question_id>/new-tag', methods=['POST', 'GET'])
def new_tag(question_id):
    if request.method == 'GET':
        question_line = execute_sql_statement("SELECT * FROM question WHERE id = %s;", (question_id,))[0]
        existing_tags = execute_sql_statement("SELECT name FROM tag;")
        return render_template('new-tag.html',
                               question_id=question_id,
                               question_title=question_line[4],
                               question_msg=question_line[5],
                               tags=existing_tags)

    if request.method == 'POST':
        try:
            tag_name = str(request.form['tag_name'])
            try:
                tag_id = execute_sql_statement("SELECT id FROM tag WHERE name=%s;", (tag_name,))[0]
            except IndexError:
                execute_sql_statement("INSERT INTO tag (name) VALUES (%s);", (tag_name,))
                tag_id = execute_sql_statement("SELECT id FROM tag WHERE name=%s;", (tag_name,))[0]
            execute_sql_statement("INSERT INTO question_tag (question_id, tag_id) VALUES (%s, %s);",
                                  (question_id, tag_id))
        except psycopg2.IntegrityError:
            pass
        return redirect(url_for('question', question_id=question_id))


###############################################################################################################
#                                               OTHERS                                                        #
###############################################################################################################
@app.route("/delete_unused_images")
def delete_unused_images():
    local_images = next(os.walk(constants.UPLOAD_FOLDER))[2]
    db_images = execute_sql_statement("SELECT image FROM question where image is not null union all SELECT image FROM answer where answer is not null")
    match = []
    for i in range(len(local_images)):
        for j in range(len(db_images)):
            if str(db_images[j][0]).lower() == str('images/'+local_images[i]).lower():
                match.append(db_images[j][0])
    for i in range(len(local_images)):
        if str('images/'+local_images[i]).lower() not in match:
            del_file = constant.UPLOAD_FOLDER + '/' + local_images[i]
            os.remove(del_file)
    return redirect(url_for('list'))


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
