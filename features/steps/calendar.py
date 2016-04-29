import datetime

from bs4 import BeautifulSoup
from flask import json
from behave import *
import humanize


def post_email(
    context, from_email, to_emails, userids, subject, body, datetime, duration
):
    data = {
        'envelope[from]': from_email,
        'headers[Subject]': subject,
        'headers[To]': ', '.join(to_emails),
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
        'to': userids,
        'subject': subject,
        'body': body,
        'start_time': datetime,
        'duration': duration,
    }

    with context.app.app_context():
        response = context.client.post('/calendar/invites/incoming', data=data)
        context.post_email['response'] = response
        assert response.status_code == 200, 'status = [{}] {}'.format(
            response.status_code, response.status,
        )


@when('I send him a meeting invitation')
def step_impl(context):
    post_email(
        context,
        'err8n@eservices.virginia.edu',
        [
            'frankbot@cloudmailin.com',
            '"Davis Ferrell" <daf2c@virginia.edu>',
            '"Guinevere Aguilar" <gva9b@eservices.virginia.edu>',
        ],
        ['daf2c', 'gva9b'],
        'This is the subject',
        '',
        datetime.datetime.now(),
        datetime.timedelta(minutes=30),
    )


@when('I send him a meeting invitation with {userid} in the {location}')
def step_impl(context, userid, location):
    if location == 'title':
        subject = 'Meeting with {}@'.format(userid)
        body = ''
    else:
        subject = 'Meeting'
        body = 'Meeting with {}@ and others'.format(userid)

    post_email(
        context,
        'err8n@eservices.virginia.edu',
        [
            'frankbot@cloudmailin.com',
            '"Davis Ferrell" <daf2c@virginia.edu>',
            '"Guinevere Aguilar" <gva9b@eservices.virginia.edu>',
        ],
        ['daf2c', 'gva9b'],
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
            '"Davis Ferrell" <daf2c@virginia.edu>',
            '"Guinevere Aguilar" <gva9b@eservices.virginia.edu>',
        ],
        ['daf2c', 'gva9b'],
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
            '"Davis Ferrell" <daf2c@virginia.edu>',
            '"Guinevere Aguilar" <gva9b@eservices.virginia.edu>',
        ],
        ['daf2c', 'gva9b'],
        'This is the subject',
        '',
        datetime.datetime.now(),
        datetime.timedelta(minutes=30),
    )


@when('I visit the invitation\'s page')
def step_impl(context):
    data = json.loads(context.post_email['response'].data)
    url = '/calendar/invites/{id}'.format(**data)
    response = context.client.get(url)
    context.post_email['response'] = response
    assert response.status_code == 200, '<{}> status = [{}] {}'.format(
        url, response.status_code, response.status,
    )


@then('I should see my consultation')
def step_impl(context):
    subject = context.post_email['subject']
    response = context.post_email['response']
    assert subject in response.data.decode('utf8')


@then('I should see the duration of the consultation')
def step_impl(context):
    duration = context.post_email['duration']
    response = context.post_email['response']
    assert '{} minute(s)'.format(duration / 60) in response.data.decode('utf8')


@then('I should see the date of the consultation')
def step_impl(context):
    start_time = context.post_email['start_time']
    response = context.post_email['response']
    assert humanize.naturalday(start_time) in response.data.decode('utf8')


@then('I should see {userid} as the meeting owner')
def step_impl(context, userid):
    soup = BeautifulSoup(context.post_email['response'].data, 'html.parser')
    strings = []
    for consultant in soup.select('#owner'):
        strings += consultant.strings
    assert userid in ' '.join(strings)


@then('I should see the other attendees of the consultation')
def step_impl(context):
    tos = context.post_email['to']
    data = context.post_email['response'].data.decode('utf8')
    assert all(t in data for t in tos)


@then('I should see {userid} as an attendee')
def step_impl(context, userid):
    soup = BeautifulSoup(context.post_email['response'].data, 'html.parser')
    strings = []
    for attendees in soup.select('#attendees'):
        strings += attendees.strings
    assert userid in ' '.join(strings)


@then('I should not see {userid} as an attendee')
def step_impl(context, userid):
    soup = BeautifulSoup(context.post_email['response'].data, 'html.parser')
    strings = []
    for attendees in soup.select('#attendees'):
        strings += attendees.strings
    assert userid not in ' '.join(strings)


@then('I should see that the invitation is {status}')
def step_impl(context, status):
    soup = BeautifulSoup(context.post_email['response'].data, 'html.parser')
    strings = []
    for status_tag in soup.select('#status'):
        strings += status_tag.strings
    assert status in ' '.join(strings)
