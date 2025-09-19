"""
Loud Hawk v2 - Background Scheduler
Handles automatic RSS feed polling every 5 minutes
"""
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from ingest import run_harvest

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = AsyncIOScheduler()

async def scheduled_ingest():
    """Scheduled news harvest task"""
    try:
        logger.info("Starting scheduled news harvest...")
        
        # Run the comprehensive harvest process
        saved_count = run_harvest()
        
        if saved_count > 0:
            logger.info(f"Scheduled harvest completed: {saved_count} new articles saved")
        else:
            logger.warning("No new articles found in scheduled harvest")
        
    except Exception as e:
        logger.error(f"Error in scheduled harvest: {e}")

def start_scheduler():
    """Start the background scheduler"""
    try:
        # Add job to run every 5 minutes
        scheduler.add_job(
            scheduled_ingest,
            trigger=IntervalTrigger(minutes=5),
            id='news_ingestion',
            name='News Ingestion',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Background scheduler started - RSS feeds will be polled every 5 minutes")
        
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")

def stop_scheduler():
    """Stop the background scheduler"""
    try:
        scheduler.shutdown()
        logger.info("Background scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
