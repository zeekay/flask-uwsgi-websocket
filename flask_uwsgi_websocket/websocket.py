import os
import sys
import uuid

from ._uwsgi import uwsgi


class WebSocketClient(object):
    '''
    Default WebSocket client has a blocking recieve method, but still exports
    rest of uWSGI API.
    '''
    def __init__(self, environ, fd, timeout=5):
        self.environ   = environ
        self.fd        = fd
        self.timeout   = timeout
        self.id        = str(uuid.uuid1())
        self.connected = True

    def receive(self):
        return self.recv()

    def recv(self):
        try:
            return uwsgi.websocket_recv()
        except IOError:
            return None

    def recv_nb(self):
        return uwsgi.websocket_recv_nb()

    def send(self, msg, binary=False):
        if binary:
            return self.send_binary(msg)
        return uwsgi.websocket_send(msg)

    def send_binary(self, msg):
        return uwsgi.websocket_send_binary(msg)

    def send_from_sharedarea(self, id, pos):
        return uwsgi.websocket_send_from_sharedarea(id, pos)

    def send_binary_from_sharedarea(self, id, pos):
        return uwsgi.websocket_send_binary_from_sharedarea(id, pos)

    def close(self):
        self.connected = False


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

        if not handler or 'HTTP_SEC_WEBSOCKET_KEY' not in environ:
            return self.wsgi_app(environ, start_response)

        uwsgi.websocket_handshake(environ['HTTP_SEC_WEBSOCKET_KEY'], environ.get('HTTP_ORIGIN', ''))
        handler(self.client(environ, uwsgi.connection_fd(), self.websocket.timeout))
        return []


class WebSocket(object):
    '''
    Flask extension which makes it easy to integrate uWSGI-powered WebSockets
    into your applications.
    '''
    middleware = WebSocketMiddleware

    def __init__(self, app=None, timeout=5):
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

        uwsgi_executable = "{0}/uwsgi".format(os.path.dirname(sys.executable))
        args = '{0} --http {1}:{2} --http-websockets {3} --wsgi {4}'.format(uwsgi_executable, host, port, uwsgi_args, app)

        # set enviromental variable to trigger adding debug middleware
        if self.app.debug or debug:
            args = 'FLASK_UWSGI_DEBUG=true {0} --python-autoreload 1'.format(args)

        # run uwsgi with our args
        print('Running: {0}'.format(args))
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
