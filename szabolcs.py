from flask import Flask, render_template, request
import base64
import time
app = Flask(__name__, static_url_path='/static')

def load_question():
    fieldnames = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
    with open('./static/data/question.csv', 'r') as qcsvfile:
        data_set = [line.split(',') for line in qcsvfile]
        data_set = sorted(data_set, key=lambda x: x[1], reverse=True)
        for line in data_set:
            line[1] = time.ctime(int(line[1]))
            line[4] = decode_this(line[4])
            line[5] = decode_this(line[5])
            line[6] = decode_this(line[6])
    return data_set


def decode_this(string):
    return base64.b64decode(string).decode('utf-8')


@app.route('/newquestion', methods=['POST', 'GET'])
def list():
    if request.method == 'POST':
        data_set = load_question()
        last_id = data_set[len(data_set)-1][0]
        datas = []
        datas.append(int(last_id)+1)
        datas.append(request.form['q_title'])
        datas.append(request.form['q_text'])
        return str(datas)
        #return redirect(url_for('list_page')) #LISTÁZÁS
    data_tmp = []
    return render_template('new_quest.html', question=data_tmp, typ='A')


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()