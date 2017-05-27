from utilities import execute_sql_statement
from os import path, remove
from werkzeug.utils import secure_filename
from datetime import datetime


def get_question_tags_for_display(question_id):
    tag_id_list = execute_sql_statement("SELECT tag_id FROM question_tag WHERE question_id = %s;", (question_id,))
    question_tags = []
    tag_ids = []
    for tags in tag_id_list:
        question_tags.append(execute_sql_statement("SELECT name FROM tag WHERE id = %s;", (tags[0],))[0][0])
        tag_ids.append(execute_sql_statement("SELECT id FROM tag WHERE id = %s;", (tags[0],))[0][0])
    return zip(tag_ids, question_tags)


def get_question_answers_for_display(question_id):
    questions_answer_rows = execute_sql_statement("SELECT * FROM answer WHERE question_id = %s;", (question_id,))
    answer_ids = [row[0] for row in questions_answer_rows]
    answer_comments = []
    for answer_id in answer_ids:
        answer_comments.append(execute_sql_statement("SELECT * FROM comment WHERE answer_id = %s", (answer_id,)))
    return (questions_answer_rows, answer_comments)


def new_question_image_handling(filex, app, new_question=False):
        if filex.filename != '':
            if filex:
                filex.save(path.join(app.config['UPLOAD_FOLDER'], secure_filename(filex.filename)))
                return 'images/'+secure_filename(filex.filename)
        if new_question:
            return ''


def delete_image(question_id):
    q_img = execute_sql_statement("SELECT image from question WHERE id=%s;", (question_id,))[0][0]
    if q_img and path.isfile('static/' + q_img):
        remove('static/' + q_img)


def insert_new_question_into_database(q_user_input, q_img):
    execute_sql_statement("""
                       INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
                       VALUES (%s, %s, %s, %s, %s, %s);
                       """, (datetime.now(),
                             0, 0,  # view_number and vote_number
                             str(q_user_input['question_title']),
                             str(q_user_input['question_text']),
                             q_img))


def update_question(q_user_input, question_id):
    execute_sql_statement("""
                          UPDATE question
                          SET
                          title=%s,message=%s
                          WHERE id=%s;
                          """,
                          (str(q_user_input['question_title']), str(q_user_input['question_text']), question_id))
