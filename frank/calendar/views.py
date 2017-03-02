"""Views for the calendar blueprint."""


import datetime
import email.utils
import re
import traceback

from flask import (
    abort, current_app, json, render_template, request, url_for, Blueprint
)

from frank.model import (
    db, insert_or_create, ErrorReport, Invitation, Profile, RecurPeriod,
    MeetingTime,
)


ATTENDEE_REGEXEN = [
    re.compile(r'(?P<userid> [a-z]+ (?: \d [a-z]+ )? ) @', re.VERBOSE),
]


calendar = Blueprint('calendar', __name__, template_folder='templates')


def profile(userid):
    """Create and return a profile that's been added to the session."""
    prof = Profile(userid=userid)
    db.session.add(prof)
    return prof


def add_profile(profile_index, userid):
    """This creates a user and adds it to the database and the index."""
    return insert_or_create(profile_index, userid, lambda: profile(userid))


def read_recipients(form, index):
    """This reads all the envelope[recipients][N] entries from the form."""
    attendees = []
    to_emails = email.utils.getaddresses(
        form.get('headers[To]', '').split(','),
        )
    for _, address in to_emails:
        userid = address.split('@')[0]
        attendees.append(add_profile(index, userid))

    return attendees


def parse_when(body):
    """This parses the 'When:' line in the body."""
    for line in body.splitlines():
        if line.lower().startswith('when: '):
            meeting_time = MeetingTime.parse(line[6:])
            break
    else:
        abort(400)

    return meeting_time


def read_attendee(attendee_set, index, text):
    """This scans the text for a UVa computing ID."""
    attendees = []

    for regex in ATTENDEE_REGEXEN:
        for match in regex.finditer(text):
            userid = match.group('userid')
            if userid not in attendee_set:
                attendee_set.add(userid)
                prof = add_profile(index, userid)
                attendees.append(prof)

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
    print('{} files'.format(len(request.files)))
    for file_value in request.files.values():
        print(file_value.filename)
        print(file_value.read())
        print()

    with current_app.app_context():
        try:
            profiles = {p.userid: p for p in db.session.query(Profile)}
            key = incoming['envelope[from]'].split('@')[0]
            owner = insert_or_create(profiles, key, lambda: profile(key))
            attendees = read_recipients(incoming, profiles)
            attendee_set = set(attendee.userid for attendee in attendees)
            subject = incoming['headers[Subject]']
            body = incoming['plain']
            meeting_time = parse_when(body)
            meeting_date = meeting_time.start_time
            duration = meeting_time.duration
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
        except:
            db.session.rollback()
            db.session.add(ErrorReport(
                message='error creating invitation',
                route='calendar /invites/incoming/',
                stacktrace=traceback.format_exc(),
            ))
            db.session.commit()
            raise

        return json.jsonify(
            status=1,
            id=invitation.id,
            url=url_for('.invite', invite_id=invitation.id),
            )


@calendar.route('/invites/<invite_id>')
def invite(invite_id):
    """The view page for the invite."""
    invite_id = int(invite_id)
    with current_app.app_context():
        invitation = Invitation.query.get_or_404(invite_id)
        return render_template(
            'invite_show.html',
            invitation=invitation,
            timedelta=datetime.timedelta,
        )
