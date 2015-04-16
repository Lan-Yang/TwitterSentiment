'''
Simple server.
Usage: python server.py
'''


from application import application
from wsgiref.simple_server import make_server
from gevent.wsgi import WSGIServer

PORT = 80

httpd = WSGIServer(('', PORT), application)
# httpd = make_server('', PORT, application)
print "Serving HTTP on port %s..." % PORT

httpd.serve_forever()
