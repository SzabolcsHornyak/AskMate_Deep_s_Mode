from askmate_package.db_handling import execute_sql_statement
from askmate_package import user_module


def set_to_accepted(answer_id):
    '''
    Sets an answer to Accepted, all others to the same question to not accepted,
    and updates the reputation of the user who posted the accepted answer.
    '''
    answer = execute_sql_statement('''SELECT * FROM answer WHERE id=%s;''', (answer_id,))[0]
    qid = answer[3]
    user_id = answer[7]

    execute_sql_statement('''UPDATE answer SET accepted=FALSE WHERE question_id=%s AND accepted=TRUE;''', (qid,))
    execute_sql_statement('''UPDATE answer SET accepted=TRUE WHERE id=%s;''', (answer_id,))
    user_module.user_reputation(user_id, 15)

    return qid
