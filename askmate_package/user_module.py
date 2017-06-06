from askmate_package.db_handling import execute_sql_statement


def get_user_list():
    '''
    Gets a list of all users in the users table, returns them as a list of tuples
    where one tuple contains the dataset of one user.
    '''
    users = execute_sql_statement('''SELECT username, registration_time, reputation FROM users;''')
    return users
