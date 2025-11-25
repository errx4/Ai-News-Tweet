import logging
import os
from datetime import datetime, timedelta
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

class DatabaseManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = self.setup_supabase()
        
    def setup_supabase(self):
        """Initialize Supabase client"""
        try:
            if not SUPABASE_URL or not SUPABASE_KEY:
                raise ValueError("Supabase URL and Key must be set in environment variables")
            
            client = create_client(SUPABASE_URL, SUPABASE_KEY)
            
            # Test connection
            test_response = client.table('posted_news').select('count', count='exact').limit(1).execute()
            self.logger.info("✅ Supabase connection established successfully")
            return client
            
        except Exception as e:
            self.logger.error(f"❌ Supabase connection failed: {e}")
            raise

    def is_news_posted(self, title):
        """Check if news has been posted before"""
        try:
            response = self.client.table('posted_news')\
                .select('id')\
                .eq('title', title)\
                .execute()
            
            exists = len(response.data) > 0
            
            if exists:
                self.logger.debug(f"📌 News already in database: {title[:50]}...")
            else:
                self.logger.debug(f"🆕 New news found: {title[:50]}...")
                
            return exists
            
        except Exception as e:
            self.logger.error(f"❌ Error checking news in Supabase: {e}")
            return False

    def mark_news_as_posted(self, title, url, content, source):
        """Mark news as posted in Supabase"""
        try:
            data = {
                'title': title,
                'url': url,
                'content': content,
                'source': source,
                'posted_at': datetime.now().isoformat()
            }
            
            response = self.client.table('posted_news').insert(data).execute()
            
            if response.data:
                self.logger.info(f"✅ News marked as posted in Supabase: {title[:50]}...")
                return True
            else:
                self.logger.error(f"❌ Failed to insert news into Supabase: {response.error}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error marking news in Supabase: {e}")
            return False

    def get_bot_stats(self):
        """Get comprehensive bot statistics from Supabase"""
        try:
            # Total posts count
            total_response = self.client.table('posted_news')\
                .select('id', count='exact')\
                .execute()
            total_posts = total_response.count

            # Today's posts count
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_response = self.client.table('posted_news')\
                .select('id', count='exact')\
                .gte('posted_at', today_start.isoformat())\
                .execute()
            today_posts = today_response.count

            # Last 24 hours posts count
            last_24h = datetime.now() - timedelta(hours=24)
            last_24h_response = self.client.table('posted_news')\
                .select('id', count='exact')\
                .gte('posted_at', last_24h.isoformat())\
                .execute()
            last_24h_posts = last_24h_response.count

            # Source distribution
            source_response = self.client.table('posted_news')\
                .select('source')\
                .execute()
            
            source_stats = {}
            for item in source_response.data:
                source = item['source']
                source_stats[source] = source_stats.get(source, 0) + 1

            # Success rate calculation (based on 5-minute intervals)
            success_rate = (last_24h_posts / 24) * 100 if last_24h_posts > 0 else 0

            return {
                'total_posts': total_posts,
                'today_posts': today_posts,
                'last_24h_posts': last_24h_posts,
                'success_rate': min(success_rate, 100),
                'source_stats': source_stats,
                'database': 'supabase'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting bot stats from Supabase: {e}")
            return {
                'total_posts': 0, 
                'today_posts': 0, 
                'last_24h_posts': 0,
                'success_rate': 0,
                'source_stats': {},
                'database': 'error'
            }

    def get_recent_posts(self, limit=10):
        """Get recent posts from Supabase"""
        try:
            response = self.client.table('posted_news')\
                .select('*')\
                .order('posted_at', desc=True)\
                .limit(limit)\
                .execute()
            
            posts = []
            for item in response.data:
                posts.append({
                    'title': item.get('title'),
                    'source': item.get('source'),
                    'posted_at': item.get('posted_at'),
                    'content': item.get('content'),
                    'url': item.get('url')
                })
            
            return posts
            
        except Exception as e:
            self.logger.error(f"❌ Error getting recent posts from Supabase: {e}")
            return []

    def cleanup_old_records(self, days=30):
        """Cleanup old records from Supabase"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            response = self.client.table('posted_news')\
                .delete()\
                .lt('posted_at', cutoff_date.isoformat())\
                .execute()
            
            deleted_count = len(response.data) if response.data else 0
            self.logger.info(f"🧹 Cleaned up {deleted_count} records older than {days} days from Supabase")
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up old records in Supabase: {e}")
            return 0

    def health_check(self):
        """Check Supabase connection health"""
        try:
            response = self.client.table('posted_news')\
                .select('id')\
                .limit(1)\
                .execute()
            
            return {
                'status': 'healthy',
                'database': 'supabase',
                'table_access': True
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'database': 'supabase', 
                'error': str(e)
            }
