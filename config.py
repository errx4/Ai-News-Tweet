import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Bot Settings
POSTING_INTERVAL = 5  # minutes
MAX_RETRY_ATTEMPTS = 3
REQUEST_TIMEOUT = 15

# News Sources
NEWS_SOURCES = ['coingecko', 'coinranking', 'coinpaprika']

# Content Settings
MAX_TWEET_LENGTH = 280
MIN_NEWS_LENGTH = 50

# Hashtag Mapping
HASHTAG_MAPPING = {
    'bitcoin': ['Bitcoin', 'BTC', 'Crypto'],
    'ethereum': ['Ethereum', 'ETH', 'Crypto'],
    'defi': ['DeFi', 'Crypto'],
    'nft': ['NFT', 'Crypto'],
    'web3': ['Web3', 'Crypto'],
    'trading': ['Trading', 'Crypto'],
    'market': ['Market', 'Crypto'],
    'blockchain': ['Blockchain', 'Crypto'],
    'altcoin': ['Altcoin', 'Crypto']
}
