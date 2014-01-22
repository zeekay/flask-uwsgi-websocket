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
            ws.send(message)

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


API
---
``flask_uwsgi_websocket.WebSocket``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Automatically performs WebSocket handshake for you, but otherwise only exposes
the `uWSGI WebSocket API
<http://uwsgi-docs.readthedocs.org/en/latest/WebSockets.html#api>`_.

``websocket.recv()`` (alias ``websocket.receive()``)

``websocket.recv_nb()``

``websocket.send(msg)``

``websocket.send_binary(msg)``

``websocket.recv_nb()``

``websocket.send_from_sharedarea(id, pos)``

``websocket.send_binary_from_sharedarea(id, pos)``

``flask_uwsgi_websocket.GeventWebSocket``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Fancier WebSocket abstraction that takes advantage of Gevent loop engine. Route
handlers are spawned in their own greenlets and able to easily send messages to
each other.

``websocket.receive()``

``websocket.send()``

``websocket.close()``

``websocket.connected``
