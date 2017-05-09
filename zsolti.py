from flask import Flask


app = Flask(__name__, static_url_path='/static')


@app.route('/list')
def list():
    return 'asd'


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()