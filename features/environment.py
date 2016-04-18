"""Caring for the environment."""


from frank.wsgi import app


def before_feature(context, _feature):
    """Bootstrap the app before each feature."""
    app.config['TESTING'] = True
    context.client = app.test_client()


def after_feature(_context, _feature):
    """Tear down after each feature."""
    pass
