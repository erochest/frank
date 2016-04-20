import datetime

from bs4 import BeautifulSoup
from flask import json
from behave import *
import humanize


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
    context.post_email = {
        'from': from_email,
        'to': to_emails,
        'subject': subject,
        'body': body,
        'start_time': datetime,
        'duration': duration,
    }
    for i, to in enumerate(to_emails):
        key = 'envelope[recipients][{}]'.format(i)
        data[key] = to

    with context.app.app_context():
        response = context.client.post('/calendar/invites/incoming', data=data)
        context.post_email['response'] = response
        assert response.status_code == 200


@when('I send him a meeting invitation')
def step_impl(context):
    post_email(
        context,
        'err8n@eservices.virginia.edu',
        [
            'frankbot@cloudmailin.com',
            'lam2c@virginia.edu',
            'rag9b@virginia.edu',
        ],
        'This is the subject',
        '',
        datetime.datetime.now(),
        datetime.timedelta(minutes=30),
    )


@when('I send him a meeting invitation with {userid} in the {location}')
def step_impl(context, userid, location):
    if location == 'title':
        subject = 'Meeting with {}'.format(userid)
        body = ''
    else:
        subject = 'Meeting'
        body = 'Meeting with {}'.format(userid)

    post_email(
        context,
        'err8n@eservices.virginia.edu',
        [
            'frankbot@cloudmailin.com',
            'lam2c@virginia.edu',
            'rag9b@virginia.edu',
        ],
        subject,
        body,
        datetime.datetime.now(),
        datetime.timedelta(minutes=30),
    )


@when('I send him a meeting invitation for {delta_time}')
def step_impl(context, delta_time):
    when = datetime.datetime.now()
    if delta_time == 'tomorrow':
        when = when + datetime.timedelta(days=1)
    elif delta_time == 'yesterday':
        when = when - datetime.timedelta(days=1)
    when = when.replace(hour=16, minute=0)

    post_email(
        context,
        'err8n@eservices.virginia.edu',
        [
            'frankbot@cloudmailin.com',
            'lam2c@virginia.edu',
            'rag9b@virginia.edu',
        ],
        'This is the subject',
        '',
        when,
        datetime.timedelta(minutes=30),
    )


@when('I send him a meeting invitation as {userid}')
def step_impl(context, userid):
    post_email(
        context,
        '{}@eservices.virginia.edu'.format(userid),
        [
            'frankbot@cloudmailin.com',
            'lam2c@virginia.edu',
            'rag9b@virginia.edu',
        ],
        'This is the subject',
        '',
        datetime.datetime.now(),
        datetime.timedelta(minutes=30),
    )


@when('I visit the invitation\'s page')
def step_impl(context):
    data = json.loads(context.post_email['response'].data)
    response = context.client.get('/calendar/invites/{id}/'.format(**data))
    context.post_email['response'] = response
    assert response.status_code == 200


@then('I should see my consultation')
def step_impl(context):
    subject = context.post_email['subject']
    response = context.post_data['response']
    assert subject in response.data


@then('I should see the duration of the consultation')
def step_impl(context):
    duration = context.post_email['duration']
    response = context.post_data['response']
    assert humanize.naturaltime(duration) in response.data


@then('I should see the date of the consultation')
def step_impl(context):
    start_time = context.post_email['start_time']
    response = context.post_email['response']
    assert humanize.naturalday(start_time) in response.data


@then('I should see {userid} as the consultant')
def step_impl(context, userid):
    soup = BeautifulSoup(context.post_email['response'].data, 'html.parser')
    assert userid in ' '.join(soup.select('#consultant').strings)


@then('I should see the other attendees of the consultation')
def step_impl(context):
    tos = [email.split('@')[0] for email in context.post_email['to']]
    data = context.post_email['response'].data
    assert all(t in data for t in tos)


@then('I should see {userid} as an attendee')
def step_impl(context, userid):
    soup = BeautifulSoup(context.post_email['response'].data, 'html.parser')
    assert userid in ' '.join(soup.select('#attendees').strings)


@then('I should not see {userid} as an attendee')
def step_impl(context, userid):
    soup = BeautifulSoup(context.post_email['response'].data, 'html.parser')
    assert userid not in ' '.join(soup.select('#attendees').strings)


@then('I should see that the invitation is {status}')
def step_impl(context, status):
    soup = BeautifulSoup(context.post_email['response'].data, 'html.parser')
    assert status in ' '.join(soup.select('#status').strings)


@then('I should see a link to a consultation')
def step_impl(context):
    soup = BeautifulSoup(context.post_email['response'].data, 'html.parser')
    assert any(
        'Consultation' in ' '.join(a.strings) for a in soup.find_all('a')
    )


@then('I should not see a link to a consultation')
def step_impl(context):
    soup = BeautifulSoup(context.post_email['response'].data, 'html.parser')
    assert not any(
        'Consultation' in ' '.join(a.strings) for a in soup.find_all('a')
    )
