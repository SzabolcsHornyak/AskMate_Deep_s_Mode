from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
import psycopg2
import csv
import time
import os


app = Flask(__name__, static_url_path='/static')
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
dbname = 'basic_sql2'
user = 'codecooler'
host = 'localhost'
password = '1234'


UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
FIELDNAMES = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message',
              'image', 'view', 'delete', 'vote']

"""
As a user, I want to see the latest 5 submitted questions on the main page (/). 
I want to see somewhere a link to all of the questions (/list).
"""


def delete_unused_images():
    local_images = next(os.walk(UPLOAD_FOLDER))[2]
    db_images = execute_sql_statement("SELECT image FROM question where image is not null union all SELECT image FROM answer where answer is not null")
    match = []
    for i in range(len(local_images)):
        for j in range(len(db_images)):
            if str(db_images[j][0]).lower() == str('images/'+local_images[i]).lower():
                match.append(db_images[j][0])
    for i in range(len(local_images)):
        if str('images/'+local_images[i]).lower() not in match:
            del_file = UPLOAD_FOLDER + '/' + local_images[i]
            os.remove(del_file)


def execute_sql_statement(sql_statement, values=tuple()):
    try:
        # setup connection string
        connect_str = "dbname="+dbname+" user="+user+" host="+host+" password="+password
        # use our connection values to establish a connection
        conn = psycopg2.connect(connect_str)
        # set autocommit option, to do every query when we call it
        conn.autocommit = True
    except Exception as e:
        print("Uh oh, can't connect. Invalid dbname, user or password?")
        print(e)
    cursor = conn.cursor()
    if values:
        cursor.execute(sql_statement, values)
    else:
        cursor.execute(sql_statement)
    if sql_statement[:6] == 'SELECT':
        rows = list(cursor.fetchall())
        return rows


@app.route('/')
def get_list_5():
    data_set = execute_sql_statement("SELECT * FROM question order by submission_time DESC limit 5;")
    sort_direction = 'asc' 
    return render_template('list.html', data_set=data_set, fieldnames=FIELDNAMES, dir=sort_direction)


@app.route('/list')
def get_list_all():
    data_set = execute_sql_statement("SELECT * FROM question order by submission_time DESC;")
    sort_direction = 'asc' 
    return render_template('list.html', data_set=data_set, fieldnames=FIELDNAMES, dir=sort_direction)


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()