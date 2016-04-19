from flask import current_app, json, request, Blueprint

from frank.model import db


calendar = Blueprint('calendar', __name__)


@calendar.route('/invites/incoming')
def invites_incoming():
    import pprint
    pprint.pprint(request.form)
    return json.jsonify(status=1)
