from flask import current_app, Blueprint
from sqlalchemy import text

from frank.model import db


homepage = Blueprint('homepage', __name__)


@homepage.route('/')
def index():
    with current_app.app_context():
        n = list(db.session.execute(text('SELECT RANDOM();'), {}))[0][0]
    return "It's alive!\n" + str(n) + "\n"
