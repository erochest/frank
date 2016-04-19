

"""The main entry point for the webapp."""


from flask import Flask
from flask.ext.heroku import Heroku
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# from frank import db


app = Flask(__name__)
heroku = Heroku(app)
db = SQLAlchemy(app)


@app.before_request
def before_request():
    db.create_all()


@app.route('/')
def main():
    """The root page."""
    n = list(db.session.execute(text('SELECT RANDOM();'), {}))[0][0]
    return "It's alive!\n" + str(n) + "\n"


if __name__ == '__main__':
    main()
