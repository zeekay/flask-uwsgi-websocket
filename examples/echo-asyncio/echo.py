#!/usr/bin/env python3
from flask import Flask, render_template
from flask.ext.uwsgi_websocket import AsyncioWebSocket
from asyncio import coroutine

app = Flask(__name__)
ws = AsyncioWebSocket(app)

@app.route('/')
def index():
    return render_template('index.html')

@ws.route('/websocket')
@coroutine
def echo(ws):
    while True:
        msg = yield from ws.receive()
        if msg is not None:
            yield from ws.send(msg)
        else: return

if __name__ == '__main__':
    app.run(debug=True, asyncio=100, greenlet=True)
