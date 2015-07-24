import os
import sys
import uuid

from ._uwsgi import uwsgi
from werkzeug.routing import Map, Rule, RequestRedirect, BuildError
from werkzeug.exceptions import HTTPException
from flask.app import setupmethod


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
        urls = self.websocket.url_map.bind_to_environ(environ)
        try:
            endpoint, args = urls.match()
            print(endpoint, args)
            handler = self.websocket.view_functions[endpoint]
        except HTTPException as e:
            raise e

        if not handler or 'HTTP_SEC_WEBSOCKET_KEY' not in environ:
            return self.wsgi_app(environ, start_response)

        uwsgi.websocket_handshake(environ['HTTP_SEC_WEBSOCKET_KEY'], environ.get('HTTP_ORIGIN', ''))
        handler(self.client(environ, uwsgi.connection_fd(), self.websocket.timeout), **args)
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
        self.url_map = Map()
        self.view_functions = {}
        self.blueprints = {}
        if app is not None:
            self.debug = app.debug
            self._got_first_request = app._got_first_request
        else:
            self.debug = False
            self._got_first_request = False

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

    def route(self, rule, **options):
        def decorator(f):
            endpoint = options.pop('endpoint', None)
            self.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        assert view_func is not None, 'view_func is mandatory'
        if endpoint is None:
            endpoint = view_func.__name__
        options['endpoint'] = endpoint
        # supposed to be GET
        methods = set(('GET', ))
        required_methods = set()
        provide_automatic_options = False

        rule = Rule(rule, methods=methods, **options)
        rule.provide_automatic_options = provide_automatic_options
        self.url_map.add(rule)
        if view_func is not None:
            old_func = self.view_functions.get(endpoint)
            if old_func is not None and old_func != view_func:
                raise AssertionError('View function mapping is overwriting an '
                                     'existing endpoint function: %s' % endpoint)
            self.view_functions[endpoint] = view_func

    # merged from flask.app
    @setupmethod
    def register_blueprint(self, blueprint, **options):
        '''
        Registers a blueprint on the WebSockets.
        '''
        first_registration = False
        if blueprint.name in self.blueprints:
            assert self.blueprints[blueprint.name] is blueprint, \
                'A blueprint\'s name collision occurred between %r and ' \
                '%r.  Both share the same name "%s".  Blueprints that ' \
                'are created on the fly need unique names.' % \
                (blueprint, self.blueprints[blueprint.name], blueprint.name)
        else:
            self.blueprints[blueprint.name] = blueprint
            first_registration = True
        blueprint.register(self, options, first_registration)
