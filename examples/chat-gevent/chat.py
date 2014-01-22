#!/usr/bin/env python
from flask import Flask, render_template
from flask.ext.uwsgi_websocket import GeventWebSocket

app = Flask(__name__)
ws = GeventWebSocket(app)

users = {}

@app.route('/')
def index():
    return render_template('index.html')

@ws.route('/websocket')
def chat(ws):
    users[ws.id] = ws

    while True:
        msg = ws.receive()
        if msg is not None:
            for id in users:
                if id != ws.id:
                    users[id].send(msg)
        else:
            break

    del users[ws.id]

if __name__ == '__main__':
    app.run(debug=True, gevent=100)
