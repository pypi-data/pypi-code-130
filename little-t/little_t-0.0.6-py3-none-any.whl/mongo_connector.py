import pymongo
from little_t.api_keys import MongoKeys


class MongoConnector:
    """
    Simple class to hold the Database Info such as client to connect, the database, and collections.

    CONTAINS:
    user_collection ("UserAccounts")
    tweet_collection ("TweetDumps")
    account_collection ("AccountActivity")
    """

    def __init__(self) -> None:
        self.client = pymongo.MongoClient(
            f"mongodb+srv://little_t:{MongoKeys.get_cluster_password()}@clustertwitter.vd6bg.mongodb.net/ClusterTwitter?retryWrites=true&w=majority"
        )
        self.db = self.client["tweetDB"]
        self.user_collection = self.db["UserAccounts"]
        self.tweet_collection = self.db["TweetDumps"]
        self.account_collection = self.db["AccountActivity"]


if __name__ == "__main__":
    foo = MongoConnector()
    print(foo.client.list_database_names())
    # foo.tweet_collection.create_index([("tweet_id", 1)], unique=True)
    # foo.tokens_collection.create_index([("state", 1)], unique=True)
