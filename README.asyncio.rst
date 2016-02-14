UWSGI_PROFILE
-------------
To make use of asyncio, it should be enabled at uwsgi compile time. If your
linux distribution has provided uwsgi with specific plugins, it should meet the
requirement. But if it lacks asyncio support, which is currently uwsgi's default
build profile, and/or you want to install uwsgi with pip and venv there would
be something tricky.
Currently(Jan, 2016), without specified configuration ``pip install uwsgi`` will
build a uwsgi without asyncio support. According to `uWSGI asyncio docs
<http://uwsgi-docs.readthedocs.org/en/latest/asyncio.html>`_, ``UWSGI_PROFILE``
and ``greenlet.h`` location should be specified. Here's the hack.

Prepare some system packages::

    # apt-get install build-essential python3-dev python3-venv

or something equivalent.
Prepare venv and greenlet::

    $ python3 -m venv pyvenv
    $ . pyvenv/bin/activate
    (pyvenv)$ pip install greenlet

Now, ``greenlet.h`` should be available at ``$VIRTUAL_ENV/include/site/python3.5``
or other python version while uwsgi's greenlet plugin includes ``<greenlet/greenlet.h>``.
As a compromise::

    $ mkdir -p $VIRTUAL_ENV/include/site/python3.5/greenlet
    $ ln -s ../greenlet.h $VIRTUAL_ENV/include/site/python3.5/greenlet/
    $ CFLAGS='-I$VIRTUAL_ENV/include/site/python3.5' UWSGI_PROFILE=asyncio pip install uwsgi

    
Install
-------
Until merged into master::

    $ pip install flask
    $ python setup.py install


Deployment
----------
Similar to other branch::

    $ uwsgi --master --http :5000 --http-websockets --asyncio 100 --greenlet --wsgi chat:app

...or::

    app.run(debug=True, asyncio=100, greenlet=True)

...with nginx::

    $ uwsgi --master --socket /tmp/uwsgi.sock --umask 000 --asyncio 100 --greenlet --wsgi chat:app

API
---
``flask_uwsgi_websocket.AsyncioWebSocket``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Fancier WebSocket abstraction that takes advantage of Asyncio loop engine.
Requires uWSGI to be run with ``--asyncio`` and ``--greenlet`` option.


``flask_uwsgi_websocket.AsyncioWebSocketMiddleware``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Automatically performs WebSocket handshake and passes a ``AsyncioWebSocketClient`` instance to your route.


``flask_uwsgi_websocket.AsyncioWebSocketClient``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
WebSocket client abstraction with asyncio coroutines.

``coroutine a_recv()`` (alias ``receive()``, ``recv()``)

``coroutine a_send(msg)`` (alias ``send()``)

``recv_nb()`` (should be useless)

``send_nb()`` (should be useless)

``close()``

``connected``
