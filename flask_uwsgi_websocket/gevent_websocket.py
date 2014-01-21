from . import WebSocketClient, WebSocketMiddleware
import gevent.select
import uwsgi


class GeventWebSocketClient(WebSocketClient):
    def receive(self):
        ready = gevent.select.select([self.fd], [], [], self.timeout)
        try:
            return uwsgi.websocket_recv_nb()
        except IOError:  # client disconnected
            pass


class GeventWebSocketMiddleware(WebSocketMiddleware):
    Client = GeventWebSocketClient
