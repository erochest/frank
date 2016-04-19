

"""The main entry point for the webapp."""


from flask import Flask
from flask.ext.heroku import Heroku
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# from frank import db


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

heroku = Heroku(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.route('/')
def homepage():
    """The root page."""
    n = list(db.session.execute(text('SELECT RANDOM();'), {}))[0][0]
    return "It's alive!\n" + str(n) + "\n"
