import tweepy
import sys
import re
from word_list import words
import cred_twitter as twc
import boto.sqs
import cred_aws as aws
from application import db, Twit


sqs = boto.sqs.connect_to_region(
        "us-east-1",
        aws_access_key_id=aws.aws_access_key_id,
        aws_secret_access_key=aws.aws_secret_access_key)

def clean_old_records():
    clean_sql = '''
    DELETE FROM twit
    WHERE twit_id IN (
    SELECT twit_id FROM twit
    ORDER BY twit_id DESC OFFSET 1000
    );
    '''
    if Twit.query.count() <= 2000:
        return
    db.session.delete(Twit.query.order_by(Twit.twit_id).limit(1000))


class CustomStreamListener(tweepy.StreamListener):
    # splitter function
    splitter = re.compile(r'\W+')

    def on_status(self, status):
        if not status.coordinates:
            return
        longitude, latitude = status.coordinates['coordinates']
        text = status.text.encode('utf-8').lower()
        words = filter(bool, self.splitter.split(text))
        time = status.created_at
        text = ' '.join(words)
        # clean db
        clean_old_records()
        # add new twit to db
        twit = Twit(longitude=longitude, latitude=latitude, time=time, words=text)
        db.session.add(twit)
        db.session.commit()

    def on_error(self, status_code):
        print >> sys.stderr, 'Error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream


def main(socket):
    while True:
        try:
            auth = tweepy.OAuthHandler(twc.consumer_key, twc.consumer_secret)
            auth.set_access_token(twc.access_token, twc.access_token_secret)
            sapi = tweepy.streaming.Stream(auth, CustomStreamListener())
            sapi.filter(locations=[-130, -60, 70, 60], track=words)
        except KeyboardInterrupt:  # on Ctrl-C, break
            break
        except:
            pass
