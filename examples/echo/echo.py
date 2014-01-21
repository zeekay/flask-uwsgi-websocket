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
        ws.send(msg)
