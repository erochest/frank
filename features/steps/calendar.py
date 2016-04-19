from flask import url_for
from behave import *


@when('I send him a meeting invitation')
def step_impl(context):
    with context.app.app_context():
        context.client.post(
            url_for('frank.views.calendar.invites_incoming'),
            data={
                'envelope': None,
                'headers': None,
                'plain': None,
                'html': None,
                'reply_plain': None,
                'attachments': None,
            },
        )


@when('I send him a meeting invitation with {userid} in the {location}')
def step_impl(context, userid, location):
    raise NotImplementedError


@when('I send him a meeting invitation for {delta_time}')
def step_impl(context, delta_time):
    raise NotImplementedError


@then('he should recognize that I have a consultation')
def step_impl(context):
    raise NotImplementedError


@then('he should scrape the duration of the consultation')
def step_impl(context):
    raise NotImplementedError


@then('he should scrape the date of the consultation')
def step_impl(context):
    raise NotImplementedError


@then('he should scrape the other attendees of the consultation')
def step_impl(context):
    raise NotImplementedError


@then('he should scrape {userid} from the {location} of the invitation')
def step_impl(context):
    raise NotImplementedError


@then('he should recognize that the invitation is {status}')
def step_impl(context, status):
    raise NotImplementedError


@then('he should create a meeting for the invitation')
def step_impl(context):
    raise NotImplementedError


@then('he should not create a meeting for the invitation')
def step_impl(context):
    raise NotImplementedError
