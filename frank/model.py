"""Data models for the database and beyond."""


import datetime
import enum

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from frank.utils import date_parses


db = SQLAlchemy()
migrate = Migrate()


@enum.unique
class RecurPeriod(enum.Enum):
    none = 0
    daily = 1
    weekly = 2
    monthly = 3
    annually = 4


class RecurMixin:
    """\
    This is a mixin class to provide methods to coordinate the values of the
    `recur` and `recur_param` properties.
    """

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


def insert_or_create(index, key, fn):
    """\
    This checks for key in index. If it doesn't exist, create the object with
    fn.
    """
    obj = index.get(key)
    if obj is None:
        obj = fn()
        index[key] = obj
    return obj


invitation_attendees = db.Table(
    'attendees',
    db.Column('invitation_id', db.Integer, db.ForeignKey('invitation.id')),
    db.Column('profile_id', db.Integer, db.ForeignKey('profile.id')),
)


class Invitation(db.Model, RecurMixin):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(256))
    body = db.Column(db.Text())

    meeting_date = db.Column(db.DateTime(), nullable=False)
    duration = db.Column(db.Integer())

    # A value from RecurPeriod
    recur = db.Column(db.Enum(RecurPeriod), default=RecurPeriod.none)

    # The semantics of this are the same as of `recur` and `recur_param` in
    # `MeetingTime`, as documented below.
    recur_param = db.Column(db.String(12), default=None, nullable=True)

    # This is one of
    # -1 = canceled
    #  0 = pending
    #  1 = done (and should have a link to a Consult)
    status = db.Column(db.Integer(), nullable=False, default=0)

    owner_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
    owner = db.relationship('Profile', back_populates='invitations_owned')

    attendees = db.relationship('Profile', secondary=invitation_attendees,
                                back_populates='invitations')


consult_attendees = db.Table(
    'consult_attendees',
    db.Column('consult_id', db.Integer, db.ForeignKey('consult.id')),
    db.Column('profile_id', db.Integer, db.ForeignKey('profile.id')),
)


class Consult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_invitation = db.Column(db.Integer, db.ForeignKey('invitation.id'))

    meeting_date = db.Column(db.DateTime(), nullable=False)
    duration = db.Column(db.Integer)
    attendees = db.relationship('Profile', secondary=consult_attendees,
                                back_populates='consults')

    notes = db.Text()


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(32), unique=True, nullable=False)

    invitations_owned = db.relationship('Invitation', back_populates='owner')
    invitations = db.relationship('Invitation', secondary=invitation_attendees,
                                  back_populates='attendees')
    consults = db.relationship('Consult', secondary=consult_attendees,
                               back_populates='attendees')


class ErrorReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String)
    stacktrace = db.Column(db.String)
    route = db.Column(db.String(75))


class MeetingTime(RecurMixin):
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
