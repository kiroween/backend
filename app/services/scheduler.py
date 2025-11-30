from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.services.tombstone_service import TombstoneService
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def unlock_tombstones_job():
    """Job to check and unlock tombstones whose unlock date has arrived"""
    db: Session = SessionLocal()
    try:
        service = TombstoneService(db)
        unlocked_count = service.check_and_unlock_tombstones()
        logger.info(f"Unlocked {unlocked_count} tombstones")
    except Exception as e:
        logger.error(f"Error unlocking tombstones: {e}")
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler"""
    # Run daily at midnight
    scheduler.add_job(
        unlock_tombstones_job,
        trigger=CronTrigger(hour=0, minute=0),
        id="unlock_tombstones",
        name="Check and unlock tombstones",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started")


def stop_scheduler():
    """Stop the background scheduler"""
    scheduler.shutdown()
    logger.info("Scheduler stopped")
