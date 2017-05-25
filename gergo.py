@app.route('/list')
def list():
    data_set = execute_sql_statement("SELECT * FROM question order by submission_time DESC;")
    sort_direction = 'asc'
    list_from_query_string = request.query_string.decode('utf-8').split('=')
    try:
        if len(list_from_query_string) == 2:
            column = list_from_query_string[0].encode('utf-8')
            if str(list_from_query_string[1]) == 'asc':
                sort_direction = 'dsc'
                data_set = execute_sql_statement("SELECT * FROM question ORDER BY %s DESC;", (column,))

            elif str(list_from_query_string[1]) == 'desc':
                sort_direction = 'asc'
                data_set = execute_sql_statement("SELECT * FROM question ORDER BY %s ASC;", (column,))

    except IndexError:
        pass
    return render_template('list.html', data_set=data_set, fieldnames=constants.FIELDNAMES, dir=sort_direction)
