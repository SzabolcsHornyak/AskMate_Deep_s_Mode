from askmate_package.db_handling import execute_sql_statement
from os import path, remove
from werkzeug.utils import secure_filename
from datetime import datetime


def get_question_tags_for_display(question_id):
    """
    This function returns the tag_ids(list) and question tags(list), found by the question_id as a 2d list.
    """
    tag_id_list = execute_sql_statement("SELECT tag_id FROM question_tag WHERE question_id = %s;", (question_id,))
    question_tags = []
    tag_ids = []
    for tags in tag_id_list:
        question_tags.append(execute_sql_statement("SELECT name FROM tag WHERE id = %s;", (tags[0],))[0][0])
        tag_ids.append(execute_sql_statement("SELECT id FROM tag WHERE id = %s;", (tags[0],))[0][0])
    return zip(tag_ids, question_tags)


def get_question_answers_for_display(question_id):
    """
    This function returns the list of answers with matching question_id and corresponding comments.
    """
    questions_answer_rows = execute_sql_statement("""SELECT * FROM answer
                                                     WHERE question_id = %s
                                                     ORDER BY accepted desc, vote_number DESC, id;""",
                                                  (question_id,))
    answer_ids = [row[0] for row in questions_answer_rows]
    answer_comments = []
    for answer_id in answer_ids:
        answer_comments.append(execute_sql_statement("SELECT * FROM comment WHERE answer_id = %s;", (answer_id,)))
    return (questions_answer_rows, answer_comments)


def new_question_image_handling(image_file, app, new_question=False):
    """
    This function handles existing and non-existing images.
    """
    if image_file.filename != '':
        if image_file:
            image_file.save(path.join(app.config['UPLOAD_FOLDER'], secure_filename(image_file.filename)))
            return 'images/'+secure_filename(image_file.filename)
    if new_question:
        return ''


def delete_image(question_id):
    """
    Using the question_id this function deletes all the corresponding images.
    """
    question_image = execute_sql_statement("SELECT image from question WHERE id=%s;", (question_id,))[0][0]
    if question_image and path.isfile('static/' + question_image):
        remove('static/' + question_image)


def insert_new_question_into_database(question_user_input, question_image):
    """
    This function gets a form object and a path to an image file as parameters
    and puts theem in the database.
    """
    known_user = question_user_input['username']
    known_user_id = execute_sql_statement("SELECT id FROM users WHERE username=%s;", (known_user,))[0]
    execute_sql_statement("""
                          INSERT INTO question (submission_time, view_number,
                          vote_number, title, message, image, user_id)
                          VALUES (%s, %s, %s, %s, %s, %s, %s);
                          """, (datetime.now().replace(microsecond=0),
                                0, 0,  # view_number and vote_number
                                str(question_user_input['question_title']),
                                str(question_user_input['question_text']),
                                question_image,
                                known_user_id))


def update_question(question_user_input, question_id):
    """
    Gets a form object and a question_id as parameters and updates the corresponding question
    with data from the former one.
    """
    execute_sql_statement("""
                          UPDATE question
                          SET
                          title=%s,message=%s
                          WHERE id=%s;
                          """,
                          (str(question_user_input['question_title']),
                           str(question_user_input['question_text']),
                           question_id))
