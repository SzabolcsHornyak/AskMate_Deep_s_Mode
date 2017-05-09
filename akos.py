from flask import Flask, render_template, request
import base64
import time
app = Flask(__name__, static_url_path='/static')


@app.route("/question/<question_id>/new-answer", methods=['GET', 'POST'])
def post_answer(question_id):

    if request.method == 'GET':
        #    with open('./static/answer.csv', 'r') as file:
        #        all_answers = [line.split(',') for line in file]

        #    answers = [line for line in all_answers if line[3] == question_id]
        #
        #    ^  should the answers be displayed with the question as well? ^
        # if so, shouldn't this be done on the question details page?

        with open('./static/data/question.csv', 'r') as file:
            question = [line.split(',') for line in file if line.split(',')[0] == question_id][0]
            question_title = base64.b64decode(question[4]).decode('utf-8')
            question_msg = base64.b64decode(question[5]).decode('utf-8')

        return render_template('a_answer.html', question_id=question_id, question_title=question_title, question_msg=question_msg)

    if request.method == 'POST':
        with open('./static/data/answer.csv', 'a+') as file:
            _id = len(file.readlines())
            submission_time = round(time.time())
            vote_number = 0
            qid = question_id
            message = base64.b64encode(request.form['answer_message'].encode("utf-8")).decode("utf-8")
            image = ''  # - to-do

            s = ','.join(list(map(str, [_id, submission_time, vote_number, qid, message, image])))
            file.write(s + "\n")

        return "No errors i guess."  # - the fuck should it return? :) details page of the question mb?


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
