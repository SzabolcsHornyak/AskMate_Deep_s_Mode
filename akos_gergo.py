@app.route('/question/<int:question_id>')
def question(question_id):
        question_line = execute_sql_statement("SELECT * FROM question WHERE id =  %s;", (question_id,))[0]
        answers = execute_sql_statement("SELECT * FROM answer WHERE question_id = %s;", (question_id,))
        comments = execute_sql_statement("SELECT * FROM comment WHERE question_id = %s;", (question_id,))
        return render_template('display.html',
                               line=question_line,
                               fieldnames=constants.FIELDNAMES,
                               answers=answers,
                               comments=comments, 
                               question_id=question_id)


@app.route("/question/<question_id>/new-comment", methods=['GET', 'POST'])
def post_comment(question_id):
    if request.method == 'GET':
        question_line = execute_sql_statement("SELECT * FROM question WHERE id = %s;", (question_id,))[0]
        return render_template('new-comment.html',
                               question_id=question_id,
                               question_title=question_line[4],
                               question_msg=question_line[5])

    if request.method == 'POST':
        comment_time = datetime.now()
        comment_message = request.form['comment_message']
        comment_edits = 0
        question_line = execute_sql_statement("""INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count)
                                                VALUES (%s, NULL, %s, %s, %s);""",
                                              (question_id, comment_message, comment_time, comment_edits))

        return redirect(url_for('question', question_id=question_id))


@app.route('/question/<int:question_id>/<int:comment_id>/del', methods=["POST"])
def delete_comment(question_id, comment_id):
    execute_sql_statement("DELETE FROM comment WHERE id= %s;", (comment_id,))
    return redirect(url_for('question', question_id=question_id))
