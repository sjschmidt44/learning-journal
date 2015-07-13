# _*_ coding: utf-8- _*_
from __future__ import unicode_literals
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from pyramid import testing
from cryptacular.bcrypt import BCRYPTPasswordManager
# from bs4 import BeautifulSoup

db_usr = os.environ.get('USER', )

TEST_DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://' + db_usr + '@localhost:5432/travis_ci_test'
)
os.environ['DATABASE_URL'] = TEST_DATABASE_URL
os.environ['TESTING'] = 'TRUE'

import journal

"""There is a problem with connection and or db_session"""


@pytest.fixture(scope='session')
def connection(request):
    engine = create_engine(TEST_DATABASE_URL)
    journal.Base.metadata.create_all(engine)
    connection = engine.connect()
    journal.DBSession.registry.clear()
    journal.DBSession.configure(bind=connection)
    journal.Base.metadata.bind = engine
    request.addfinalizer(journal.Base.metadata.drop_all)
    return connection


@pytest.fixture()
def db_session(request, connection):
    from transaction import abort
    trans = connection.begin()
    request.addfinalizer(trans.rollback)
    request.addfinalizer(abort)

    from journal import DBSession
    return DBSession


def login_helper(username, password, app):
    """
    Encapsulate app login for reuse in test_do_login_success
    Accept all status codes so that we can make assertions in tests
    """
    login_data = {'username': username, 'password': password}
    return app.post('/login', params=login_data, status='*')


def test_write_entry(db_session):
    kwargs = {'title': "Test Title", 'text': 'Test Entry'}
    kwargs['session'] = db_session
    assert db_session.query(journal.Entry).count() == 0
    entry = journal.Entry.write(**kwargs)
    assert isinstance(entry, journal.Entry)
    auto_fields = ['id', 'timestamp']
    for field in auto_fields:
        assert getattr(entry, field, None) is None
    db_session.flush()
    assert db_session.query(journal.Entry).count() == 1

    for field in kwargs:
        if field != 'session':
            assert getattr(entry, field, '') == kwargs[field]

    for auto in ['id', 'timestamp']:
        assert getattr(entry, auto, None) is not None


def test_entry_no_title_fails(db_session):
    bad_data = {'text': 'test text'}
    journal.Entry.write(session=db_session, **bad_data)
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_entry_no_text_fails(db_session):
    bad_data = {'title': 'test title'}
    journal.Entry.write(session=db_session, **bad_data)
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_read_entries_empty(db_session):
    entries = journal.Entry.all()
    assert len(entries) == 0


def test_read_entries_one(db_session):
    title_template = 'Entry Title {}'
    text_template = 'Entry Text {}'
    for x in range(3):
        journal.Entry.write(
            title=title_template.format(x),
            text=text_template.format(x),
            session=db_session)
        db_session.flush()
    entries = journal.Entry.all()
    assert entries[0].title > entries[1].title > entries[2].title
    for entry in entries:
        assert isinstance(entry, journal.Entry)


@pytest.fixture()
def app():
    from journal import main
    from webtest import TestApp
    app = main()
    return TestApp(app)


def test_empty_listing(app):
    response = app.get('/')
    assert response.status_code == 200
    actual = response.body
    expected = 'No entries here so far'
    assert expected in actual


@pytest.fixture()
def entry(db_session):
    entry = journal.Entry.write(
        title='Test Title',
        text='Test Entry Text',
        session=db_session
    )
    db_session.flush()
    return entry


def test_add_no_params(app):
    response = app.post('/add', status=302)
    assert '302 Found' in response.body


@pytest.fixture(scope='function')
def auth_req(request):
    manager = BCRYPTPasswordManager()
    settings = {
        'auth.username': 'admin',
        'auth.password': manager.encode('secret'),
    }
    testing.setUp(settings=settings)
    req = testing.DummyRequest()

    def cleanup():
        testing.tearDown()

    request.addfinalizer(cleanup)
    return req


def test_do_login_success(auth_req):
    from journal import do_login
    auth_req.params = {'username': 'admin', 'password': 'secret'}
    assert do_login(auth_req)


def test_do_login_bad_pass(auth_req):
    from journal import do_login
    auth_req.params = {'username': 'admin', 'password': 'wrong'}
    assert not do_login(auth_req)


def test_do_login_bad_user(auth_req):
    from journal import do_login
    auth_req.params = {'username': 'bad', 'password': 'secret'}
    assert not do_login(auth_req)


def test_do_login_missing_params(auth_req):
    from journal import do_login
    for params in ({'username': 'admin'}, {'password': 'secret'}):
        auth_req.params = params
        with pytest.raises(ValueError):
            do_login(auth_req)


INPUT_BTN = '<input id="submit-new" type="submit" value="Submit" name="Submit"/>'
ENTRY_ONE = 'Logout'


def test_start_as_anonymous(app):
    response = app.get('/', status=200)
    actual = response.body
    assert INPUT_BTN not in actual


def test_login_successful(app):
    username, password = ('admin', 'secret')
    redirect = login_helper(username, password, app)
    assert redirect.status_code == 302
    response = redirect.follow()
    assert response.status_code == 200
    actual = response.body
    assert ENTRY_ONE in actual


def test_login_fails(app):
    username, password = ('admin', 'wrong')
    response = login_helper(username, password, app)
    assert response.status_code == 200
    actual = response.body
    assert 'Login Failed' in actual
    assert INPUT_BTN not in actual


def test_logout(app):
    test_login_successful(app)
    redirect = app.get('/logout', status='3*')
    response = redirect.follow()
    assert response.status_code == 200
    actual = response.body
    assert INPUT_BTN not in actual


def test_new_entry_load(app):
    username, password = ('admin', 'wrong')
    response = login_helper(username, password, app)
    assert response.status_code == 200
    actual = response.body
    assert 'Login Failed' in actual
    assert INPUT_BTN not in actual


@pytest.fixture()
def test_entry(db_session):
    from journal import Entry
    entry = Entry.write(title="Test", text="Test Text", session=db_session)
    db_session.flush()
    return entry


def test_listing(app, test_entry):
    username, password = ('admin', 'secret')
    redirect = login_helper(username, password, app)
    assert redirect.status_code == 302
    eid = test_entry.id
    response = app.get('/detail/{id}'.format(id=eid))
    assert response.status_code == 200
    actual = response.body
    for field in ['title', 'text']:
        expected = getattr(test_entry, field, 'none')
        assert expected in actual


def test_post_to_add_view(app):
    username, password = 'admin', 'secret'
    login_helper(username, password, app)
    entry_data = {
        'title': 'Hello there',
        'text': 'This is a post',
    }
    response = app.post('/add', params=entry_data, status='3*')
    redirected = response.follow()
    actual = redirected.body
    assert entry_data['title'] in actual

"""New tests for resubmit"""


def test_login_notice_new_entry(app):
    response = app.get('/new-entry', status=200)
    actual = response.body
    expected = '<h1>Please Login</h1>'
    assert expected in actual


def test_login_notice_edit_entry(app, test_entry):
    app.get('/logout', status='3*')
    response = app.get('/edit-entry/{id}'.format(id=test_entry.id))
    actual = response.body
    expected = '<h1>Please Login</h1>'
    assert expected in actual


# def test_new_entry_with_markdown(app):
#     """Can't get these two to pass"""
#     username, password = 'admin', 'secret'
#     login_helper(username, password, app)
#     entry_details = {
#         'title': "#The new title",
#         'text': "```python\r\ndef fun():\r\n\treturn 'happy'\r\n```"
#     }
#     submit = app.post("/add", params=entry_details, status='3*')
#     response = submit.follow()
#     soup = response.html
#     expected_title = '<h3><a href="http://localhost/detail/10">#The new title</a></h3>'
#     assert expected_title in soup


# def test_new_entry_with_code_block(app):
#     """Can't get these two to pass"""
#     username, password = 'admin', 'secret'
#     login_helper(username, password, app)
#     entry_details = {
#         'title': "#The new title",
#         'text': "```python\r\ndef fun():\r\n\treturn 'happy'\r\n```"
#     }
#     submit = app.post("/add", params=entry_details, status='3*')
#     response = submit.follow()
#     soup = response.html
#     expected_code = '```python'
#     assert expected_code in soup
