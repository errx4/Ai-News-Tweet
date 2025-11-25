import requests
import random
import logging
from config import RAPIDAPI_KEY, NEWS_SOURCES, REQUEST_TIMEOUT

class APIClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rapidapi_key = RAPIDAPI_KEY
        
        self.api_configs = {
            'coingecko': {
                'url': 'https://coingecko.p.rapidapi.com/news',
                'headers': {
                    'X-RapidAPI-Key': self.rapidapi_key,
                    'X-RapidAPI-Host': 'coingecko.p.rapidapi.com'
                }
            },
            'coinranking': {
                'url': 'https://coinranking1.p.rapidapi.com/news',
                'headers': {
                    'X-RapidAPI-Key': self.rapidapi_key,
                    'X-RapidAPI-Host': 'coinranking1.p.rapidapi.com'
                }
            },
            'coinpaprika': {
                'url': 'https://coinpaprika1.p.rapidapi.com/news',
                'headers': {
                    'X-RapidAPI-Key': self.rapidapi_key,
                    'X-RapidAPI-Host': 'coinpaprika1.p.rapidapi.com'
                }
            }
        }

    def get_random_news(self):
        """Get news from random API source"""
        selected_source = random.choice(NEWS_SOURCES)
        self.logger.info(f"🎲 Selected news source: {selected_source}")
        return self.get_news_from_source(selected_source)

    def get_news_from_source(self, source):
        """Get news from specific source"""
        try:
            if source not in self.api_configs:
                self.logger.error(f"❌ Unknown news source: {source}")
                return None
            
            config = self.api_configs[source]
            response = requests.get(
                config['url'],
                headers=config['headers'],
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                news_items = self.parse_news_response(data, source)
                self.logger.info(f"✅ Successfully fetched {len(news_items)} items from {source}")
                return news_items
            else:
                self.logger.error(f"❌ API Error {source}: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            self.logger.error(f"⏰ Timeout while fetching from {source}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Exception in {source}: {e}")
            return None

    def parse_news_response(self, data, source):
        """Parse API response based on source"""
        news_items = []
        
        try:
            if source == 'coingecko':
                articles = data.get('data', {}).get('news', [])
                for article in articles[:10]:  # Get top 10
                    if self.is_valid_article(article):
                        news_items.append({
                            'title': article.get('title', '').strip(),
                            'description': article.get('description', '').strip(),
                            'url': article.get('url', ''),
                            'published_at': article.get('created_at', ''),
                            'source': source,
                            'author': article.get('author', '')
                        })
                        
            elif source == 'coinranking':
                articles = data.get('data', {}).get('news', [])
                for article in articles[:10]:
                    if self.is_valid_article(article):
                        news_items.append({
                            'title': article.get('title', '').strip(),
                            'description': article.get('description', '').strip(),
                            'url': article.get('url', ''),
                            'published_at': article.get('published_at', ''),
                            'source': source,
                            'author': article.get('author', '')
                        })
                        
            elif source == 'coinpaprika':
                articles = data[:10]  # CoinPaprika returns list directly
                for article in articles:
                    if self.is_valid_article(article):
                        news_items.append({
                            'title': article.get('title', '').strip(),
                            'description': article.get('description', '').strip(),
                            'url': article.get('url', ''),
                            'published_at': article.get('date', ''),
                            'source': source,
                            'author': article.get('author', '')
                        })
            
            return news_items
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing {source} response: {e}")
            return []

    def is_valid_article(self, article):
        """Validate article has minimum required data"""
        title = article.get('title', '').strip()
        description = article.get('description', '').strip()
        
        return (
            len(title) >= 10 and 
            len(description) >= 20 and
            article.get('url')
          )
