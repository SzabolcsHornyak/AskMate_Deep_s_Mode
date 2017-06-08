from askmate_package.db_handling import execute_sql_statement


def vote_up_down(vote_number, vote_direction):
    """
    Handles voting up and down.
    """
    if vote_direction == 'vote-up':
        return vote_number + 1
    elif vote_direction == 'vote-down':
        return vote_number - 1


def change_vote(table, id_, vote_direction):
    """
    Fetching vote data from database.
    """
    if table == 'answer':
        vote_number = execute_sql_statement("SELECT vote_number FROM answer WHERE id = %s;", (id_,))[0][0]
        vote_number = vote_up_down(vote_number, vote_direction)
        execute_sql_statement("UPDATE answer SET vote_number= %s WHERE id = %s;", (vote_number, id_))
    elif table == 'question':
        vote_number = execute_sql_statement("SELECT vote_number FROM question WHERE id = %s;", (id_,))[0][0]
        vote_number = vote_up_down(vote_number, vote_direction)
        execute_sql_statement("UPDATE question SET vote_number= %s WHERE id = %s;", (vote_number, id_))
