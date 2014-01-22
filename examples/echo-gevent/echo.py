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
        if msg is not None:
            ws.send(msg)
        else: return

if __name__ == '__main__':
    app.run(debug=True, gevent=100)
