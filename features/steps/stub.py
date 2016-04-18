from behave import *


@given("Frank is alive")
def step_impl(context):
    assert context.client


@when("I visit the site")
def step_impl(context):
    context.page = context.client.get('/')
    assert context.page


@then("I should see \"{message}\"")
def step_impl(context, message):
    assert message in context.page.data.decode('utf8')
