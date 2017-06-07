import psycopg2
# from tabulate import tabulate  source: https://pypi.python.org/pypi/tabulate probably won't need it, kepping it though


def execute_sql_statement(sql_statement, values=tuple()):
    # setup connection string, not the most secure way
    with open('static/conn_str.txt', 'r') as file:
        conn_str = file.readline()
    dbname = conn_str.split(',')[0]
    user = conn_str.split(',')[1]
    host = conn_str.split(',')[2]
    password = conn_str.split(',')[3]
    connect_str = "dbname="+dbname+" user="+user+" host="+host+" password="+password
    # we create this variable by assigning a None value to it,
    # so when an Exception is catched, the function will not try to close a non-existing variable
    conn = None
    try:
        # use our connection values assigned to the connection string to establish a connection
        # Hey dawg, I heard you like connection, so I put your connection values into your connection string to
        # use them to establish a connection
        conn = psycopg2.connect(connect_str)
    except psycopg2.DatabaseError as e:  # TODO don't use this, remember: "raise PythonicError("Errors should never go silently.")
        print(e)
        return [[e]]
    else:
        conn.autocommit = True
        cursor = conn.cursor()
        try:
            cursor.execute(sql_statement, values)
        except psycopg2.ProgrammingError as e:
            print(e)
            return [[e]]
        else:
            if sql_statement.split(' ')[0].lower() == 'select':
                rows = list(cursor.fetchall())
                return rows
    finally:
        if conn:
            # conn.commit() leaving it here for future testing to see how it works
            conn.close()