# _*_ coding: utf-8- _*_
from __future__ import unicode_literals
from pytest_bdd import scenario, given, when, then
from test_journal import login_helper
# import pytest

# import journals


@scenario('features/homepage.feature', 'Click an entry title')
def test_entry_exists():
    """Click on entry title, and navigate to that entry's detail view"""
    pass


@given('I want to have a permalink for each journal entry')
def title_active_anchor_link(app, entry):
    response = app.get('detail/{id}'.format(id=entry.id))
    assert response.status_code == 200


@when('I click each journal entry title')
def click_entry():
    pass


@then('I am directed to a detail page for only that entry')
def detail_page_clicked_title(app, entry):
    response = app.get('detail/{id}'.format(id=entry.id))
    assert response.status_code == 200
    redirect = response.follow()
    assert entry.text in redirect.body


@scenario('features/homepage.feature', 'Click on the edit button')
def test_edit_button():
    """
    Click the edit button, and have the ability to edit and resubmit to
    that entry in the DB
    """
    pass


@given('I want to edit my entry')
def edit_button_available(app, entry):
    username, password = 'admin', 'secret'
    login_helper(username, password, app)
    response = app.get('detail/{id}'.format(id=entry.id))
    expected = '<button id="input-forward">Edit Entry</button>'
    assert expected in response.body


@when('I click on the edit button')
def input_area_available():
    pass


@then('I can update or fix my entry')
def enter_text_and_submit():
    pass


@scenario('features/homepage.feature', 'View entries with formatted markdown')
def test_page_loads_from_db():
    """Entries will be formatted with markdown"""
    pass


@given('I want to display my entries')
def entries_display():
    pass


@given('use Markdown to decorate entry text')
def entries_with_markdown():
    pass


@when('I load my entries')
def list_view_display():
    pass


@then('I can view them formatted nicely')
def markdown_formatting():
    pass


@scenario(
    'features/homepage.feature',
    'View code block entries with syntax highlighting'
)
def test_code_highlighting():
    """Code blocks will be well formatted with syntax highlighting"""
    pass


@given('I want to see colorized code samples in my entries')
def code_sample():
    pass


@when('I have entered code samples')
def check_backtick_or_indents():
    pass


@then('I can more easily understand them')
def code_block_formatting():
    pass
