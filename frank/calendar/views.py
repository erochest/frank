"""Views for the calendar blueprint."""


import datetime
import email.utils
import enum
import re
import traceback

from flask import (
    abort, current_app, json, render_template, request, url_for, Blueprint
)

from frank.model import db, insert_or_create, ErrorReport, Invitation, Profile


ATTENDEE_REGEXEN = [
    re.compile(r'(?P<userid> [a-z]+ (?: \d [a-z]+ )? ) @', re.VERBOSE),
]


calendar = Blueprint('calendar', __name__, template_folder='templates')


def profile(userid):
    """Create and return a profile that's been added to the session."""
    prof = Profile(userid=userid)
    db.session.add(prof)
    return prof


@enum.unique
class RecurPeriod(enum.Enum):
    none = 0
    daily = 1
    weekly = 2
    monthly = 3
    annually = 4


class MeetingTime:
    """\
    This represents all the data for a meeting time and its recurrence bound up
    together.

    """

    def __init__(self):
        """Initialize the meeting time."""
        self.start_time = None
        self.duration = None
        self.recur = RecurPeriod.none

        # OMG this is nasty. After Haskell, data modeling in Python feels like
        # doing brain surgery with a chainsaw. Editorializing aside, the
        # semantics of `recur_param` depends on the value of `recur`, according
        # to this table:
        #
        # recur    # recur_param                            #
        #####################################################
        # none     # None                                   #
        # daily    # None                                   #
        # weekly   # Weekday decimal (0 (Monday) - 6)       #
        # monthly  # Day of month decimal (1-31)            #
        # annually # Tuple of (month decimal, day of month) #
        #####################################################
        #
        # There are methods defined to keep them in sync, but geez.
        self.recur_param = None

    def recur_off(self):
        """Turn recurring off."""
        self.recur = RecurPeriod.none
        self.recur_param = None

    def recur_daily(self):
        """Recur every day."""
        self.recur = RecurPeriod.daily
        self.recur_param = None

    def recur_weekly(self, weekday):
        """\
        Recur every week. `weekday` is the day of the week as a decimal,
        Monday = 0, to 6.
        """
        self.recur = RecurPeriod.weekly
        self.recur_param = weekday

    def recur_monthly(self, month_day):
        """\
        Recur every month. `month_day` is the day of the month as a
        decimal (1-31).
        """
        self.recur = RecurPeriod.monthly
        self.recur_param = month_day

    def recur_annually(self, month, day):
        """\
        Recur every year. `month` is the month as a decimal (1-12); `day` is
        the day of the month (1-31).
        """
        self.recur = RecurPeriod.annually
        self.recur_param = (month, day)

    @classmethod
    def parse(cls, line):
        """Parse a 'When' line from an invitation into a MeetingTime."""
        if line.startswith('Occurs '):
            meeting_time = cls.parse_recurring(line)
        else:
            meeting_time = cls.parse_once(line)
        return meeting_time

    @classmethod
    def parse_once(cls, line):
        """\
        Parse a 'When' line from sole-occuring invitation into a MeetingTime.
        """

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
        parts[6] = parts[6].replace('.', '')
        parts[7] = parts[7].replace(':', '')
        parts2 = parts[5].split('-')

        d_str = ' '.join(parts[:5] + [parts2[0], parts[7]])
        start = datetime.datetime.strptime(
            d_str, '%A, %B %d, %Y %I:%M %p (%Z%z)',
            )

        dend = datetime.datetime.strptime(
            ' '.join(parts[:4] + [parts2[1]] + parts[6:8]),
            '%A, %B %d, %Y %I:%M %p (%Z%z)',
        )

        meeting_time = MeetingTime()
        meeting_time.start_time = start
        meeting_time.duration = dend - start
        meeting_time.recur_off()
        return meeting_time

    @classmethod
    def parse_recurring(cls, line):
        """\
        Parse a 'When' line from a recurring invitation into a MeetingTime.
        """

        meeting_time = MeetingTime()
        now = datetime.datetime.now()
        words = line.split()
        prefix = ' '.join(words[:3])

        # daily
        if line.startswith('Occurs every day from '):
            start_str = '%s %s %s' % (words[10], words[4], words[5])
            start = datetime.datetime.strptime(
                start_str, '%m/%d/%Y. %I:%M %p',
                )
            end_str = '%s %s %s' % (words[10], words[7], words[8])
            end = datetime.datetime.strptime(
                end_str, '%m/%d/%Y. %I:%M %p',
                )
            meeting_time.recur_daily()

        # weekly
        elif date_parses(prefix, 'Occurs every %A'):
            start_str = '%s %s %s' % (words[10], words[4], words[5])
            start = datetime.datetime.strptime(start_str, '%m/%d/%Y. %I:%M %p')
            end_str = '%s %s %s' % (words[10], words[7], words[8])
            end = datetime.datetime.strptime(end_str, '%m/%d/%Y. %I:%M %p')

            weekday_str = words[2]
            step = start
            day = datetime.timedelta(days=1)
            while True:
                if step.strftime('%A') == weekday_str:
                    weekday = step.weekday()
                    break
                step = step + day
            else:
                raise Exception('Invalid weekday: "{}"'.format(weekday_str))

            meeting_time.recur_weekly(weekday)

        # monthly
        elif line.startswith('Occurs every month on day '):
            day = int(words[5])
            start_str = '%s %s %s' % (words[16], words[10], words[11])
            start = datetime.datetime.strptime(start_str, '%m/%d/%Y. %I:%M %p')
            end_str = '%s %s %s' % (words[16], words[13], words[14])
            end = datetime.datetime.strptime(end_str, '%m/%d/%Y. %I:%M %p')
            meeting_time.recur_monthly(day)

        # annually
        elif date_parses(prefix, 'Occurs every %B'):
            start_str = '%s %s, %s, %s %s' % (
                words[2], words[3], now.year, words[5], words[6],
                )
            start = datetime.datetime.strptime(
                start_str, '%B %d, %Y, %I:%M %p',
                )
            start_date = datetime.datetime.strptime(words[11], '%m/%d/%Y.')
            start = datetime.datetime.combine(start_date.date(), start.time())
            end_str = '%s %s, %s, %s %s' % (
                words[2], words[3], start.year, words[8], words[9],
                )
            end = datetime.datetime.strptime(
                end_str, '%B %d, %Y, %I:%M %p',
                )
            meeting_time.recur_annually(start.month, start.day)

        else:
            raise Exception('Invalid "when" line: "{}"'.format(line))

        meeting_time.start_time = start
        meeting_time.duration = end - start
        return meeting_time


def date_parses(date_str, date_format):
    """\
    Returns True or False depending on whether the string matches the format.
    """
    try:
        datetime.datetime.strptime(date_str, date_format)
    except ValueError:
        return False
    else:
        return True


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
