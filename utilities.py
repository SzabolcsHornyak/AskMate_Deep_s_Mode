import base64
import psycopg2


def decode_this(string):
    '''Takes a base64 string and decodes it to human-readable value.'''
    return base64.b64decode(string).decode()


def encode_this(string):
    '''Takes a human-readable string and encodes it to a base64 value.'''
    return base64.b64encode(string.encode('utf-8')).decode('utf-8')


def just_read(file_path):
    '''Takes a csv file and makes a raw 2d table from it.'''
    with open(file_path, 'r') as csvfile:
        return [line.split(',') for line in csvfile]


def execute_sql_statement(sql_statement, values=tuple()):
    try:
        # setup connection string
        with open('static/conn_str.txt', 'r') as file:
            conn_str = file.readline()
        dbname = conn_str.split(',')[0]
        user = conn_str.split(',')[1]
        host = conn_str.split(',')[2]
        password = conn_str.split(',')[3]

        connect_str = "dbname="+dbname+" user="+user+" host="+host+" password="+password
        # use our connection values to establish a connection
        conn = psycopg2.connect(connect_str)
        # set autocommit option, to do every query when we call it
        conn.autocommit = True
    except Exception as e:
        print("Uh oh, can't connect. Invalid dbname, user or password?")
        print(e)
    cursor = conn.cursor()
    cursor.execute(sql_statement, values)
    if sql_statement[:6] == 'SELECT':
        rows = list(cursor.fetchall())
        return rows
