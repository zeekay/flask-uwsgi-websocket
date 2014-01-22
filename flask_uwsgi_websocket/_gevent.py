from gevent import sleep, spawn
from gevent.event import Event
from gevent.queue import Queue
from gevent.select import select
import uuid

from . import WebSocket, WebSocketClient, WebSocketMiddleware
from ._uwsgi import uwsgi


class GeventWebSocketClient(object):
    def __init__(self, send_event, send_queue, recv_event, recv_queue, timeout=60):
        self.id = str(uuid.uuid1())
        self.send_event = send_event
        self.send_queue = send_queue
        self.recv_event = recv_event
        self.recv_queue = recv_queue
        self.timeout = timeout

    def send(self, message):
        self.send_queue.put(message)
        self.send_event.set()
        self.send_event.clear()

    def receive(self):
        self.recv_event.set()
        self.recv_event.clear()
        self.recv_queue.get()


class GeventWebSocketMiddleware(WebSocketMiddleware):
    client = GeventWebSocketClient

    def __call__(self, environ, start_response):
        handler = self.websocket.routes.get(environ['PATH_INFO'])

        if not handler:
            return self.wsgi_app(environ, start_response)

        # do handshake
        uwsgi.websocket_handshake(environ['HTTP_SEC_WEBSOCKET_KEY'], environ.get('HTTP_ORIGIN', ''))

        send_event = Event()
        send_queue = Queue()

        recv_event = Event()
        recv_queue = Queue()

        client = self.client(send_event, send_queue, recv_event, recv_queue)

        fd = uwsgi.connection_fd()

        def send():
            ready.set()
            message = send_queue.get()
            uwsgi.websocket_send(message)
        send_event.rawlink(send)

        def listen():
            ready.set()
            select([fd], [], [], client.timeout)
            try:
                recv_queue.put(uwsgi.websocket_recv_nb())
            except IOError:  # client disconnected
                pass
        recv_event.rawlink(listen)

        ready = Event()

        while True:
            ready.clear()
            ready.wait()


class GeventWebSocket(WebSocket):
    middleware = GeventWebSocketMiddleware
