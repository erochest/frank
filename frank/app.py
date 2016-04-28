

"""The main entry point for the webapp."""


from flask import Flask
from flask.ext.heroku import Heroku
from flask_humanize import Humanize


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    heroku = Heroku(app)
    humanize = Humanize(app)

    from frank.model import db, migrate
    db.init_app(app)
    migrate.init_app(app, db)

    from .views.home import homepage
    from .calendar.views import calendar
    app.register_blueprint(homepage)
    app.register_blueprint(calendar, url_prefix='/calendar')

    return {
        'app': app,
        'heroku': heroku,
        'humanize': humanize,
        'db': db,
        'migrate': migrate,
    }
