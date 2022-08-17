from mongoengine import Document, IntField, StringField, BinaryField


class TwitterUser(Document):
    twitter_id = IntField(required=True, unique=True)
    username = StringField(required=True, unique=True)
