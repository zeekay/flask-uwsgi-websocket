#!/usr/bin/env python
from flask import Flask, render_template
from flask.ext.uwsgi_websocket import WebSocket

app = Flask(__name__)
ws = WebSocket(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/oops')
def oops():
    raise Exception('oops')

@ws.route('/websocket')
def echo(ws):
    while True:
        msg = ws.receive()
        if not msg: return
        ws.send(msg)

if __name__ == '__main__':
    app.run(debug=True, threads=16)
