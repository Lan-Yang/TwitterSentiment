from gevent import monkey
monkey.patch_all()

import tweepy
from flask import Flask, jsonify, render_template, request, session
from flask.ext.socketio import SocketIO, emit
from flask.ext.sqlalchemy import SQLAlchemy
from threading import Thread
import cred_db
import sys
import os
from word_list import words
import cred_twitter as twc
import cred_aws
import boto.sqs, boto.sns
from boto.sqs.message import Message
import json
import time
import logging

FORMAT = r'%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format=FORMAT)


sqs = boto.sqs.connect_to_region(
        "us-east-1",
        aws_access_key_id=cred_aws.aws_access_key_id,
        aws_secret_access_key=cred_aws.aws_secret_access_key)
my_queue = sqs.get_queue('myqueue') or sqs.create_queue('myqueue')

sns = boto.sns.connect_to_region(
        "us-east-1",
        aws_access_key_id=cred_aws.aws_access_key_id,
        aws_secret_access_key=cred_aws.aws_secret_access_key)
topicarn = r"arn:aws:sns:us-east-1:239028447426:twit-senti"

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
socket_count = 0

# Daemon
class CustomStreamListener(tweepy.StreamListener):
    # db_count = 0
    twit_count = 0
    flag_stop = False

    def fake_stop(self):
        self.flag_stop = True

    def fake_start(self):
        self.flag_stop = False

    def on_status(self, status):
        if not status.coordinates:
            return True
        if self.flag_stop:
            return True

        # drop half twits
        self.twit_count += 1
        if self.twit_count % 2 == 0:
            return True

        # self.db_count += 1
        longitude, latitude = status.coordinates['coordinates']
        text = status.text#.encode('utf-8')
        # print type(status.text)
        time = status.created_at

        # Twit.query.delete()
        # db.session.commit()
        # return True
        # add new twit to db
        # self.db_count = 0
        # self.twit_count = 0
        twit = Twit(longitude=longitude, latitude=latitude, time=time, words=text)
        db.session.add(twit)
        db.session.commit()

        # add new twit to sqs
        m = Message()
        sqs_m = {
            'id': twit.twit_id,
            'content': text
        }
        m.set_body(json.dumps(sqs_m))
        my_queue.write(m)

        # emit new twit to client
        socketio.emit('twit', {
            'text': text,
            'longitude': longitude,
            'latitude': latitude,
            'time': time,
            'id': twit.twit_id
            })

    def on_error(self, status_code):
        print >> sys.stderr, '[tweepy] Error with status code:', status_code
        if status_code == 420:
            time.sleep(60)
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, '[tweepy] Timeout...'
        return True # Don't kill the stream

    def on_disconnect(self, notice):
        print >> sys.stderr, '[tweepy] Disconnect: %s' % notice
        return True

# Twitter Stream API
listener = CustomStreamListener()

def get_tweet():
    while True:
        try:
            auth = tweepy.OAuthHandler(twc.consumer_key, twc.consumer_secret)
            auth.set_access_token(twc.access_token, twc.access_token_secret)
            sapi = tweepy.streaming.Stream(auth, listener)
            sapi.filter(locations=[-130, -60, 70, 60], track=words)
        except KeyboardInterrupt:  # on Ctrl-C, break
            break
        except BaseException as e:
            print e
            pass

def init():
    global daemon, listener
    listener.fake_start()
    if not daemon:
        daemon = Thread(target=get_tweet)
        logging.info("daemon start")
        daemon.start()

@app.before_first_request
def init_bf_req():
    init()

# main pages
@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect(data):
    # print 'connect', data
    global socket_count
    logging.info("connect")
    socket_count += 1
    init()

@socketio.on('disconnect')
def on_disconnect():
    logging.info("disconnect")
    global listener, socket_count
    socket_count -= 1
    if socket_count <= 0:
        listener.fake_stop()

@app.route('/sns', methods=['POST'])
def sns_endpoint():
    '''http://160.39.7.94:5000/sns'''
    data = json.loads(request.data)
    if data['Type'] == 'SubscriptionConfirmation':
        sns.confirm_subscription(topicarn, data['Token'])
    elif data['Type'] == 'Notification':
        msg = json.loads(data['Message'])
        socketio.emit('sentiment', {
            'id': msg['id'],
            'sentiment': msg['senti']
            })
    # print request.data
    return ""

# @app.route('/data/<word>')
# def search(word):
#     result = []
#     cur = Twit.query.order_by(Twit.twit_id.desc()).limit(500)
#     for record in cur:
#         if word == '-ALL-' or word in record.words.split():
#             result.append({
#                 'longitude': record.longitude,
#                 'latitude': record.latitude
#             })
#     return jsonify(data=result)


# Error Handler
@app.errorhandler(404)
def not_found(error):
    return 'Page Not Found', 404


@app.errorhandler(500)
def internal_server_error(error):
    return 'Internal Server Error', 500

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000)
    socketio.run(
        app, host="0.0.0.0", port=80,
        policy_server=False,
        transports=['websocket', 'xhr-polling', 'xhr-multipart'])
