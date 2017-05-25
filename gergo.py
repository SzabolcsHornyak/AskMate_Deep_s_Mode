@app.route('/list')
def list():
    data_set = execute_sql_statement("SELECT * FROM question ORDER BY submission_time DESC;")
    sort_direction = 'asc'
    dict_from_query_string = request.args
    column = dict_from_query_string.keys()

    try:
        if request.args.values() == 'asc':
            sort_direction = 'dsc'
            execute_sql_statement('SELECT * FROM question ORDER BY %s DESC;', (column,))
        elif request.args.values() == 'dsc':
            sort_direction = 'asc'
            execute_sql_statement('SELECT * FROM question ORDER BY %s ASC;', (column,))
    except IndexError:
        pass
    return render_template('list.html', data_set=data_set, fieldnames=constants.FIELDNAMES, dir=sort_direction)
