from askmate_package.db_handling import execute_sql_statement


def set_to_accepted(answer_id):
    qid = execute_sql_statement('''SELECT question_id FROM answer WHERE id=%s;''', (answer_id,))[0][0]
    execute_sql_statement('''UPDATE answer SET accepted=FALSE WHERE question_id=%s AND accepted=TRUE;''', (qid,))
    execute_sql_statement('''UPDATE answer SET accepted=TRUE WHERE id=%s;''', (answer_id,))
    return qid
