from typing import List
from little_t.mongo_connector import MongoConnector
from little_t.data.Tweet import Tweet
from little_t.data.User import TwitterUser


class MongoReader(MongoConnector):
    def __init__(self) -> None:
        super().__init__()

    def get_user_by_twitter_id(self, twitter_id: int) -> TwitterUser:

        cursor = self.user_collection.find_one({"twitter_id": twitter_id})
        if cursor is None:
            raise ValueError(f"No User Found of id {twitter_id}")
        user = TwitterUser()
        user.twitter_id = cursor["twitter_id"]
        user.username = cursor["username"]
        user.model = cursor.get("model", None)
        return user

    def get_user_by_handle(self, twitter_handle: str) -> TwitterUser:
        if twitter_handle[0] == "@":
            twitter_handle = twitter_handle[1:]
        cursor = self.user_collection.find_one({"username": twitter_handle})
        if cursor is None:
            raise ValueError(f"No User Found of name {twitter_handle}")
        user = TwitterUser()
        user.twitter_id = cursor["twitter_id"]
        user.username = cursor["username"]
        return user

    def get_tweets_by_twitter_id(self, twitter_id: int) -> List[Tweet]:
        tweets = []
        for mongo_tweet in self.tweet_collection.find({"author_id": twitter_id}):
            tweet = Tweet()
            tweet.author_id = mongo_tweet["author_id"]
            tweet.tweet_id = mongo_tweet["tweet_id"]
            tweet.text = mongo_tweet["text"]
            tweets.append(tweet)
        return tweets



if __name__ == "__main__":
    foo = MongoReader()
    me = foo.get_user_by_twitter_id(twitter_id=858911602053074944)
    # tweets_int = foo.get_tweets_by_author_id(858911602053074944)
    # tweets_str = foo.get_tweets_by_author_id("858911602053074944")

    print(me.to_json())
