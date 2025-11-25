import tweepy
import logging
from config import (
    TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
)

class TwitterManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = self.setup_twitter()

    def setup_twitter(self):
        """Setup Twitter API client"""
        try:
            client = tweepy.Client(
                consumer_key=TWITTER_API_KEY,
                consumer_secret=TWITTER_API_SECRET,
                access_token=TWITTER_ACCESS_TOKEN,
                access_token_secret=TWITTER_ACCESS_SECRET
            )
            self.logger.info("✅ Twitter API configured successfully")
            return client
        except Exception as e:
            self.logger.error(f"❌ Twitter setup failed: {e}")
            raise

    def post_tweet(self, content):
        """Post tweet to Twitter"""
        try:
            response = self.client.create_tweet(text=content)
            tweet_id = response.data['id']
            self.logger.info(f"✅ Tweet posted successfully: {tweet_id}")
            return True
        except tweepy.TweepyException as e:
            self.logger.error(f"❌ Twitter API error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error posting tweet: {e}")
            return False

    def verify_credentials(self):
        """Verify Twitter credentials"""
        try:
            user = self.client.get_me()
            if user.data:
                self.logger.info("✅ Twitter credentials verified")
                return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Twitter credentials verification failed: {e}")
            return False
