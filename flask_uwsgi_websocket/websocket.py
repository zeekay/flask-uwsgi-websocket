import os
import sys
import uuid
from ._uwsgi import uwsgi


class WebSocketClient(object):
    '''
    Default WebSocket client has a blocking recieve method, but still exports
    rest of uWSGI API.
    '''
    def __init__(self, environ, fd, timeout=60):
        self.environ = environ
        self.fd      = fd
        self.timeout = timeout
        self.id      = str(uuid.uuid1())

    def receive(self):
        return uwsgi.websocket_recv()

    def recv(self):
        return uwsgi.websocket_recv()

    def recv_nb(self):
        return uwsgi.websocket_recv_nb()

    def send(self, msg):
        return uwsgi.websocket_send(msg)

    def send_binary(self, msg):
        return uwsgi.websocket_send_binary(msg)

    def send_from_sharedarea(self, id, pos):
        return uwsgi.websocket_send_from_sharedarea(id, pos)

    def send_binary_from_sharedarea(self, id, pos):
        return uwsgi.websocket_send_binary_from_sharedarea(id, pos)


class WebSocketMiddleware(object):
    '''
    WebSocket Middleware that handles handshake and passes route a WebSocketClient.
    '''
    client = WebSocketClient

    def __init__(self, wsgi_app, websocket):
        self.wsgi_app  = wsgi_app
        self.websocket = websocket

    def __call__(self, environ, start_response):
        handler = self.websocket.routes.get(environ['PATH_INFO'])

        if handler:
            uwsgi.websocket_handshake(environ['HTTP_SEC_WEBSOCKET_KEY'], environ.get('HTTP_ORIGIN', ''))
            handler(self.client(environ, uwsgi.connection_fd(), self.websocket.timeout))
        else:
            return self.wsgi_app(environ, start_response)


class WebSocket(object):
    '''
    Flask extension which makes it easy to integrate uWSGI-powered WebSockets
    into your applications.
    '''
    middleware = WebSocketMiddleware

    def __init__(self, app=None, timeout=60):
        if app:
            self.init_app(app)
        self.timeout = timeout
        self.routes = {}

    def run(self, app=None, debug=False, host='localhost', port=5000, **kwargs):
        if not app:
            app = self.app.name + ':app'

        # kwargs are treated as uwsgi arguments
        if kwargs.get('master') is None:
            kwargs['master'] = True

        # boolean should be treated as empty value
        for k,v in kwargs.items():
            if v is True:
                kwargs[k] = ''

        # constructing uwsgi arguments
        uwsgi_args = ' '.join(['--{0} {1}'.format(k,v) for k,v in kwargs.items()])
        args = 'uwsgi --http {0}:{1} --http-websockets {2} --wsgi {3}'.format(host, port, uwsgi_args, app)

        print args

        # set enviromental variable to trigger adding debug middleware
        if self.app.debug or debug:
            args = 'FLASK_UWSGI_DEBUG=true {0}'.format(args)

        # run uwsgi with our args
        sys.exit(os.system(args))

    def init_app(self, app):
        self.app = app

        if os.environ.get('FLASK_UWSGI_DEBUG'):
            from werkzeug.debug import DebuggedApplication
            app.wsgi_app = DebuggedApplication(app.wsgi_app, True)
            app.debug = True

        app.wsgi_app = self.middleware(app.wsgi_app, self)
        app.run = lambda **kwargs: self.run(**kwargs)

    def route(self, rule):
        def decorator(f):
            self.routes[rule] = f
            return f
        return decorator
