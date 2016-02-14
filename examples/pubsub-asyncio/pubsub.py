#!/usr/bin/env python3
from collections import deque
from flask import Flask, render_template, Blueprint
from flask.ext.uwsgi_websocket import AsyncioWebSocket
import asyncio
import asyncio_redis

app = Flask(__name__)
wschat = Blueprint('wsBlueprint', __name__)
ws = AsyncioWebSocket(app)

@app.route('/')
def index():
    return render_template('index.html')

@wschat.route('/<string:channel>')
@asyncio.coroutine
def chat(ws, channel):
    yield from ws.send("Welcome to channel <{}>".format(channel))

    asyncio.get_event_loop().create_task(redis_subscribe(ws, channel))
    conn = yield from asyncio_redis.Connection.create()

    while True:
        msg = yield from ws.receive()
        if msg is not None:
            yield from conn.publish(channel, msg.decode('utf-8'))
        else:
            break

ws.register_blueprint(wschat, url_prefix='/websocket')

@asyncio.coroutine
def redis_subscribe(ws, channel):
    conn = yield from asyncio_redis.Connection.create()
    sub = yield from conn.start_subscribe()
    yield from sub.subscribe([channel])
    while ws.connected:
        reply = yield from sub.next_published()
        yield from ws.send(reply.value.encode('utf-8'))

if __name__ == '__main__':
    app.run(debug=True, asyncio=100, greenlet=True)
