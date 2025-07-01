from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = BackgroundScheduler()

def start_scheduler():
    if not scheduler.running:
        scheduler.start()

def schedule_ingestion_job(ingest_func, interval_minutes=60):
    scheduler.add_job(
        ingest_func,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id="news_ingestion_job",
        replace_existing=True,
    ) 