from alchemyapi import AlchemyAPI
alchemyapi = AlchemyAPI()
myText = "I love to get started with AlchemyAPI!"
response = alchemyapi.sentiment("text", myText)
print "Sentiment: ", response["docSentiment"]["type"]