from gevent import monkey
monkey.patch_all()

from flask import Flask, jsonify, render_template, request, session
from flask.ext.socketio import SocketIO, emit
from flask.ext.sqlalchemy import SQLAlchemy
from threading import Thread
import cred_db
import sys
import os
from word_list import words
from functools import partial


# Flask app object
application = app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'adsf7678%*^&sdfg7wq'
app.config['SQLALCHEMY_DATABASE_URI'] = cred_db.SQLALCHEMY_DATABASE_URI
daemon = None

# Dabatase connection
db = SQLAlchemy(app)

class Twit(db.Model):
    twit_id = db.Column(db.Integer, primary_key=True)  # auto-inc
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    time = db.Column(db.DateTime)
    words = db.Column(db.String(256))

# db.drop_all()
# db.create_all()

# WebSocket
socketio = SocketIO(app)

# Twitter Stream API
import twit_daemon


@app.before_first_request
def init():
    global daemon
    if not daemon:
        bound_main = partial(f, 1)
        daemon = Thread(target=bound_main)
        daemon.start()

# main pages
@app.route('/')
def index():
    # load keywords
    payload = {'keywords': words}
    return render_template('index.html', api_data=payload)


@app.route('/data/<word>')
def search(word):
    result = []
    cur = Twit.query.order_by(Twit.twit_id.desc()).limit(500)
    for record in cur:
        if word == '-ALL-' or word in record.words.split():
            result.append({
                'longitude': record.longitude,
                'latitude': record.latitude
            })
    return jsonify(data=result)


# Error Handler
@app.errorhandler(404)
def not_found(error):
    return 'Page Not Found', 404


@app.errorhandler(500)
def internal_server_error(error):
    return 'Internal Server Error', 500

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000)
    socketio.run(app, host="0.0.0.0", port=5000)
