'''
Flask-uWSGI-WebSocket
---------------------
High-performance WebSockets for your Flask apps powered by `uWSGI <http://uwsgi-docs.readthedocs.org/en/latest/>`_.
'''

__docformat__ = 'restructuredtext'
__version__ = '0.0.3'
__license__ = 'MIT'
__author__  = 'Zach Kelling'

import sys
from werkzeug.debug import DebuggedApplication
from ._uwsgi import uwsgi


class WebSocketClient(object):
    def __init__(self, fd, timeout=100):
        self.fd = fd
        self.timeout = timeout

    def receive(self):
        print 'hi'
        uwsgi.wait_fd_read(self.fd, self.timeout)
        uwsgi.suspend()
        fd = uwsgi.ready_fd()
        print fd
        print 'hi'
        return uwsgi.websocket_recv_nb()

    def recv(self):
        return uwsgi.websocket_recv()

    def recv_nb(self):
        return uwsgi.websocket_recv_nb()

    def send(self, msg):
        return uwsgi.websocket_send(msg)

    def send_binary(self, msg):
        return uwsgi.websocket_send_binary(msg)

    def send_from_sharedarea(self, id, pos):
        return uwsgi.websocket_send_from_sharedarea(msg)

    def send_binary_from_sharedarea(self, id, pos):
        return uwsgi.websocket_send_binary_from_sharedarea(msg)


class WebSocketMiddleware(object):
    Client = WebSocketClient

    def __init__(self, wsgi_app, ws):
        self.app = wsgi_app
        self.ws  = ws

    def __call__(self, environ, start_response):
        handler = self.ws.websocket_routes.get(environ['PATH_INFO'])

        if handler:
            uwsgi.websocket_handshake(environ['HTTP_SEC_WEBSOCKET_KEY'], environ.get('HTTP_ORIGIN', ''))
            handler(self.Client(uwsgi.connection_fd(), self.ws.timeout))
        else:
            return self.app(environ, start_response)


class WebSocket(object):
    def __init__(self, app=None, timeout=100):
        if app:
            self.init_app(app)
        self.timeout = timeout
        self.websocket_routes = {}

    def init_app(self, app):
        if app.debug:
            app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

        app.wsgi_app = WebSocketMiddleware(app.wsgi_app, self)

    def route(self, rule, **options):
        def decorator(f):
            endpoint = options.pop('endpoint', None)
            self.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator

    def add_url_rule(self, rule, _, f, **options):
        self.websocket_routes[rule] = f

from ._gevent import *
