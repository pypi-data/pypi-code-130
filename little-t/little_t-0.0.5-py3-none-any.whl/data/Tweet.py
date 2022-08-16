from mongoengine import *


class Tweet(Document):
    author_id = IntField(required=True)
    tweet_id = IntField(required=True)
    text = StringField(required=True)
