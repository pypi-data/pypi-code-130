from typing import Optional, List
from wj_social_net_queries.controllers.twitter_controller import fetch_terms_tweets

class Twitter():
    """
    Description
    ----------
    Allows the use of functions related with Twitter platform
    
    """


    def __init__(
        self,
        twitter_consumer_key: str,
        twitter_consumer_secret: str,
        twitter_key: str,
        twitter_secret: str
    ):
        self.twitter_consumer_key = twitter_consumer_key
        self.twitter_consumer_secret = twitter_consumer_secret
        self.twitter_key = twitter_key
        self.twitter_secret = twitter_secret
    
    def fetch_terms_tweets(
        self,
        terms: List[str],
        max_tweets_per_term: Optional[int] = 20
    ):
        tweets, terms_updated = fetch_terms_tweets(
            terms=terms,
            twitter_consumer_key=self.twitter_consumer_key,
            twitter_consumer_secret=self.twitter_consumer_secret,
            twitter_key=self.twitter_key,
            twitter_secret=self.twitter_secret,
            max_tweets_per_term=max_tweets_per_term
        )
        return tweets, terms_updated
