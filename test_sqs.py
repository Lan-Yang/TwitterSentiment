import boto.sqs
from boto.sqs.message import Message
import cred_aws
import json

sqs = boto.sqs.connect_to_region(
        "us-east-1",
        aws_access_key_id=cred_aws.aws_access_key_id,
        aws_secret_access_key=cred_aws.aws_secret_access_key)

# print sqs.get_all_queues()
my_queue = sqs.get_queue('myqueue') or sqs.create_queue('myqueue')

for i in range(5):
    m = Message()
    payload = {
        'twit_id': i,
        'text': 'This is my %d-th message.' % i
    }
    m.set_body(json.dumps(payload))
    # print vars(m)
    my_queue.write(m)
    # print vars(m)
    # print m is rs
    # print rs.id  # request id

# need to wait a few seconds

ms = my_queue.get_messages(10)
for m in ms:
    print json.loads(m.get_body())
    # print m.id
    # print m.md5
    my_queue.delete_message(m)


# sqs.delete_queue(my_queue)
