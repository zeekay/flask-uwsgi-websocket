Flask-uWSGI-WebSocket
=====================
High-performance WebSockets for your Flask apps powered by `uWSGI
<http://uwsgi-docs.readthedocs.org/en/latest/>`_.  Inspired by `Flask-Sockets
<https://github.com/kennethreitz/flask-sockets>`_.

.. code-block:: python

    from flask import Flask
    from flask.ext.uwsgi_websocket import WebSocket

    app = Flask(__name__)
    ws = WebSocket(app)

    @ws.route('/echo')
    def echo(ws):
        while True:
            msg = ws.receive()
            ws.send(message)

Installation
------------
To install Flask-uWSGI-WebSocket, simply::

    $ pip install Flask-uWSGI-WebSocket

Deployment
----------
You can use uWSGI's built-in HTTP router to get up and running quickly::

    $ uwsgi --master --http :8080 --http-websockets --wsgi-file app.py

uWSGI supports several concurrency models, in particular it has nice support
for Gevent. If you want to use Gevent, use
``flask.ext.uwsgi_websocket.GeventWebSocket`` and configure uWSGI to use the
gevent loop engine:

    $ uwsgi --master --http :8080 --http-websockets --gevent 100 --wsgi-file app.py

For production you'll probably want to run uWSGI behind Haproxy or nginx of
course, instead of using the built-int HTTP router.  Explore the `uWSGI
documentation <http://uwsgi-docs.readthedocs.org/en/latest/WebSockets.html>`_
for more detail.


Development
-----------
It's possible to take advantage of Flask's interactive debugger by installing
werkzeug's ``DebuggedApplication`` middleware::

    from werkzeug.debug import DebuggedApplication
    app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

...and running uWSGI with only a single worker::


    $ uwsgi --master --http :8080 --http-websockets --wsgi-file --workers 1 --threads 8 app.py

If you specify ``app.debug = True``, Flask-uWSGI-Websocket will do this
automatically for you.


API
---
Flask-uWSGI-Websocket automatically performs the WebSocket handshake for you
and passes your router a websocket client exposing `uWSGI's WebSocket API
<http://uwsgi-docs.readthedocs.org/en/latest/WebSockets.html#api>`_.

``websocket.recv()``

``websocket.send(msg)``

``websocket.send_binary(msg)``

``websocket.recv_nb()``

``websocket.send_from_sharedarea(id, pos)``

``websocket.send_binary_from_sharedarea(id, pos)``

In addition there is a special ``websocket.receive()`` method which makes using
non-blocking calls simpler.
