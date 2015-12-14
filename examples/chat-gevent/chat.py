#!/usr/bin/env python
from collections import deque
from flask import Flask, render_template, request
from flask.ext.uwsgi_websocket import GeventWebSocket

app = Flask(__name__)
ws = GeventWebSocket(app)

users = {}
backlog = deque(maxlen=10)

@app.route('/')
def index():
    uri = '%s://%s/%s' % \
        (request.environ['wsgi.url_scheme'] == 'https' and 'wss' or 'ws', \
        request.headers['host'], 'websocket')
    return render_template('index.html', websocket_uri = uri)


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
