import logging
import time
import random
from datetime import datetime
from .api_clients import APIClient
from .content_generator import ContentGenerator
from .twitter_manager import TwitterManager
from .database import DatabaseManager
from .news_manager import NewsManager

class CryptoBot:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.db = DatabaseManager()
        self.api_client = APIClient()
        self.content_gen = ContentGenerator()
        self.twitter = TwitterManager()
        self.news_manager = NewsManager()
        
        self.consecutive_failures = 0
        self.max_consecutive_failures = 5
        
        self.logger.info("✅ Crypto Bot initialized successfully")

    def run_single_cycle(self):
        """Run one complete bot cycle"""
        try:
            self.logger.info("🔄 Starting bot cycle...")
            
            # Step 1: Get news from random API
            news_data = self.get_news_with_fallback()
            if not news_data:
                self.handle_no_news()
                return False

            # Step 2: Filter and select best news
            selected_news = self.select_best_news(news_data)
            if not selected_news:
                self.logger.warning("📭 No suitable news after filtering")
                return False

            # Step 3: Check for duplicates
            if self.db.is_news_posted(selected_news['title']):
                self.logger.info("📝 News already posted, skipping...")
                return False

            # Step 4: Generate high-quality tweet
            tweet_content = self.content_gen.create_high_quality_tweet(selected_news)
            if not tweet_content:
                self.logger.error("❌ Failed to generate tweet content")
                return False

            # Step 5: Post to Twitter
            if self.twitter.post_tweet(tweet_content):
                self.db.mark_news_as_posted(
                    title=selected_news['title'],
                    url=selected_news.get('url', ''),
                    content=tweet_content,
                    source=selected_news.get('source', 'unknown')
                )
                self.consecutive_failures = 0
                self.logger.info("✅ Tweet posted successfully!")
                return True
            else:
                self.logger.error("❌ Failed to post tweet")
                return False

        except Exception as e:
            self.logger.error(f"❌ Error in bot cycle: {e}")
            self.consecutive_failures += 1
            return False

    def get_news_with_fallback(self):
        """Get news with fallback to other APIs if one fails"""
        news_data = self.api_client.get_random_news()
        
        if not news_data:
            # Try all APIs sequentially
            for source in ['coingecko', 'coinranking', 'coinpaprika']:
                self.logger.info(f"🔄 Trying fallback API: {source}")
                news_data = self.api_client.get_news_from_source(source)
                if news_data:
                    break
                time.sleep(1)  # Rate limiting
        
        return news_data

    def select_best_news(self, news_data):
        """Select the best news item based on quality score"""
        if not news_data:
            return None
            
        # Filter news
        filtered_news = self.news_manager.filter_news(news_data)
        if not filtered_news:
            return None
            
        # Sort by quality score and return the best one
        filtered_news.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
        return filtered_news[0]

    def handle_no_news(self):
        """Handle situation when no news is available"""
        self.consecutive_failures += 1
        self.logger.warning(f"🚫 No news available. Consecutive failures: {self.consecutive_failures}")
        
        if self.consecutive_failures >= self.max_consecutive_failures:
            self.logger.warning("🔄 Too many consecutive failures, taking a break...")
            time.sleep(300)  # 5 minutes break
            self.consecutive_failures = 0

    def test_all_apis(self):
        """Test all API connections"""
        results = {}
        
        # Test Twitter API
        try:
            twitter_ok = self.twitter.verify_credentials()
            results['twitter'] = 'connected' if twitter_ok else 'failed'
        except Exception as e:
            results['twitter'] = f'error: {str(e)}'
        
        # Test News APIs
        for source in ['coingecko', 'coinranking', 'coinpaprika']:
            try:
                news_data = self.api_client.get_news_from_source(source)
                results[source] = f'connected ({len(news_data) if news_data else 0} items)'
            except Exception as e:
                results[source] = f'error: {str(e)}'
        
        # Test Database
        try:
            stats = self.db.get_bot_stats()
            results['database'] = 'connected'
        except Exception as e:
            results['database'] = f'error: {str(e)}'
        
        return results
