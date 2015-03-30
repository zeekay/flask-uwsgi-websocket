from gevent import spawn, wait
from gevent.event import Event
from gevent.queue import Queue, Empty
from gevent.select import select
import uuid

from .websocket import WebSocket, WebSocketMiddleware
from ._uwsgi import uwsgi


class GeventWebSocketClient(object):
    def __init__(self, environ, fd, send_event, send_queue, recv_event, recv_queue, timeout=60):
        self.environ    = environ
        self.fd         = fd
        self.send_event = send_event
        self.send_queue = send_queue
        self.recv_event = recv_event
        self.recv_queue = recv_queue
        self.timeout    = timeout

        self.id         = str(uuid.uuid1())
        self.connected  = True

    def send(self, message):
        self.send_queue.put(message)
        self.send_event.set()

    def receive(self):
        return self.recv()

    def recv(self):
        return self.recv_queue.get()

    def close(self):
        self.connected = False


class GeventWebSocketMiddleware(WebSocketMiddleware):
    client = GeventWebSocketClient

    def __call__(self, environ, start_response):
        handler = self.websocket.routes.get(environ['PATH_INFO'])

        if not handler or 'HTTP_SEC_WEBSOCKET_KEY' not in environ:
            return self.wsgi_app(environ, start_response)

        # do handshake
        uwsgi.websocket_handshake(environ['HTTP_SEC_WEBSOCKET_KEY'], environ.get('HTTP_ORIGIN', ''))

        # setup events
        send_event = Event()
        send_queue = Queue()

        recv_event = Event()
        recv_queue = Queue(maxsize=1)

        # create websocket client
        client = self.client(environ, uwsgi.connection_fd(), send_event,
                             send_queue, recv_event, recv_queue, self.websocket.timeout)

        # spawn handler
        handler = spawn(handler, client)

        # spawn recv listener
        def listener(client):
            select([client.fd], [], [], client.timeout)
            recv_event.set()
        listening = spawn(listener, client)

        while True:
            if not client.connected:
                recv_queue.put(None)
                listening.kill()
                handler.join(client.timeout)
                return ''

            # wait for event to draw our attention
            wait([handler, send_event, recv_event], None, 1)

            # handle send events
            if send_event.is_set():
                try:
                    try:
                        while True:
                            uwsgi.websocket_send(send_queue.get_nowait())
                    except Empty:
                        send_event.clear()
                except IOError:
                    client.connected = False

            # handle receive events
            elif recv_event.is_set():
                recv_event.clear()
                try:
                    recv_queue.put(uwsgi.websocket_recv_nb())
                    listening = spawn(listener, client)
                except IOError:
                    client.connected = False

            # handler done, we're outta here
            elif handler.ready():
                listening.kill()
                return ''


class GeventWebSocket(WebSocket):
    middleware = GeventWebSocketMiddleware
