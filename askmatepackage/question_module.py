from utilities import execute_sql_statement


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
