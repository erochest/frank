from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
migrate = Migrate()


attendees = db.Table(
    'attendees',
    db.Column('invitation_id', db.Integer, db.ForeignKey('invitation.id')),
    db.Column('profile.id', db.Integer, db.ForeignKey('profile.id')),
)


class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(256))
    body = db.Column(db.String())

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
