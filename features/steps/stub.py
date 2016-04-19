from behave import *
from sqlalchemy import text


@given("Frank is alive")
def step_impl(context):
    assert context.client


@when("I visit the site")
def step_impl(context):
    context.page = context.client.get('/')
    assert context.page


@when ("I select the answer from the database")
def step_impl(context):
    context.answer = context.db.session.execute(text('SELECT 42;'), {})
    assert context.answer


@then("I should see \"{message}\"")
def step_impl(context, message):
    assert message in context.page.data.decode('utf8')


@then("I should get back '{answer}'")
def step_impl(context, answer):
    answer = int(answer)
    assert answer == 42
