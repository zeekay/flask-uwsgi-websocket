#!/usr/bin/env python
from flask import Flask, render_template, request
from flask.ext.uwsgi_websocket import WebSocket

app = Flask(__name__)
ws = WebSocket(app)

@app.route('/')
def index():
    uri = '%s://%s/%s' % \
        (request.environ['wsgi.url_scheme'] == 'https' and 'wss' or 'ws', \
        request.headers['host'], 'websocket')
    return render_template('index.html', websocket_uri = uri)

@ws.route('/websocket')
def echo(ws):
    while True:
        msg = ws.receive()
        if msg is not None:
            ws.send(msg)
        else: return

if __name__ == '__main__':
    app.run(debug=True, threads=16)
