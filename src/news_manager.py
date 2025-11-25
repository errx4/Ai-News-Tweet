import logging
import re
from config import MIN_NEWS_LENGTH

class NewsManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Important keywords for scoring
        self.important_keywords = {
            'bitcoin': 5,
            'ethereum': 4,
            'crypto': 3,
            'blockchain': 3,
            'defi': 4,
            'nft': 3,
            'web3': 4,
            'trading': 3,
            'market': 3,
            'price': 3,
            'bullish': 4,
            'bearish': 4,
            'regulation': 5,
            'sec': 5,
            'binance': 4,
            'coinbase': 4
        }
        
        self.spam_keywords = [
            'buy now', 'limited offer', 'sign up', 'click here',
            'discount', 'promotion', 'get rich', 'make money',
            'investment opportunity', 'free money'
        ]

    def filter_news(self, news_items):
        """Filter and score news items"""
        filtered_items = []
        
        for item in news_items:
            if self.is_valid_news(item):
                # Calculate quality score
                item['quality_score'] = self.calculate_quality_score(item)
                filtered_items.append(item)
        
        self.logger.info(f"✅ Filtered {len(filtered_items)} valid news from {len(news_items)} items")
        return filtered_items

    def is_valid_news(self, news_item):
        """Validate news item"""
        title = news_item.get('title', '').strip()
        description = news_item.get('description', '').strip()
        
        # Basic validation
        if not title or len(title) < 10:
            return False
        
        if not description or len(description) < MIN_NEWS_LENGTH:
            return False
        
        # Spam check
        if self.contains_spam(title) or self.contains_spam(description):
            return False
        
        # Relevance check
        if not self.contains_important_topic(title + ' ' + description):
            return False
        
        return True

    def contains_spam(self, text):
        """Check for spam content"""
        text_lower = text.lower()
        return any(spam in text_lower for spam in self.spam_keywords)

    def contains_important_topic(self, text):
        """Check if text contains important topics"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.important_keywords.keys())

    def calculate_quality_score(self, news_item):
        """Calculate quality score for news item"""
        score = 0.0
        content = (news_item.get('title', '') + ' ' + news_item.get('description', '')).lower()
        
        # Keyword scoring
        for keyword, weight in self.important_keywords.items():
            if keyword in content:
                score += weight
        
        # Length scoring
        title_len = len(news_item.get('title', ''))
        desc_len = len(news_item.get('description', ''))
        
        if title_len > 30:
            score += 2.0
        if desc_len > 100:
            score += 3.0
        
        # Source reliability (you can expand this)
        source = news_item.get('source', '').lower()
        if source in ['coingecko', 'coinranking']:
            score += 2.0
        
        return score
