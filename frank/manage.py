
"""The manager app."""


import os
import subprocess
import tempfile

from flask.ext.script import Manager
from flask_migrate import MigrateCommand

from frank.app import create_app


HEROKU_APP = 'frankensystem'

app = create_app()['app']
manager = Manager(app)


@manager.command
def freeze():
    """Freeze the current dependencies to 'requirements.txt'"""
    proc = subprocess.run(['pip', 'freeze'], stdout=subprocess.PIPE)
    with open('requirements.txt', 'wb') as fout:
        fout.write(proc.stdout)


@manager.command
def deploy(branch=None, to='master', keep=False, heroku_app=HEROKU_APP):
    """Close the current or given branch, merge it, and push it.
    Then run migrations on the server.
    """
    if branch is None:
        proc = subprocess.run(['git', 'branch'], stdout=subprocess.PIPE)
        lines = [
            line[2:]
            for line in proc.stdout.decode('utf8').splitlines()
            if line.startswith('* ')
        ]
        branch = lines[0]

    assert branch != to

    subprocess.run(['git', 'checkout', to])
    subprocess.run(['git', 'merge', branch])
    if not keep:
        subprocess.run(['git', 'branch', '--delete', branch])
    subprocess.run(['git', 'push'])

    heroku_migrate(heroku_app)


@manager.command
def heroku_migrate(heroku_app=HEROKU_APP):
    """This migrates the database on the server and restarts the app."""
    subprocess.run([
        'heroku', 'run',
        '--app', heroku_app,
        '--env', 'PYTHON_PATH=/app',
        '--exit-code',
        '--',
        'python', '-m', 'frank.manage', 'db', 'upgrade',
    ])
    subprocess.run(['heroku', 'restart', '--app', heroku_app])


@manager.command
def post_fixture(url=None, data_file=None):
    """This posts the data from `data_file` to `url`."""
    if url is None:
        url = 'http://localhost:5000/calendar/invites/incoming'
    temp_file = None
    if data_file is None:
        handle, temp_file = tempfile.mkstemp()
        data_file = temp_file
        os.write(
            handle,
            'envelope[from]=err8n@eservices.virginia.edu&\n'
            'headers[Subject]=This is a subject&\n'
            'headers[To]=frank-bot@cloudmailin.com,\n'
            'lam2c@virginia.edu,\n'
            'rag9b@virginia.edu&\n'
            'plain=When: Wednesday, April 20, 2016 4:00 PM-4:30 PM '
            '(UTC-05:00) Eastern Time (US %26 Canada)%13'
            'Where: An office%13'
            '%13'
            '*~*~*~*~*~*~*~*~*~*%13'
            '%13'
            '%13'.encode('utf8')
        )
        os.close(handle)

    print(' '.join(
        ['curl', '-v', '-X', 'POST', '--data-ascii', '@' + data_file,
         # '--trace', '-',
         url],
    ))
    subprocess.run(
        ['curl', '-v', '-X', 'POST', '--data-ascii', '@' + data_file,
         # '--trace', '-',
         url],
    )

    if temp_file is not None:
        os.remove(temp_file)


manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
