import datetime
import email.utils
import re
import sys

from flask import (
    abort, current_app, json, render_template, request, Blueprint
)

from frank.model import db, insert_or_create, Invitation, Profile


ATTENDEE_REGEXEN = [
    re.compile(r'(?P<userid> [a-z]+ (?: \d [a-z]+ ) ) @', re.VERBOSE),
]


calendar = Blueprint('calendar', __name__, template_folder='templates')


def profile(userid):
    """Create and return a profile that's been added to the session."""
    p = Profile(userid=userid)
    db.session.add(p)
    return p


def parse_date_time(line):
    """This parses a meeting time and returns the start time and duration."""
    # Wednesday, April 20, 2016 9:00 PM-10:00 PM (UTC-05:00)
    # 0: Wednesday,
    # 1: April
    # 2: 20,
    # 3: 2016
    # 4: 9:00
    # 5: PM-10:00
    # 6: PM
    # 7: (UTC-05:00)
    parts = line.split()
    parts[7] = parts[7].replace(':', '')
    parts2 = parts[5].split('-')

    d_str = ' '.join(parts[:5] + [parts2[0], parts[7]])
    d = datetime.datetime.strptime(d_str, '%A, %B %d, %Y %I:%M %p (%Z%z)')

    dend = datetime.datetime.strptime(
        ' '.join(parts[:4] + [parts2[1]] + parts[6:8]),
        '%A, %B %d, %Y %I:%M %p. (%Z%z)',
    )

    return (d, dend - d)


def add_profile(profile_index, userid):
    """This creates a user and adds it to the database and the index."""
    return insert_or_create(profile_index, userid, lambda: profile(userid))


def read_recipients(form, index):
    """This reads all the envelope[recipients][N] entries from the form."""
    attendees = []
    to_emails = email.utils.getaddresses(form.get('headers[To]', '').split(','))
    for _, address in to_emails:
        userid = address.split('@')[0]
        attendees.append(add_profile(index, userid))

    return attendees


def parse_when(body):
    """This parses the 'When:' line in the body."""
    for line in body.splitlines():
        if line.lower().startswith('when: '):
            meeting_date, duration = parse_date_time(line[6:])
            break
    else:
        abort(400)

    return (meeting_date, duration)


def read_attendee(attendee_set, index, text):
    """This scans the text for a UVa computing ID."""
    attendees = []

    for regex in ATTENDEE_REGEXEN:
        for match in regex.finditer(text):
            userid = match.group('userid')
            if userid not in attendee_set:
                attendee_set.add(userid)
                profile = add_profile(index, userid)
                attendees.append(profile)

    return attendees


@calendar.route('/invites/incoming', methods=['POST'])
def invites_incoming():
    """\
    Gets an invitation from a POST request, adds it to the db, and returns its
    ID.
    """
    incoming = request.form
    import pprint
    pprint.pprint(incoming)
    with current_app.app_context():
        profiles = {p.userid: p for p in db.session.query(Profile)}
        key = incoming['envelope[from]'].split('@')[0]
        owner = insert_or_create(profiles, key, lambda: profile(key))
        attendees = read_recipients(incoming, profiles)
        attendee_set = set(attendee.userid for attendee in attendees)
        subject = incoming['headers[Subject]']
        body = incoming['plain']
        meeting_date, duration = parse_when(body)
        attendees += read_attendee(attendee_set, profiles, subject) \
            + read_attendee(attendee_set, profiles, body)
        if meeting_date < datetime.datetime.now(meeting_date.tzinfo):
            status = 1
        else:
            status = 0

        invitation = Invitation(
            subject=subject,
            body=body,
            status=status,
            meeting_date=meeting_date,
            duration=round(duration.total_seconds() / 60.0),
            owner=owner,
            attendees=attendees,
        )

        db.session.add(invitation)
        db.session.commit()

        return json.jsonify(status=1, id=invitation.id)


@calendar.route('/invites/<invite_id>')
def invite(invite_id):
    """The view page for the invite."""
    invite_id = int(invite_id)
    with current_app.app_context():
        invitation = Invitation.query.get_or_404(invite_id)
        return render_template(
            'calendar/invite_show.html',
            invitation=invitation,
            timedelta=datetime.timedelta,
        )


@calendar.route('/consult/<consult_id>')
def consult(consult_id):
    """The view page for a consult."""
    consult_id = int(consult_id)
    with current_app.app_context():
        consult = Consult.query.get_or_404(consult_id)
        return render_template(
            'calendar/consult_show.html',
            consult=consult,
        )
