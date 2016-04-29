from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
migrate = Migrate()


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


attendees = db.Table(
    'attendees',
    db.Column('invitation_id', db.Integer, db.ForeignKey('invitation.id')),
    db.Column('profile.id', db.Integer, db.ForeignKey('profile.id')),
)


class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(256))
    body = db.Column(db.Text())

    meeting_date = db.Column(db.DateTime(), nullable=False)
    duration = db.Column(db.Integer())

    # This is one of
    # -1 = canceled
    #  0 = pending
    #  1 = done (and should have a link to a Consult)
    status = db.Column(db.Integer(), nullable=False, default=0)

    owner_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
    owner = db.relationship('Profile', back_populates='invitations_owned')

    attendees = db.relationship('Profile', secondary=attendees,
                                back_populates='invitations')


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(32), unique=True, nullable=False)

    invitations_owned = db.relationship('Invitation', back_populates='owner')
    invitations = db.relationship('Invitation', secondary=attendees,
                                  back_populates='attendees')


class ErrorReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String)
    stacktrace = db.Column(db.String)
    route = db.Column(db.String(75))
