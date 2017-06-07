from askmate_package.db_handling import execute_sql_statement


def get_user_list():
    '''
    Gets a list of all users in the users table, returns them as a list of tuples
    where one tuple contains the dataset of one user.
    '''
    users = execute_sql_statement('''SELECT * FROM users;''')
    return users


def user_reputation(user_id=0, change_rep=0):
    """This function change the user reputation"""
    if user_id != 0 and change_rep != 0:
        if str(change_rep)[0] == '-':
            psql_query = """
            UPDATE users
            SET
                reputation = reputation - """ + str(change_rep)[1:] + """
            WHERE
            id = """ + str(user_id) + """
            """
        else:
            psql_query = """
            UPDATE users
            SET
                reputation = reputation + """ + str(change_rep) + """
            WHERE
            id = """ + str(user_id) + """
            """
        execute_sql_statement(psql_query)


def userid_from_answer(answer_id=0):
    """Get back the user id based on answer_id"""
    user_id = 0
    if answer_id > 0:
        psql_query = "SELECT user_id FROM answer WHERE id = " + str(answer_id)
        user_id = execute_sql_statement(psql_query)[0][0]
        if user_id > 0:
            return user_id
        else:
            return 0
    return 0


def userid_from_question(answer_id=0):
    """Get back the user id based on answer_id"""
    user_id = 0
    if answer_id > 0:
        psql_query = "SELECT user_id FROM answer WHERE id = " + str(answer_id)
        user_id = execute_sql_statement(psql_query)[0][0]
        if user_id > 0:
            return user_id
        else:
            return 0
    return 0