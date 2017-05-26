from utilities import execute_sql_statement


def vote_up_down(vote_nr, vote_direction):
    if vote_direction == 'vote-up':
        return vote_nr + 1
    elif vote_direction == 'vote-down':
        return vote_nr - 1


def change_vote(table, id_, vote_direction):
    if table == 'answer':
        vote_nr = execute_sql_statement("SELECT vote_number FROM answer WHERE id = %s;", (id_,))[0][0]
        vote_nr = vote_up_down(vote_nr, vote_direction)
        execute_sql_statement("UPDATE answer SET vote_number= %s WHERE id = %s;", (vote_nr, id_))
    elif table == 'question':
        vote_nr = execute_sql_statement("SELECT vote_number FROM question WHERE id = %s;", (id_,))[0][0]
        vote_nr = vote_up_down(vote_nr, vote_direction)
        execute_sql_statement("UPDATE question SET vote_number= %s WHERE id = %s;", (vote_nr, id_))
