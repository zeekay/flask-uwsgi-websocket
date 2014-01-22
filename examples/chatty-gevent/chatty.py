#!/usr/bin/env python
from flask import Flask, render_template
from flask.ext.uwsgi_websocket import GeventWebSocket
from gevent import sleep

app = Flask(__name__)
ws = GeventWebSocket(app)

@app.route('/')
def index():
    return render_template('index.html')

users = {}

@ws.route('/websocket')
def sender(ws):
    users[ws.id] = ws

    while True:
        for id in users:
            if id != ws.id:
                users[id].send('hi from ' + ws.id)
        sleep(3)

if __name__ == '__main__':
    app.run(debug=True, gevent=100)
