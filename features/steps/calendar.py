import datetime

from flask import url_for
from behave import *


def post_email(
    context, from_email, to_emails, subject, body, datetime, duration
):
    data = {
        'envelope[from]': from_email,
        'headers[Subject]': subject,
        'plain': 'When: {} {}-{}. '
                 '(UTC-05:00) Eastern Time (US & Canada)\n'
                 'Where: Elsewhere\n'
                 '\n'
                 '*~*~*~*~*~*~*~*~*~*\n'
                 '\n'
                 '{}\n'
                 '\n'
                 '\n'.format(
                     datetime.strftime('%A, %B %d, %Y'),
                     datetime.strftime('%I:%M %p'),
                     (datetime + duration).strftime('%I:%M %p'),
                     body,
                 ),
        'reply_plain': '',
    }
    for i, to in enumerate(to_emails):
        key = 'envelope[recipients][{}]'.format(i)
        data[key] = to

    with context.app.app_context():
        context.client.post('/calendar/invites/incoming', data=data)


@when('I send him a meeting invitation')
def step_impl(context):
    post_email(
        context,
        'err8n@eservices.virginia.edu',
        ['rag9b@virginia.edu', 'lam2c@virginia.edu', 'nemo@cloudmailin.net'],
        'This is the subject',
        '',
        datetime.datetime(2016, 4, 19, 16, 0),
        datetime.timedelta(minutes=30),
    )


@when('I send him a meeting invitation with {userid} in the {location}')
def step_impl(context, userid, location):
    if location == 'title':
        subject = 'The Subject {}'.format(userid)
        body = (
            'When: Tuesday, April 19, 2016 4:00 PM-4:30 PM. '
            '(UTC-05:00) Eastern Time (US & Canada)\n'
            'Where: Elsewhere\n'
            '\n'
            '*~*~*~*~*~*~*~*~*~*\n'
            '\n'
            'Consultation with {}\n'
            '\n'
            '\n'
        ).format(userid)
    else:
        subject = 'This is the subject'
        body = (
            'When: Tuesday, April 19, 2016 4:00 PM-4:30 PM. '
            '(UTC-05:00) Eastern Time (US & Canada)\n'
            'Where: Elsewhere\n'
            '\n'
            '*~*~*~*~*~*~*~*~*~*\n'
            '\n'
            '\n'
        )

    post_email(
        context,
        'err8n@eservices.virginia.edu',
        ['rag9b@virginia.edu', 'lam2c@virginia.edu', 'nemo@cloudmailin.net'],
        subject,
        body,
        datetime.datetime(2016, 4, 19, 16, 0),
        datetime.timedelta(minutes=30),
    )


@when('I send him a meeting invitation for {delta_time}')
def step_impl(context, delta_time):
    now = datetime.datetime.now()
    if delta_time == 'yesterday':
        now = now - datetime.timedelta(1)
    elif delta_time == 'tomorrow':
        now = now + datetime.timedelta(1)
    now = now.replace(hour=16, minute=0)

    post_email(
        context,
        'err8n@eservices.virginia.edu',
        ['rag9b@virginia.edu', 'lam2c@virginia.edu', 'nemo@cloudmailin.net'],
        'This is the subject',
        '',
        now,
        datetime.timedelta(minutes=30),
    )


@then('he should recognize that I have a consultation')
def step_impl(context):
    # return
    raise NotImplementedError


@then('he should scrape the duration of the consultation')
def step_impl(context):
    # return
    raise NotImplementedError


@then('he should scrape the date of the consultation')
def step_impl(context):
    # return
    raise NotImplementedError


@then('he should scrape the other attendees of the consultation')
def step_impl(context):
    # return
    raise NotImplementedError


@then('he should scrape {userid} from the {location} of the invitation')
def step_impl(context, userid, location):
    # return
    raise NotImplementedError


@then('he should recognize that the invitation is {status}')
def step_impl(context, status):
    # return
    raise NotImplementedError


@then('he should create a meeting for the invitation')
def step_impl(context):
    # return
    raise NotImplementedError


@then('he should not create a meeting for the invitation')
def step_impl(context):
    # return
    raise NotImplementedError
