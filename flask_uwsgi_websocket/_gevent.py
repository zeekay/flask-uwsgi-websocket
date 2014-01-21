from . import WebSocket, WebSocketClient, WebSocketMiddleware
from ._uwsgi import uwsgi
import gevent.select


class GeventWebSocketClient(WebSocketClient):
    def receive(self):
        ready = gevent.select.select([self.fd], [], [], self.timeout)
        try:
            return uwsgi.websocket_recv_nb()
        except IOError:  # client disconnected
            pass


class GeventWebSocketMiddleware(WebSocketMiddleware):
    Client = GeventWebSocketClient


class GeventWebSocket(WebSocket):
    def init_app(self, app):
        if app.debug:
            app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

        app.wsgi_app = GeventWebSocketMiddleware(app.wsgi_app, self)
