#!/usr/bin/env python
from flask import Flask, render_template
from flask.ext.uwsgi_websocket import GeventWebSocket

app = Flask(__name__)
ws = GeventWebSocket(app)

@app.route('/')
def index():
    return render_template('index.html')

@ws.route('/websocket')
def echo(ws):
    while True:
        msg = ws.receive()
        if not msg: return
        ws.send(msg)

if __name__ == '__main__':
    from os import system
    system('uwsgi --http :8080 --http-websockets --master --gevent 100 -w echo:app')
