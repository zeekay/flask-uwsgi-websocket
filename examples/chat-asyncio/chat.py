#!/usr/bin/env python
from collections import deque
from flask import Flask, render_template
from flask.ext.uwsgi_websocket import AsyncioWebSocket
from asyncio import coroutine

app = Flask(__name__)
ws = AsyncioWebSocket(app)

users = {}
backlog = deque(maxlen=10)

@app.route('/')
def index():
    return render_template('index.html')

@ws.route('/websocket')
@coroutine
def chat(ws):
    users[ws.id] = ws

    for msg in backlog:
        yield from ws.send(msg)

    while True:
        msg = yield from ws.receive()
        if msg is not None:
            backlog.append(msg)
            for id in users:
                if id != ws.id:
                    yield from users[id].send(msg)
        else:
            break

    del users[ws.id]

if __name__ == '__main__':
    app.run(debug=True, asyncio=100, greenlet=True)
