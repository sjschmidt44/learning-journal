# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import datetime
import sqlalchemy as sa
from waitress import serve
from pyramid.config import Configurator
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import remember, forget
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from cryptacular.bcrypt import BCRYPTPasswordManager
from markdown import markdown

# db_usr = os.environ.get('USER', )

DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension())
)
Base = declarative_base()
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    "postgresql://Scott@localhost:5432/learning-journal"
)
HERE = os.path.dirname(os.path.abspath(__file__))


class Entry(Base):
    __tablename__ = 'entries'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    title = sa.Column(sa.Unicode(127), nullable=False)
    text = sa.Column(sa.UnicodeText, nullable=False)
    timestamp = sa.Column(
        sa.DateTime, nullable=False, default=datetime.datetime.utcnow
    )

    def __repr__(self):
        return self.title

    @classmethod
    def all(cls, session=None):
        if session is None:
            session = DBSession
        return session.query(cls).order_by(cls.timestamp.desc()).all()

    @classmethod
    def write(cls, title=None, text=None, session=None):
        if session is None:
            session = DBSession
        instance = cls(title=title, text=text)
        session.add(instance)
        return instance

    @classmethod
    def one(cls, eid=None, session=None):
        if session is None:
            session = DBSession
        return session.query(cls).get(eid)

    @classmethod
    def modify(cls, eid=None, title=None, text=None, session=None):
        if session is None:
            session = DBSession
        instance = cls.one(eid)
        instance.title = title
        instance.text = text
        session.add(instance)
        return instance

    @classmethod
    def delete(cls, eid, session=None):
        if session is None:
            session = DBSession
        instance = cls.one(eid)
        session.delete(instance)

    @property
    def markdown(self):
        return markdown(self.text, extensions=['codehilite', 'fenced_code'])


def init_db():
    engine = sa.create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)


@view_config(route_name='home', renderer='templates/list.jinja2')
def list_view(request):
    entries = Entry.all()
    return {'entries': entries}


@view_config(route_name='detail', renderer='templates/detail.jinja2')
def detail_view(request):
    entry = Entry.one(request.matchdict['id'])
    return {'entry': entry}


@view_config(route_name='new-entry', renderer='templates/new-entry.jinja2')
def create_view(request):
    return {}


@view_config(route_name='edit-entry', xhr=True, renderer='json')
@view_config(
    route_name='edit-entry',
    xhr=False,
    renderer='templates/edit-entry.jinja2'
)
def edit_view(request):
    """Work in progress"""
    entry = Entry.one(request.matchdict['id'])
    if request.method == 'GET':
        entry = json.dumps(entry)
        return {'entry': entry}

    return {'entry': entry}


@view_config(route_name='add', request_method='POST')
def add_entry(request):
    title = request.params.get('title')
    text = request.params.get('text')
    Entry.write(title=title, text=text)
    return HTTPFound(request.route_url('home'))


@view_config(route_name='modify', request_method='POST')
def modify_entry(request):
    eid = request.matchdict['id']
    title = request.params.get('title')
    text = request.params.get('text')
    Entry.modify(eid=eid, title=title, text=text)
    return HTTPFound(request.route_url('home'))


@view_config(route_name='delete', request_method='POST')
def delete(request):
    entry = request.matchdict['id']
    Entry.delete(eid=entry.id)
    return HTTPFound(request.route_url('home'))


@view_config(route_name='login', renderer='templates/login.jinja2')
def login(request):
    """authenticate a user by username/password"""
    username = request.params.get('username', '')
    error = ''
    if request.method == 'POST':
        error = "Login Failed"
        authenticated = False
        try:
            authenticated = do_login(request)
        except ValueError as e:
            error = str(e)

        if authenticated:
            headers = remember(request, username)
            return HTTPFound(request.route_url('home'), headers=headers)

    return {'error': error, 'username': username}


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(request.route_url('home'), headers=headers)


@view_config(context=DBAPIError)
def db_exception(context, request):
    from pyramid.response import Response
    response = Response(context.message)
    response.status_int = 500
    return response


def main():
    """Create a configured wsgi app"""
    settings = {}
    debug = os.environ.get('DEBUG', True)
    settings['reload_all'] = debug
    settings['debug_all'] = debug
    settings['auth.username'] = os.environ.get('AUTH_USERNAME', 'admin')
    manager = BCRYPTPasswordManager()
    settings['auth.password'] = os.environ.get(
        'AUTH_PASSWORD', manager.encode('secret')
    )
    if not os.environ.get('TESTING', False):
        engine = sa.create_engine(DATABASE_URL)
        DBSession.configure(bind=engine)
    auth_secret = os.environ.get('JOURNAL_AUTH_SECRET', 'itsaseekrit')
    config = Configurator(
        settings=settings,
        authentication_policy=AuthTktAuthenticationPolicy(
            secret=auth_secret,
            hashalg='sha512'
        ),
        authorization_policy=ACLAuthorizationPolicy(),
    )
    config.include('pyramid_tm')
    config.include('pyramid_jinja2')
    config.add_route('home', '/')
    config.add_route('add', '/add')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('detail', '/detail/{id}')
    config.add_route('new-entry', '/new-entry')
    config.add_route('edit-entry', '/edit-entry/{id}')
    config.add_route('modify', '/modify/{id}')
    config.add_route('delete', '/delete')
    config.add_static_view('static', os.path.join(HERE, 'static'))
    config.scan()
    app = config.make_wsgi_app()
    return app


def do_login(request):
    username = request.params.get('username', None)
    password = request.params.get('password', None)
    if not (username and password):
        raise ValueError('Both user and pass are required')

    settings = request.registry.settings
    manager = BCRYPTPasswordManager()
    if username == settings.get('auth.username', ''):
        hashed = settings.get('auth.password', '')
        return manager.check(hashed, password)


if __name__ == '__main__':
    app = main()
    port = os.environ.get('PORT', 5000)
    serve(app, host='0.0.0.0', port=port)
