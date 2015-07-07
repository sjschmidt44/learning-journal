# _*_ coding: utf-8- _*_
from __future__ import unicode_literals
from pytest_bdd import scenario, given, when, then
# import pytest

# import journal


"""Review webtest docs for supplimental info."""


# @pytest.fixture()
# def pytestbdd_feature_basedir():
#     return b'~/Projects/pyEnvs/learning-journal/tests/features/'


@scenario('features/homepage.feature', 'Click an entry title')
def test_entry_exists():
    """Click and entry title, and navigate to that entry's detail view"""
    pass


@given('I want to have a permalink for each journal entry')
def test_title_active_anchor_link():
    pass


@when('I click each journal entry title')
def test_click_entry():
    pass


@then('I am directed to a detail page for only that entry')
def test_detail_page_clicked_title():
    pass


@scenario('features/homepage.feature', 'Click on the edit button')
def test_edit_button():
    """
    Click the edit button, and have the ability to edit and resubmit to
    that entry in the DB
    """
    pass


@given('I want to edit my entry')
def test_edit_button_available():
    pass


@when('I click on the edit button')
def test_input_area_available():
    pass


@then('I can update or fix my entry')
def test_enter_text_and_submit():
    pass


@scenario('features/homepage.feature', 'View entries with formatted markdown')
def test_page_loads_from_db():
    """Entries will be formatted with markdown"""
    pass


@given('I want to display my entries')
def test_entries_display():
    pass


@given('use Markdown to decorate entry text')
def test_entries_with_markdown():
    pass


@when('I load my entries')
def test_list_view_display():
    pass


@then('I can view them formatted nicely')
def test_markdown_formatting():
    pass


@scenario(
    'features/homepage.feature',
    'View code block entries with syntax highlighting'
)
def test_code_highlighting():
    """Code blocks will be well formatted with syntax highlighting"""
    pass


@given('I want to see colorized code samples in my entries')
def test_code_sample():
    pass


@when('I have entered code samples')
def test_check_backtick_or_indents():
    pass


@then('I can more easily understand them')
def test_code_block_formatting():
    pass
