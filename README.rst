Flask-WebSocket
===============
High-performance WebSockets for your Flask apps powered by `uWSGI <http://uwsgi-docs.readthedocs.org/en/latest/>`_.
Inspired by `Flask-Sockets <https://github.com/kennethreitz/flask-sockets>`_.

.. code-block:: python

    from flask import Flask
    from flask.ext.websocket import WebSocket

    app = Flask(__name__)
    websocket = WebSocket(app)

    @websocket.route('/echo')
    def echo(websocket):
        while True:
            message = websocket.receive()
            websocket.send(message)

Installation
------------
To install Flask-WebSocket, simply::

    $ pip install Flask-WebSocket

Deployment
----------
You can use uWSGI's built-in HTTP server to get up and running quickly::

    $ uwsgi --http :8080 --http-websockets --wsgi-file app.py

Of course for production you'll probably want to run uWSGI behind Haproxy or
nginx. uWSGI also supports several concurrency models.

- Multiprocess
- Multithreaded
- uWSGI native async api
- gevent
- greenlet + uWSGI async
- uGreen + uWSGI async
- PyPy continulets

Explore the `uWSGI documentation <http://uwsgi-docs.readthedocs.org/en/latest/WebSockets.html>`_ for all the details.


Development
-----------
You can still take advantage of Flask's interactive debugger for development by directly using werkzeug's ``DebuggedApplication`` middleware::

    from werkzeug.debug import DebuggedApplication
    app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

...and making sure you use uWSGI with only a single worker::


    $ uwsgi --http :8080 --http-websockets --wsgi-file --workers 1 --threads 8 app.py

If you specify ``app.debug = True`` before wrapping your app with Flask-Websocket, Flask-Websocket will do this for you.


API
---
Flask-Websocket exposes `uWSGI's WebSocket API <http://uwsgi-docs.readthedocs.org/en/latest/WebSockets.html#api>`_ with the exception of the handshake, which is done automatically for you.

``websocket.recv()``

``websocket.send(msg)``

``websocket.send_binary(msg)``

``websocket.recv_nb()``

``websocket.send_from_sharedarea(id, pos)``

``websocket.send_binary_from_sharedarea(id, pos)``
