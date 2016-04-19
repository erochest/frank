"""Caring for the environment."""


import os

from flask import current_app

from frank import wsgi


def before_all(context):
    """Bootstrap the app before everything."""
    context.db_file = os.path.join(os.getcwd(), 'tmp', 'test.db')
    context.app_info = wsgi.create_app()

    app = context.app_info['app']
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + context.db_file

    context.app = context.app_info['app']
    context.db = context.app_info['db']


def after_all(context):
    """Tear down after everything."""
    os.unlink(context.db_file)
    del context.app.config['SQLALCHEMY_DATABASE_URI']


def before_feature(context, feature):
    with context.app.app_context():
        context.db.create_all()
    context.client = context.app.test_client()


def after_feature(context, feature):
    with context.app.app_context():
        context.app_info['db'].drop_all()
