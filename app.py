from flask import Flask, jsonify, request
import logging
import os
from datetime import datetime
from src.bot import CryptoBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Initialize bot
bot = CryptoBot()

@app.route('/')
def home():
    """Home endpoint with bot status"""
    return jsonify({
        "status": "active",
        "service": "crypto-news-bot",
        "database": "supabase",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "run": "/run", 
            "stats": "/stats",
            "database": "/database/health"
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check Twitter API connection
        twitter_healthy = bot.twitter.verify_credentials()
        
        # Check Supabase connection
        db_health = bot.db.health_check()
        
        # Get basic stats
        stats = bot.db.get_bot_stats()
        
        return jsonify({
            "status": "healthy",
            "twitter_api": "connected" if twitter_healthy else "disconnected",
            "database": db_health,
            "statistics": {
                "total_posts": stats.get('total_posts', 0),
                "today_posts": stats.get('today_posts', 0)
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/database/health')
def database_health():
    """Database-specific health check"""
    try:
        health = bot.db.health_check()
        return jsonify(health)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/run', methods=['POST', 'GET'])
def run_bot():
    """Run the bot for one cycle"""
    try:
        logger.info("🚀 Starting bot cycle via API request...")
        
        success = bot.run_single_cycle()
        
        if success:
            logger.info("✅ Bot cycle completed successfully")
            return jsonify({
                "status": "success",
                "message": "Tweet posted successfully",
                "database": "supabase",
                "timestamp": datetime.now().isoformat()
            })
        else:
            logger.info("⏭️ Bot cycle skipped (no tweet posted)")
            return jsonify({
                "status": "skipped", 
                "message": "No tweet posted this cycle",
                "database": "supabase",
                "timestamp": datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"❌ Bot cycle failed: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "database": "supabase",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/stats')
def get_stats():
    """Get bot statistics"""
    try:
        stats = bot.db.get_bot_stats()
        recent_posts = bot.db.get_recent_posts(5)
        
        return jsonify({
            "database": "supabase",
            "statistics": stats,
            "recent_posts": recent_posts,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "database": "supabase"
        }), 500

@app.route('/cleanup', methods=['POST'])
def cleanup_old_data():
    """Cleanup old records (admin function)"""
    try:
        days = request.json.get('days', 30) if request.json else 30
        deleted_count = bot.db.cleanup_old_records(days)
        
        return jsonify({
            "status": "success",
            "message": f"Cleaned up {deleted_count} records older than {days} days",
            "database": "supabase"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
