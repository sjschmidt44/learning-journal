import os
import pytest
from sqlalchemy import create_engine

import journal

DB_USR = os.environ.get("USER", )
TEST_DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://' + DB_USR + '@localhost:5432/travis_ci_test'
)
os.environ['DATABASE_URL'] = TEST_DATABASE_URL
os.environ['TESTING'] = 'True'

"""Constructed with the help of Tanner Lake"""


@pytest.fixture(scope='session')
def connection(request):
    engine = create_engine(TEST_DATABASE_URL)
    journal.BASE.metadata.create_engine(engine)
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
def app(db_session):
    from webtest import TestApp
    from journal import main
    app = main()
    return TestApp(app)


@pytest.fixture()
def homepage(app):
    response = app.get('/')
    return response
