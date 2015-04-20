# TwitterSentiment

This is the web/app server for a twitter sentiment analysis app.

## Framework
Server built with python flask framework. Weksocket is used for server-side
pushing. The whole app is built in Docker, for easier deployment on Elastic
Beanstalk.

## Twit Stream
A daemon thread runing with the server collects twits. Every twit is inserted
into database(Postgre on RDS), written to SQS, and pushed to all connected
clients.

## Twit Sentiment
Twit Sentiment are POSTed to /sns endpoint by SNS, and then pushed to all
connected clients.

## Client side
All twits are marked on google heat map in realtime, and the sentiment trend
are also updated in realtime.
