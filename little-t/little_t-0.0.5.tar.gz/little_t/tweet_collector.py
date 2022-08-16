from typing import List
import tweepy
from tweepy.cursor import Cursor
import tweepy.errors
from little_t.api_keys import TwitterKeys

from little_t.data.Tweet import Tweet
from little_t.data.User import TwitterUser

# import mongo_database.MongoReader
class TwitterAPIConnector:
    def __init__(self) -> None:
        self.client = tweepy.Client(
            bearer_token=TwitterKeys.get_BEARER_TOKEN(), wait_on_rate_limit=True
        )

    def get_user(self, *, twitter_id=None, username=None) -> TwitterUser:
        if twitter_id is not None:
            try:
                response = self.client.get_user(id=twitter_id)
                user = TwitterUser()
                user.twitter_id = int(response.data["id"])
                user.username = response.data["username"]
                return user
            except tweepy.errors.BadRequest as twitter_error:
                raise twitter_error from tweepy.errors.BadRequest

        elif username is not None:
            try:
                if username[0] == "@":
                    username = username[1:]
                response = self.client.get_user(username=username)
                user = TwitterUser()
                user.twitter_id = int(response.data["id"])
                user.username = response.data["username"]
                return user
            except tweepy.errors.BadRequest as twitter_error:
                raise twitter_error from tweepy.errors.BadRequest
        else:
            raise TypeError("need Username or Twitter_Id!")

    def get_tweeets_paginator(self, *, twitter_id=None, username=None):
        if twitter_id is not None:
            user = self.get_user(twitter_id=twitter_id)
            if user is None:
                raise ValueError(f"Could not get {twitter_id}'s data")

        elif username is not None:
            user = self.get_user(username=username)
            if user is None:
                raise ValueError(f"Could not get {username}'s data")
        else:
            raise TypeError("ID or username is required")

        return tweepy.Paginator(
            self.client.get_users_tweets,
            user.data["id"],
            max_results=100,
            exclude=["retweets", "replies"],
        )

    def get_tweets(
        self, user: TwitterUser, amount: int = 5, repeat=False
    ) -> List[Tweet]:

        """
        Go through a given twitter user and using pagination (tweepy.pagination)
        collect the maximum amount of recent tweets using the timeline api
        """
        response_list = []
        if repeat:
            exclude = ["retweets", "replies"]
            for response in tweepy.Paginator(
                self.client.get_users_tweets,
                user.twitter_id,
                max_results=100,
                exclude=exclude,
            ).flatten():
                tweet = Tweet()
                tweet.author_id = user.twitter_id
                tweet.tweet_id = response.data["id"]
                tweet.text = response.data["text"]

                response_list.append(tweet)
            return response_list

        response = self.client.get_users_tweets(
            user.twitter_id, exclude=["replies", "retweets"], max_results=amount
        )
        tweet = Tweet()
        tweet.author_id = user.twitter_id
        tweet.tweet_id = response.data["id"]
        tweet.text = response.data["text"]

        response_list.append(tweet)
        return response_list


if __name__ == "__main__":
    # target = input("Give User: ")
    api = TwitterAPIConnector()
    TARGET = "@KusaAlexM"
    user = api.get_user(username=TARGET)
    page = api.get_tweeets_paginator(username=TARGET)
    foo = api.get_tweets(twitter_id=user.twitter_id, repeat=True)

    for tweet in page:
        print(tweet.data)
