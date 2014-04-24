Flask-uWSGI-WebSocket
=====================
High-performance WebSockets for your Flask apps powered by `uWSGI
<http://uwsgi-docs.readthedocs.org/en/latest/>`_. Low-level uWSGI WebSocket API
access and flexible high-level abstractions for building complex WebSocket
applications with Flask. Supports several different concurrency models
including Gevent. Inspired by `Flask-Sockets
<https://github.com/kennethreitz/flask-sockets>`_.

.. code-block:: python

    from flask import Flask
    from flask.ext.uwsgi_websocket import GeventWebSocket

    app = Flask(__name__)
    ws = GeventWebSocket(app)

    @ws.route('/echo')
    def echo(ws):
        while True:
            msg = ws.receive()
            ws.send(msg)

    if __name__ == '__main__':
        app.run(gevent=100)


Installation
------------
Preferred method of installation is via pip::

    $ pip install Flask-uWSGI-WebSocket


Deployment
----------
You can use uWSGI's built-in HTTP router to get up and running quickly::

    $ uwsgi --master --http :8080 --http-websockets --wsgi echo:app

...which is what ``app.run`` does after wrapping your Flask app::

    app.run(debug=True, host='localhost', port=8080, master=true, processes=8)

uWSGI supports several concurrency models, in particular it has nice support
for Gevent. If you want to use Gevent, import
``flask.ext.uwsgi_websocket.GeventWebSocket`` and configure uWSGI to use the
gevent loop engine::

    $ uwsgi --master --http :8080 --http-websockets --gevent 100 --wsgi echo:app

...or::

    app.run(debug=True, gevent=100)


Note that you cannot use multiple threads with gevent loop engine.

For production you'll probably want to run uWSGI behind Haproxy or nginx,
instead of using the built-int HTTP router. Explore the `uWSGI documentation
<http://uwsgi-docs.readthedocs.org/en/latest/WebSockets.html>`_ for more
detail about the various concurrency and deployment options.


Development
-----------
It's possible to take advantage of Flask's interactive debugger by installing
werkzeug's ``DebuggedApplication`` middleware::

    from werkzeug.debug import DebuggedApplication
    app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

...and running uWSGI with only a single worker::

    $ uwsgi --master --http :8080 --http-websockets --wsgi-file --workers 1 --threads 8 app.py

If you use ``app.run(debug=True)`` or export ``FLASK_UWSGI_DEBUG``,
Flask-uWSGI-Websocket will do this automatically for you.


Examples
--------
There are several examples `available here <https://github.com/zeekay/flask-uwsgi-websocket/tree/master/examples>`_.

API
---
``flask_uwsgi_websocket.WebSocket``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Applies ``WebSocketMiddleware`` to your Flask App, allowing you to decorate
routes with the ``route`` method, turning them into WebSocket handlers.

Additionally monkey-patches ``app.run``, to run your app directly in uWSGI.

``route(url)``

``run(debug, host, port, **kwargs)``
``**kwargs`` are passed to uWSGI as command line arguments.


``flask_uwsgi_websocket.WebSocketMiddleware``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
WebSocket Middleware which automatically performs WebSocket handshake and
passes ``WebSocketClient`` instances to your route.


``flask_uwsgi_websocket.WebSocketClient``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Exposes the `uWSGI WebSocket API
<http://uwsgi-docs.readthedocs.org/en/latest/WebSockets.html#api>`_.

``recv()`` (alias ``WebSocket.receive()``)

``recv_nb()``

``send(msg)``

``send_binary(msg)``

``recv_nb()``

``send_from_sharedarea(id, pos)``

``send_binary_from_sharedarea(id, pos)``


``flask_uwsgi_websocket.GeventWebSocket``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Fancier WebSocket abstraction that takes advantage of Gevent loop engine.
Requires uWSGI to be run with ``--uwsgi`` option.


``flask_uwsgi_websocket.GeventWebSocketMiddleware``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Automatically performs WebSocket handshake and passes a ``GeventWebSocketClient`` instance to your route.


``flask_uwsgi_websocket.GeventWebSocketClient``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
WebSocket client abstraction with fully non-blocking methods.

``receive()``

``send(msg)``

``close()``

``connected``


Advanced Usage
--------------
Normally websocket routes happen outside of the normal request context. You can
get a request context in your websocket handler by using
``app.request_context``::

    app = Flask(__name__)
    ws = GeventWebSocket(app)

    @ws.route('/websocket')
    def websocket(ws):
        with app.request_context(ws.environ):
            print request.args
