from flask import Flask, render_template
import base64
import time
app = Flask(__name__, static_url_path='/static')


def decode_this(string):
    return base64.b64decode(string).decode('utf-8')


@app.route('/')
@app.route('/list')
def list():
    fieldnames = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
    with open('./static/data/question.csv', 'r') as qcsvfile:
        data_set = [line.split(',') for line in qcsvfile]
        data_set = sorted(data_set, key=lambda x: x[1], reverse=True)
        for line in data_set:
            line[1] = time.ctime(int(line[1]))
            line[4] = decode_this(line[4])
            line[5] = decode_this(line[5])
            line[6] = decode_this(line[6])
        return render_template('zslist.html', data_set=data_set, fieldnames=fieldnames)


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()