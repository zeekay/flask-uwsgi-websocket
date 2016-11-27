#!/usr/bin/env python
from collections import deque
from flask import Flask, render_template
from flask_uwsgi_websocket import GeventWebSocket

app = Flask(__name__)
ws = GeventWebSocket(app)

users = {}
backlog = deque(maxlen=10)

@app.route('/')
def index():
    return render_template('index.html')

@ws.route('/websocket')
def chat(ws):
    users[ws.id] = ws

    for msg in backlog:
        ws.send(msg)

    while True:
        msg = ws.receive()
        if msg is not None:
            backlog.append(msg)
            for id in users:
                if id != ws.id:
                    users[id].send(msg)
        else:
            break

    del users[ws.id]

if __name__ == '__main__':
    app.run(debug=True, gevent=100)
