from flask import current_app, json, request, Blueprint

from frank.model import db


calendar = Blueprint('calendar', __name__)


@calendar.route('/invites/incoming', methods=['POST'])
def invites_incoming():
    return json.jsonify(status=1)
