"""Caring for the environment."""


import os

from frank import wsgi


def before_all(context):
    """Bootstrap the app before everything."""
    context.db_file = os.path.join(os.getcwd(), 'tmp', 'test.db')
    wsgi.app.config['TESTING'] = True
    wsgi.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + context.db_file
    context.db = wsgi.db


def after_all(context):
    """Tear down after everything."""
    os.unlink(context.db_file)
    del wsgi.app.config['SQLALCHEMY_DATABASE_URI']


def before_feature(context, feature):
    wsgi.db.create_all()
    context.client = wsgi.app.test_client()


def after_feature(context, feature):
    wsgi.db.drop_all()
