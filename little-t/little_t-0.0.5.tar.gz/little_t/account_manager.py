import tweepy
from little_t.api_keys import TwitterKeys as TC
import little_t.text_generation


class LittleTAccount():
    def __init__(self) -> None:
        self.account = tweepy.Client(
                bearer_token= TC.get_BEARER_TOKEN(),
                consumer_key=TC.get_API_KEY(),
                consumer_secret=TC.get_API_KEY_SECRET(),
                access_token=TC.get_ACCESS_TOKEN(),
                access_token_secret=TC.get_ACCESS_TOKEN_SECRET(),
                wait_on_rate_limit=True
                )
        self.id = 1511450491976241152
        self.username = "little_t_bot"
    


if __name__ == "__main__":
    little_t = LittleTAccount()
    # tweet_generator = text_generation.MarkovTweetGeneration()

    me_response = little_t.account.get_user(username="KusaAlexM")
    try:
        print(little_t.account.create_tweet(text="Still good!"))
        # little_t.client.create_tweet(text="I lived Bitch.")
    except Exception as e:
        print(e)
    finally:

