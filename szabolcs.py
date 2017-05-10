from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
import base64
import csv
import time
import os

app = Flask(__name__, static_url_path='/static')
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def decode_this(string):
    return base64.b64decode(string).decode('utf-8')


def encode_this(string):
    return base64.b64encode(string.encode('utf-8')).decode('utf-8')


def load_question():
    with open('./static/data/question.csv', 'r') as qcsvfile:
        data_set = [line.split(',') for line in qcsvfile]
        for i in range(len(data_set)):
            for j in range(len(data_set[i])):
                if j > 3:
                    data_set[i][j] = decode_this(data_set[i][j])
    return data_set


def write_questions(datas):
    filename = './static/data/question.csv'
    with open(filename, 'w') as f:
        for i in range(len(datas)):
            temp_string = ''
            for j in range(len(datas[i])):
                if j > 3:
                    temp_string += str(encode_this(datas[i][j]))+','
                else:
                    temp_string += str(datas[i][j])+','
            temp_string = temp_string[:-1]
            f.write(temp_string+'\n')


@app.route('/newquestion', methods=['POST', 'GET'])
def new_question():
    if request.method == 'POST':
        data_set = load_question()
        last_id = data_set[len(data_set)-1][0]
        datas = []
        datas.append(int(last_id)+1)
        datas.append(round(time.time()))
        datas.append('0')
        datas.append('0')
        datas.append(request.form['q_title'])
        datas.append(request.form['q_text'])
        data_set.append(datas)
        write_questions(data_set)
    return render_template('new_quest.html', data=[])


@app.route('/question/<qid>', methods=['POST', 'GET'])
def qestion_view(qid=None):
    datas = load_question()
    data_tmp = []
    if request.method == 'POST':
        secure_path = ''
        img_file = request.form['q_img']
        filex = request.files['file']
        if filex.filename != '':
            if filex:
                filex.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filex.filename)))
                secure_path = 'images/'+secure_filename(filex.filename)
        if secure_path != '':
            if img_file != secure_path:
                os.remove('static/' + img_file)
                img_file = secure_path
        for i in range(len(datas)):
            if datas[i][0] == qid:
                datas[i][4] = request.form['q_title']
                datas[i][5] = request.form['q_text']
                datas[i][6] = img_file
        write_questions(datas)
        data_tmp = datas[int(qid)]
    else:
        for i in range(len(datas)):
            if datas[i][0] == qid:
                for j in range(len(datas[i])):
                    data_tmp.append(datas[i][j])
    return render_template('new_quest.html', data=data_tmp, typ='V', qid=qid)


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()