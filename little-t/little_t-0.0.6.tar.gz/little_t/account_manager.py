import tweepy
from tweepy.streaming import json
from little_t import mongo_connector
from little_t.api_keys import TwitterKeys as TC
from little_t.text_generation import MarkovTweetGeneration
from little_t.mongo_reader import MongoReader
from little_t.mongo_writer import MongoWriter
from little_t.tweet_collector import TwitterAPIConnector
from little_t.data.User import TwitterUser
import little_t.text_generation
from bson import objectid


class LittleTAccount:
    def __init__(self) -> None:
        self.account = tweepy.Client(
            bearer_token=TC.get_BEARER_TOKEN(),
            consumer_key=TC.get_API_KEY(),
            consumer_secret=TC.get_API_KEY_SECRET(),
            access_token=TC.get_LITTLE_T_ACCESS_TOKEN(),
            access_token_secret=TC.get_LITTLE_T_ACCESS_TOKEN_SECRET(),
            wait_on_rate_limit=True,
        )

        self.auth = tweepy.OAuth1UserHandler(
            consumer_key=TC.get_API_KEY(),
            consumer_secret=TC.get_API_KEY_SECRET(),
            access_token=TC.get_LITTLE_T_ACCESS_TOKEN(),
            access_token_secret=TC.get_LITTLE_T_ACCESS_TOKEN_SECRET(),
        )
        self.id = 1511450491976241152
        self.username = "little_t_bot"
        self.API = tweepy.API(self.auth)
        self.collector = TwitterAPIConnector()

    def post_markov_tweet(self, target: TwitterUser, requester: TwitterUser):
        tweets = self.collector.get_tweets(user=target, repeat=True)
        generator = MarkovTweetGeneration(tweets, username=str(target.username))
        try:
            generator.generate_markov_model()
        except ValueError:
            self.API.send_direct_message(
                recipient_id=requester.twitter_id,
                text="Sorry User has too little tweets/text data to work with. User's with 50+ non-media (images, videos) tweets are normally suitable.",
            )
        markov_tweet = generator.make_tweet()
        if markov_tweet is None:
            return
        markov_tweet = markov_tweet + f"\n\nRequested by @{requester.username}"
        self.account.create_tweet(text=markov_tweet)

    def handle_dm_request(self, dm_event):

        message_details = dm_event["direct_message_events"][0]["message_create"]
        print(message_details)
        if len(message_details["message_data"]["entities"]["user_mentions"]) == 0:
            self.API.send_direct_message(
                recipient_id=requester_id,
                text="Unable to find mentioned user, sorry :(",
            )
        requester = self.collector.get_user(twitter_id=message_details["sender_id"])
        target = self.collector.get_user(
            twitter_id=message_details["message_data"]["entities"]["user_mentions"][0][
                "id"
            ]
        )
        if self.id in (target.twitter_id, requester.twitter_id):
            pass

        print(requester.username, requester.twitter_id)
        print(target.username, target.twitter_id)

        self.API.send_direct_message(
            recipient_id=requester.twitter_id,
            text=f"Found {target.username}, collecting data and compiling now.",
        )
        self.post_markov_tweet(target, requester)
        # self.post_markov_tweet(requester_id, target_details)


if __name__ == "__main__":
    little_t = LittleTAccount()
    print(little_t.API.verify_credentials().screen_name)
    connector = mongo_connector.MongoConnector()
    ret_doc = connector.account_collection.find_one(
        objectid.ObjectId("62fd686ec7ddfd51d983092f")
    )
    # ret_doc = connector.account_collection.find_one(
    #     objectid.ObjectId("62fd3f2c0fa012a6f3a80e06")
    # )
    # # print(ret_doc["tweet_create_events"][0])  #     # print(ret_doc)
    #
    little_t.handle_dm_request(ret_doc)
