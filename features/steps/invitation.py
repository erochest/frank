import datetime

from bs4 import BeautifulSoup
from flask import json
from behave import *
import humanize


def format_when(datetime, duration):
    """\
    This takes a meeting's starting time and duration and returns its formatted
    When.

    """

    formatted = '{} {}-{}. (UTC-05:00) Eastern Time (US & Canada)'.format(
        datetime.strftime('%A, %B %d, %Y'),
        datetime.strftime('%I:%M %p'),
        (datetime + duration).strftime('%I:%M %p'),
    )
    return (formatted, datetime, duration)


def post_email(
    context, from_email, to_emails, userids, subject, body, when_phrase
):
    (when_formatted, datetime, duration) = when_phrase
    data = {
        'envelope[from]': from_email,
        'headers[Subject]': subject,
        'headers[To]': ', '.join(to_emails),
        'plain': 'When: {}\n'
                 'Where: Elsewhere\n'
                 '\n'
                 '*~*~*~*~*~*~*~*~*~*\n'
                 '\n'
                 '{}\n'
                 '\n'
                 '\n'.format(when_formatted, body),
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


@given('Frank is alive')
def step_impl(context):
    assert context.client


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
        format_when(datetime.datetime.now(), datetime.timedelta(minutes=30)),
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
        format_when(datetime.datetime.now(), datetime.timedelta(minutes=30)),
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
        format_when(when, datetime.timedelta(minutes=30)),
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
        format_when(datetime.datetime.now(), datetime.timedelta(minutes=30)),
    )


@when('I visit the invitation\'s page')
def step_impl(context):
    data = json.loads(context.post_email['response'].data)
    url = '/calendar/invites/{id}'.format(**data)
    response = context.client.get(url)
    assert response.status_code == 200, '<{}> status = [{}] {}'.format(
        url, response.status_code, response.status,
    )
    context.post_email['response'] = response
    context.post_email['soup'] = BeautifulSoup(response.data, 'html.parser')


@when('I send him an invitation for a meeting that meets {meeting_time} '
      'at {start_time} for {duration}, starting {start_date}')
def step_impl(context, meeting_time, start_time, duration, start_date):
    (m, d, y) = [int(part.strip('.')) for part in start_date.split('/')]
    strp = '{month:02}/{day:02}/{year:04}. {start_time}'.format(
        month=m, day=d, year=y, start_time=start_time,
    )
    start_time_obj = datetime.datetime.strptime(
        strp,
        '%m/%d/%Y. %I:%M %p',
        )
    duration_minutes = datetime.timedelta(minutes=int(duration.split()[0]))
    when_phrase = ('Occurs {} from {} to {} effective {}. '
                   '(UTF-05:00) Eastern Time (US & Canada)').format(
                    meeting_time,
                    start_time,
                    (start_time_obj + duration_minutes).strftime('%I:%M %p')
                                                       .lstrip('0'),
                    start_date,
                   )
    post_email(
        context,
        'err8n@eservices.virginia.edu',
        [
            'frankbot@cloudmailin.com',
            '"Guinevere Aguilar" <gva9b@eservices.virginia.edu>',
        ],
        ['gva9b'],
        'This is the subject',
        '',
        (when_phrase, start_time_obj, duration_minutes),
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
    assert ('{} minute(s)'.format(round(duration.total_seconds() / 60.0))
            in response.data.decode('utf8'))


@then('I should see the date of the consultation')
def step_impl(context):
    start_time = context.post_email['start_time']
    response = context.post_email['response']
    assert humanize.naturalday(start_time) in response.data.decode('utf8')


@then('I should see {userid} as the meeting owner')
def step_impl(context, userid):
    soup = context.post_email['soup']
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
    soup = context.post_email['soup']
    strings = []
    for attendees in soup.select('#attendees'):
        strings += attendees.strings
    assert userid in ' '.join(strings)


@then('I should not see {userid} as an attendee')
def step_impl(context, userid):
    soup = context.post_email['soup']
    strings = []
    for attendees in soup.select('#attendees'):
        strings += attendees.strings
    assert userid not in ' '.join(strings)


@then('I should see that the invitation is {status}')
def step_impl(context, status):
    soup = context.post_email['soup']
    strings = []
    for status_tag in soup.select('#status'):
        strings += status_tag.strings
    assert status in ' '.join(strings)


@then('I should see a link to a consultation')
def step_impl(context):
    soup = context.post_email['soup']
    assert 'Consult' in {a.string for string in soup.select('a')}


@then('I should not see a link to a consultation')
def step_impl(context):
    soup = context.post_email['soup']
    assert 'Consult' not in {a.string for string in soup.select('a')}


@then('I should see it marked as recurring')
def step_impl(context):
    soup = context.post_email['soup']
    assert soup.find(id='recurring')
