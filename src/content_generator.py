import google.generativeai as genai
import logging
import random
from config import GEMINI_API_KEY, HASHTAG_MAPPING

class ContentGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_gemini()
        
        self.tweet_styles = [
            "breaking_news",
            "analytical_insight", 
            "community_engagement",
            "educational_content",
            "market_analysis"
        ]
        
        self.emojis = {
            'bitcoin': ['🚀', '💰', '🎯', '🔥', '⚡', '₿'],
            'ethereum': ['🔷', '🌐', '💎', '✨', '⚙️'],
            'defi': ['🔄', '🏦', '💹', '📊'],
            'nft': ['🖼️', '🎨', '👾', '🔄'],
            'general': ['📈', '📊', '💡', '👀', '🎉', '💥']
        }

    def setup_gemini(self):
        """Setup Gemini AI"""
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            self.logger.info("✅ Gemini AI configured successfully")
        except Exception as e:
            self.logger.error(f"❌ Gemini setup failed: {e}")
            raise

    def create_high_quality_tweet(self, news_item):
        """Create high-quality, engaging tweet"""
        try:
            style = random.choice(self.tweet_styles)
            hashtags = self.generate_smart_hashtags(news_item)
            
            prompt = self.create_advanced_prompt(news_item, style, hashtags)
            
            response = self.model.generate_content(prompt)
            tweet_text = response.text.strip()
            
            # Clean and validate tweet
            tweet_text = self.clean_tweet(tweet_text)
            
            if not self.validate_tweet_quality(tweet_text):
                self.logger.warning("❌ Generated tweet failed quality check")
                return None
            
            self.logger.info("✅ High-quality tweet generated successfully")
            return tweet_text
            
        except Exception as e:
            self.logger.error(f"❌ Error generating tweet: {e}")
            return None

    def create_advanced_prompt(self, news_item, style, hashtags):
        """Create advanced prompt for high-quality content"""
        
        base_prompt = f"""
        Create a HIGH-QUALITY, ENGAGING Twitter post about this cryptocurrency news.
        The tweet should be professional, insightful, and highly engaging for crypto enthusiasts.
        
        NEWS INFORMATION:
        Title: {news_item.get('title', '')}
        Description: {news_item.get('description', '')}
        Source: {news_item.get('source', 'unknown')}
        
        STYLE: {style}
        MAX LENGTH: 275 characters (including hashtags)
        
        QUALITY REQUIREMENTS:
        1. Start with a compelling hook that grabs attention
        2. Provide valuable insight or analysis about the news
        3. Use appropriate crypto terminology and show expertise
        4. Include 2-3 relevant hashtags: {hashtags}
        5. Add 1-2 professional emojis that enhance the message
        6. End with a thought-provoking question or call-to-action when appropriate
        7. Sound authoritative but not robotic
        8. Focus on what this means for the crypto market/community
        
        STYLE GUIDELINES:
        - Breaking News: Urgent, timely, highlight importance
        - Analytical Insight: Deep analysis, market implications
        - Community Engagement: Conversational, ask questions
        - Educational Content: Informative, explain concepts
        - Market Analysis: Price implications, trading insights
        
        EXAMPLES OF EXCELLENT TWEETS:
        - "BREAKING: {news_item.get('title', 'Major crypto development')} just hit the market! This could significantly impact {random.choice(['BTC', 'ETH', 'DeFi'])} valuations. What's your take? 🚀 #CryptoNews #{random.choice(hashtags)}"
        - "Deep dive: {news_item.get('title', 'This development')} reveals interesting market dynamics. Here's why this matters for traders and investors... 📊 #CryptoAnalysis #Trading"
        
        Return ONLY the final tweet text, nothing else.
        """
        
        return base_prompt

    def generate_smart_hashtags(self, news_item):
        """Generate smart, relevant hashtags based on content"""
        content = (news_item.get('title', '') + ' ' + news_item.get('description', '')).lower()
        
        selected_hashtags = ['Crypto']  # Default
        
        # Topic-based hashtag selection
        for topic, tags in HASHTAG_MAPPING.items():
            if topic in content:
                selected_hashtags.extend(tags)
                break
        
        # Add source-specific hashtag
        source = news_item.get('source', '').title()
        if source:
            selected_hashtags.append(source)
        
        # Ensure uniqueness and limit
        unique_hashtags = list(set(selected_hashtags))
        return unique_hashtags[:3]

    def clean_tweet(self, tweet_text):
        """Clean and format tweet text"""
        # Remove quotes and extra spaces
        tweet_text = tweet_text.replace('"', '').replace("'", "")
        tweet_text = ' '.join(tweet_text.split())
        
        # Fix encoding issues
        tweet_text = tweet_text.encode('ascii', 'ignore').decode('ascii')
        
        return tweet_text.strip()

    def validate_tweet_quality(self, tweet_text):
        """Validate tweet meets quality standards"""
        if not tweet_text or len(tweet_text.strip()) < 20:
            return False
        
        if len(tweet_text) > 280:
            return False
        
        # Check for AI-sounding phrases
        ai_phrases = [
            'as an ai', 'according to the data', 'based on the analysis',
            'the model suggests', 'generated by', 'artificial intelligence'
        ]
        
        tweet_lower = tweet_text.lower()
        for phrase in ai_phrases:
            if phrase in tweet_lower:
                return False
        
        # Check for engagement elements
        has_hashtag = '#' in tweet_text
        reasonable_length = 50 <= len(tweet_text) <= 275
        
        return has_hashtag and reasonable_length
