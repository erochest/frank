

"""The main entry point for the webapp."""


from flask import Flask
from flask.ext.heroku import Heroku


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from frank.model import db, migrate
    db.init_app(app)

    heroku = Heroku()
    heroku.init_app(app)

    migrate.init_app(app, db)

    from frank.views.home import homepage
    app.register_blueprint(homepage)

    return {
        'app': app,
        'heroku': heroku,
        'db': db,
        'migrate': migrate,
    }
