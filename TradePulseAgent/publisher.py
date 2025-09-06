import logging
import tweepy
from config (
    TWITTER_API_KEY, TWITTER_API_SECRET_KEY, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
)

def publish_post(post):
    """
    Publishes a single post to Twitter.
    """
    if not post:
        logging.warning("Post is empty, skipping.")
        return

    print(f"--- Publishing Post ---\n{post}\n")

    if any(k.startswith("YOUR_TWITTER") for k in [TWITTER_API_KEY, TWITTER_API_SECRET_KEY, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
        logging.warning("Twitter credentials not set. Skipping post to Twitter.")
        return

    try:
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET_KEY,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )
        client.create_tweet(text=post)
        logging.info(f"Successfully posted to Twitter: {post}")
    except Exception as e:
        logging.error(f"Error posting to Twitter: {e}")