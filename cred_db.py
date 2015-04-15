'''Config'''
# DB connect string
hostname = 'testtest.cbk1saqhgyyf.us-east-1.rds.amazonaws.com'
dbname = 'twit'
user = 'postgres'
paswd = 'postgres'
SQLALCHEMY_DATABASE_URI = 'postgresql+pg8000://%s:%s@%s/%s' % (user, paswd, hostname, dbname)
