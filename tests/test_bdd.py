# _*_ coding: utf-8- _*_
from __future__ import unicode_literals
import os
import pytest
import pytest_bdd
from sqlalchemy import create_engine
from pyramid import testing
from cryptacular.bcrypt import BCRYPTPasswordManager
from test_journal import login_helper

db_usr = os.environ.get('USER', )

TEST_DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://' + db_usr + '@localhost:5432/travis_ci_test'
)
os.environ['DATABASE_URL'] = TEST_DATABASE_URL
os.environ['TESTING'] = 'TRUE'

import journal


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


@pytest.fixture()
def app():
    from journal import main
    from webtest import TestApp
    app = main()
    return TestApp(app)


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


@pytest_bdd.fixture(Given='')
def test_verify_entry_id(app):
    username, password = ('admin', 'secret')
    redirect = login_helper(username, password, app)
    assert redirect.status_code == 302
    response = redirect.follow()
    assert response.status_code == 200
    actual = response.body
    assert actual is True  # Need to flush this out.


@pytest_bdd.fixture(Given='')
def test_redirect_to_page_by_id(app):
    pass


@pytest_bdd.fixture(Given='')
def test_edit_entry(app):
    pass


@pytest_bdd.fixture(Given='')
def test_markdown_in_text_area(app):
    pass


@pytest_bdd.fixture(Given='')
def test_markdown_in_entry(app):
    pass


@pytest_bdd.fixture(Given='')
def test_code_sample_syntax(app):
    pass


@pytest_bdd.fixture(Given='')
def test_code_sample_in_entry(app):
    pass


@pytest_bdd.fixture(Given='')
def test_something():
    pass
