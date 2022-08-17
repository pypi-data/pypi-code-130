from typing import List
import markovify
import re
import emoji
from requests import request
from tweepy.api import sys
from little_t.data.Tweet import Tweet
from little_t.data.User import TwitterUser
from little_t.tweet_collector import TwitterAPIConnector
from little_t.mongo_reader import MongoReader
from little_t.mongo_writer import MongoWriter


class MarkovTweetGeneration:
    def __init__(self, tweets: List[Tweet], username: str) -> None:
        self.username = username

        # modified in _text_preperation
        self.tweets = tweets
        self.required_tweet_amount = 50
        self.average_tweet_length = 0

        # generated in make generate_markov_model
        self.markov_model = None

        self.buildable = False
        if len(self.tweets) >= self.required_tweet_amount:
            self.buildable = True

    def _text_preperation(self):
        text_blob = ""
        sentence_finishers = [".", "?", "!"]
        for tweet in self.tweets:
            # have to wrap as string class because the ClassString from MongoDB throws errors :(
            text = str(tweet.text)

            # replace http(s)
            if re.search(r"http?s://t.co/\w{4,10}", text):
                text = re.sub(r"http?s://t.co/\w{4,10}", "", text)
                text = text[: len(text) - 1]

            # BEGONE EMOJIS
            text = emoji.replace_emoji(text, "")
            text = re.sub(r"@", "", text)

            #
            if len(text) == 1 or len(text) == 0:
                continue

            # occasional sentence will start with a blank, so add a '.' to close
            if text[-1] not in sentence_finishers:
                text += "."
            text = text.capitalize()

            text_blob += text + " "
        if len(text_blob) == 0:
            raise ValueError("Too many media posts to generate text from")
        self.average_tweet_length = len(text_blob) // len(self.tweets)
        return text_blob

    def generate_markov_model(self):
        if self.buildable == False:
            raise ValueError(
                f"User does not have enough tweets {self.required_tweet_amount}"
            )
        text_corpus = self._text_preperation()
        self.markov_model = markovify.Text(input_text=text_corpus, well_formed=False)

    def make_tweet(self):
        if self.markov_model == None:
            raise ValueError("No Makrov Model generated from text yet")
        try:
            new_sentence = self.markov_model.make_short_sentence(
                min_chars=self.average_tweet_length - 20,
                max_chars=self.average_tweet_length + 20,
                tries=100,
            ).capitalize()
        # TooSmall
        except KeyError:
            return
        if new_sentence[0:2] == ". ":
            new_sentence = new_sentence[2:]
        return f"\"{new_sentence}\" - {self.username}"


if __name__ == "__main__":
    collected_tweets = []
    inputted_user = input("Twitter Handle (with or without @): ")
    collector = TwitterAPIConnector()
    reader = MongoReader()
    writer = MongoWriter()

    # Check if User Exists
    twitter_user_details = collector.get_user(username=inputted_user)
    try:
        mongo_user_details = reader.get_user_by_handle(
            str(twitter_user_details.username)
        )
    except ValueError:
        print("New User")
        # If they don't:
        # 1. Get User Info
        print("Collecting Twitter Details")
        # 2. Collect User Tweets
        print("Collecting User Tweets")
        collected_tweets = collector.get_tweets(twitter_user_details, repeat=True)
        print("Total Tweets: ", len(collected_tweets))
        # 3. Store User in DB

        print("Storing User")
        writer.insert_twitter_user(twitter_user_details)
        # 4. Store Tweets in DB
        print("Storing Tweets")
        writer.insert_new_tweets(collected_tweets)

        mongo_user_details = reader.get_user_by_handle(inputted_user)

    finally:
        print("Pulling Latest Tweets from DB")
        pulled_tweets = reader.get_tweets_by_twitter_id(mongo_user_details.twitter_id)
        print("Generating Model")
        try:
            model = MarkovTweetGeneration(
                pulled_tweets, str(mongo_user_details.username)
            )
            model.generate_markov_model()
        except ValueError as ve:
            print(f"!!!ERROR: {ve}!!!")
            sys.exit()
        print(f"average tweet length of: { model.average_tweet_length}")
        tweet = model.make_tweet()
        print("=" * len(tweet))
        print(tweet)
        print("=" * len(tweet))
        print(len(tweet))
