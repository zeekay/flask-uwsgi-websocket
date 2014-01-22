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
    client = GeventWebSocketClient


class GeventWebSocket(WebSocket):
    middleware = GeventWebSocketMiddleware
