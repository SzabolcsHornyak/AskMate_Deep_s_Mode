from flask import Flask, render_template, url_for, redirect, request
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import constants
import psycopg2
from askmate_package.db_handling import execute_sql_statement
from askmate_package import vote_module, question_module, user_module, answer_module

app = Flask(__name__, static_url_path='/static')

app.config['UPLOAD_FOLDER'] = constants.UPLOAD_FOLDER


###############################################################################################################
#                                    REGISTRATION                                                             #
###############################################################################################################
@app.route('/registration', methods=['POST', 'GET'])
def registration():
    '''
    As a user I would like to have the possibility to register a new user into the system. (/registration). A user
    only has a username and the date of the registration.
    '''
    if request.method == 'GET':
        return render_template('user_registration.html')
    if request.method == 'POST':
        user_name = request.form['user_name']
        time_of_registration = datetime.now()
        user_reputation = 0
        execute_sql_statement("""INSERT INTO users (username, registration_time, reputation) VALUES (%s, %s, %s)""",
                              (user_name, time_of_registration.replace(microsecond=0), user_reputation))
        return redirect(url_for('get_list_of_questions'))


###############################################################################################################
#                                     LIST QUESTIONS                                                          #
###############################################################################################################
@app.route('/')
def get_limited_list_of_questions():
    '''
    Delivers a list of questions from question table, ordered by submission time, limited their number to five.
    '''
    data_set = execute_sql_statement("SELECT * FROM question order by submission_time DESC limit 5;")
    return render_template('list_questions.html', data_set=data_set, fieldnames=constants.FIELDNAMES, dir='asc')


@app.route('/list')
def get_list_of_questions():
    '''
    Delivers a list of all questions from question table.
    '''
    data_set = execute_sql_statement("SELECT * FROM question order by submission_time DESC;")
    sort_direction = 'asc'
    list_from_query_string = request.query_string.decode('utf-8').split('=')
    try:
        if len(list_from_query_string) == 2:
            column = list_from_query_string[0].encode('utf-8')
            if str(list_from_query_string[1]) == 'asc':
                sort_direction = 'dsc'
                data_set = execute_sql_statement("SELECT * FROM question ORDER BY %s DESC;", (column,))

            elif str(list_from_query_string[1]) == 'desc':
                sort_direction = 'asc'
                data_set = execute_sql_statement("SELECT * FROM question ORDER BY %s ASC;", (column,))

    except IndexError:
        pass
    return render_template('list_questions.html', data_set=data_set, fieldnames=constants.FIELDNAMES, dir=sort_direction)


###############################################################################################################
#                                           QUESTION                                                          #
###############################################################################################################
@app.route('/newquestion', methods=['POST', 'GET'])
def new_question():
    if request.method == 'POST':
        q_img = question_module.new_question_image_handling(request.files['file'], app, True)
        question_module.insert_new_question_into_database(request.form, q_img)
        return redirect(url_for('get_list_of_questions'))
    all_users = execute_sql_statement("SELECT username FROM users;")
    return render_template('post_question.html', data=[], usernames=all_users)


@app.route('/question/<int:question_id>')
def display_question(question_id):
    question_line = execute_sql_statement("SELECT * FROM question WHERE id =  %s;", (question_id,))[0]
    question_user = execute_sql_statement("SELECT username FROM users WHERE id= %s;", (question_line[7],))[0][0]
    question_comments = execute_sql_statement("SELECT * FROM comment WHERE question_id = %s;", (question_id,))
    answer_data = question_module.get_question_answers_for_display(question_id)
    question_tags = question_module.get_question_tags_for_display(question_id)
    return render_template('display_question.html',
                           line=question_line,
                           question_comments=question_comments,
                           fieldnames=constants.FIELDNAMES,
                           answers=answer_data[0],
                           answer_comments=answer_data[1],
                           question_id=question_id,
                           question_tags=question_tags,
                           question_user=question_user)


@app.route('/question/<int:question_id>/edit', methods=['POST', 'GET'])
def edit_question(question_id):
    if request.method == 'POST':
        q_img = question_module.new_question_image_handling(request.files['file'], app)
        if q_img:
            execute_sql_statement("""UPDATE question SET image=%s WHERE id=%s;""", (q_img, question_id))
        question_module.update_question(request.form, question_id)
        return redirect(url_for('display_question', question_id=question_id))
    data = execute_sql_statement("SELECT * FROM question WHERE id=%s;", (question_id,))[0]
    return render_template("post_question.html", data=data, question_id=question_id, get_type='edit')


@app.route('/question/<int:question_id>/del', methods=["POST"])
def delete_question(question_id):
    question_module.delete_image(question_id)
    execute_sql_statement("DELETE FROM question WHERE id=%s;", (question_id,))
    return redirect(url_for('get_list_of_questions'))


###############################################################################################################
#                                             ANSWER                                                          #
###############################################################################################################
@app.route('/answer/<int:answer_id>')
def display_answer(answer_id):
    answer_line = execute_sql_statement("SELECT * FROM answer WHERE id =  %s;", (answer_id,))[0]
    comments = execute_sql_statement("SELECT * FROM comment WHERE answer_id = %s;", (answer_id,))

    return render_template("display_answer.html", answer=answer_line, comments=comments)


@app.route("/question/<question_id>/new-answer", methods=['GET', 'POST'])
def post_answer(question_id):
    if request.method == 'GET':
        question_line = execute_sql_statement("SELECT * FROM question WHERE id = %s;", (question_id,))[0]
        all_users = execute_sql_statement("SELECT username FROM users;")
        return render_template('post_answer.html',
                               question_id=question_id,
                               question_title=question_line[4],
                               question_msg=question_line[5],
                               usernames=all_users)

    if request.method == 'POST':
        filex = request.files['file']
        if filex.filename != '':
            if filex:
                filex.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filex.filename)))
                answer_image = 'images/'+secure_filename(filex.filename)
        else:
            answer_image = ""

        a_time = datetime.now().replace(microsecond=0)
        a_vote_number = 0
        a_message = str(request.form['answer_message'])
        known_user = request.form['username']
        known_user_id = execute_sql_statement("SELECT id FROM users WHERE username=%s;", (known_user,))[0]
        execute_sql_statement("""
                       INSERT INTO answer (submission_time, vote_number, question_id, message, image, user_id)
                       VALUES (%s, %s, %s, %s, %s, %s);
                       """, (a_time, a_vote_number, question_id, a_message, answer_image, known_user_id))
        return redirect(url_for('display_question', question_id=question_id))


@app.route('/question/<int:question_id>/<int:answer_id>/del', methods=["POST"])
def delete_answer(question_id, answer_id):
    execute_sql_statement("DELETE FROM answer WHERE id= %s;", (answer_id,))
    return redirect(url_for('display_question', question_id=question_id))


###############################################################################################################
#                                               VOTE                                                          #
###############################################################################################################
@app.route('/question/<int:question_id>/<int:answer_id>/<vote_direction>')
def vote_answer(question_id, answer_id, vote_direction):
    vote_module.change_vote('answer', answer_id, vote_direction)
    if vote_direction.lower() == "vote-up":
        user_id = user_module.userid_from_answer(answer_id)
        if user_id > 0:
            user_module.user_reputation(user_id, 10)
    elif vote_direction.lower() == "vote-down":
        user_id = user_module.userid_from_answer(answer_id)
        if user_id > 0:
            user_module.user_reputation(user_id, -2)
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/question/<int:question_id>/vote/<vote_direction>')
def vote_question(question_id, vote_direction):
    vote_module.change_vote('question', question_id, vote_direction)
    if vote_direction.lower() == "vote-up":
        user_id = user_module.userid_from_question(question_id)
        if user_id > 0:
            user_module.user_reputation(user_id, 5)
    elif vote_direction.lower() == "vote-down":
        user_id = user_module.userid_from_question(question_id)
        if user_id > 0:
            user_module.user_reputation(user_id, -2)
    return redirect(url_for('display_question', question_id=question_id))


###############################################################################################################
#                                               SEARCH                                                        #
###############################################################################################################
@app.route('/search')
def search_results():
    search_phrase = '%'+str(request.query_string.decode('utf-8'))[2:].lower()+'%'
    search_result = execute_sql_statement("""SELECT * FROM question
                                          WHERE (LOWER(message) LIKE %s
                                          OR LOWER(title) LIKE %s);""", (search_phrase, search_phrase))
    return render_template('list_questions.html', data_set=search_result, fieldnames=constants.FIELDNAMES, dir='asc')


###############################################################################################################
#                                               COMMENTS                                                      #
###############################################################################################################
@app.route("/question/<question_id>/new-comment", methods=['GET', 'POST'])
def post_question_comment(question_id):
    if request.method == 'GET':
        question_line = execute_sql_statement("SELECT * FROM question WHERE id = %s;", (question_id,))[0]
        all_users = execute_sql_statement("SELECT username FROM users;")
        return render_template('post_comment_to_question.html',
                               question_id=question_id,
                               question_title=question_line[4],
                               question_msg=question_line[5],
                               usernames=all_users)

    if request.method == 'POST':
        comment_time = datetime.now().replace(microsecond=0)
        comment_message = request.form['comment_message']
        comment_edits = 0
        known_user = request.form['username']
        known_user_id = execute_sql_statement("SELECT id FROM users WHERE username=%s;", (known_user,))[0]
        question_line = execute_sql_statement("""INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count, user_id)
                                                VALUES (%s, NULL, %s, %s, %s, %s);""",
                                              (question_id, comment_message, comment_time, comment_edits, known_user_id))

        return redirect(url_for('display_question', question_id=question_id))


@app.route("/answer/<int:answer_id>/new-comment", methods=['GET', 'POST'])
def post_answer_comment(answer_id):
    answer_line = execute_sql_statement("SELECT * FROM answer WHERE id = %s;", (answer_id,))[0]
    if request.method == 'GET':
        all_users = execute_sql_statement("SELECT username FROM users;")
        return render_template('post_comment_to_answer.html',
                               answer_id=answer_id,
                               answer_message=answer_line[4],
                               usernames=all_users)

    if request.method == 'POST':
        comment_time = datetime.now().replace(microsecond=0)
        comment_message = request.form['comment_message']
        comment_edits = 0
        known_user = request.form['username']
        known_user_id = execute_sql_statement("SELECT id FROM users WHERE username=%s;", (known_user,))[0]
        execute_sql_statement("""INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count, user_id)
                                 VALUES (NULL, %s, %s, %s, %s, %s);""",
                              (answer_id, comment_message, comment_time, comment_edits, known_user_id))

        return redirect(url_for('display_question', question_id=answer_line[3]))


@app.route('/comments/<int:comment_id>/del', methods=["POST"])
def delete_comment(comment_id):
    comment = execute_sql_statement("""SELECT * FROM comment WHERE id = %s;""", (comment_id,))[0]

    if comment[1] is not None:
        question_id = execute_sql_statement("""SELECT question_id FROM comment WHERE id = %s;""", (comment_id,))[0][0]
    else:
        answer_id = execute_sql_statement("""SELECT answer_id FROM comment WHERE id = %s;""", (comment_id,))[0][0]
        question_id = execute_sql_statement("""SELECT question_id FROM answer WHERE id = %s;""", (answer_id,))[0][0]

    execute_sql_statement("DELETE FROM comment WHERE id= %s;", (comment_id,))
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/comments/<int:comment_id>/edit', methods=["POST", "GET"])
def edit_comment(comment_id):
    comment = execute_sql_statement("""SELECT * FROM comment WHERE id=%s;""", (comment_id,))[0]
    comment_message = comment[3]

    if request.method == 'GET':
        if comment[1] is not None:
            question_id = comment[1]
            question_line = execute_sql_statement("SELECT * FROM question WHERE id = %s;", (question_id,))[0]
            return render_template('post_comment_to_question.html',
                                   comment_id=comment_id,
                                   comment_message=comment_message,
                                   question_id=question_id,
                                   question_title=question_line[4],
                                   question_msg=question_line[5])
        else:
            answer_id = execute_sql_statement("""SELECT answer_id FROM comment WHERE id = %s;""", (comment_id,))[0][0]
            data = execute_sql_statement("""SELECT message FROM answer WHERE id = %s;""", (answer_id,))[0]

            return render_template('post_comment_to_answer.html',
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

            return redirect(url_for('display_question', question_id=question_id))

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
#                                               TAGS                                                          #
###############################################################################################################
@app.route('/question/<question_id>/tag/<tag_id>/delete')
def tag_delete(question_id, tag_id):
    execute_sql_statement("DELETE FROM question_tag WHERE question_id = %s and tag_id = %s;", (question_id, tag_id))
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/question/<question_id>/new-tag', methods=['POST', 'GET'])
def new_tag(question_id):
    if request.method == 'GET':
        question_line = execute_sql_statement("SELECT * FROM question WHERE id = %s;", (question_id,))[0]
        existing_tags = execute_sql_statement("SELECT name FROM tag;")
        return render_template('question_tag.html',
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
        return redirect(url_for('display_question', question_id=question_id))


@app.route('/tags')
def list_tags():
    tags = execute_sql_statement("""SELECT tag.name, count(tag_id)
                                    FROM question_tag JOIN tag
                                    ON id=tag_id GROUP BY tag.name;""")
    return render_template('display_tag_page.html',
                           tag_list=tags)


###############################################################################################################
#                                       IMAGE HANDLING                                                        #
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
            del_file = constants.UPLOAD_FOLDER + '/' + local_images[i]
            os.remove(del_file)
    return redirect(url_for('get_list_of_questions'))


###############################################################################################################
#                                              USERS                                                          #
###############################################################################################################
@app.route('/list-users')
def list_users():
    users = user_module.get_user_list()
    return render_template('list_users.html', users=users)


@app.route('/answer/<int:answer_id>/accept')
def accept_answer(answer_id):
    question_id = answer_module.set_to_accepted(answer_id)
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/user/<user_id>')
def display_user_page(user_id):
    user_data = execute_sql_statement("SELECT * FROM users WHERE id =  %s;", (user_id,))[0]
    user_questions = execute_sql_statement("SELECT * FROM question WHERE user_id = %s", (user_id,))
    user_comments = execute_sql_statement("SELECT * FROM comment WHERE user_id = %s", (user_id,))
    user_answers = execute_sql_statement("SELECT * FROM answer WHERE user_id = %s", (user_id,))
    return render_template('display_user_page.html',
                           user_data=user_data,
                           user_questions=user_questions,
                           user_comments=user_comments,
                           user_answers=user_answers)


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
