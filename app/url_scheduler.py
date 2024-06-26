from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from app.database import models
from app.database.postgres import SessionLocal
from app.database.redis import redis_client


def delete_expired_urls():
    db = SessionLocal()
    try:
        now = datetime.now()
        db.query(models.URL).filter(models.URL.expires_at <= now).delete()
        db.commit()
        print(f"Expired URLs deleted at {now}")
    except Exception as e:
        print(f"An error occurred while deleting expired URLs: {e}")
    finally:
        db.close()


def sync_access_counts():
    db = SessionLocal()
    try:
        keys = redis_client.keys("count:*")
        for key in keys:
            short_key = key.split(":")[1]
            access_count = int(redis_client.get(key))
            db_url = db.query(models.URL).filter(models.URL.short_key == short_key).first()
            if db_url:
                db_url.access_count = access_count
                db.commit()
    except Exception as e:
        print(f"An error occurred while syncing access counts: {e}")
    finally:
        db.close()


def start_url_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_expired_urls, 'cron', hour=0, minute=0)  # 매일 자정에 실행
    scheduler.add_job(sync_access_counts, 'interval', minutes=5)  # 5분마다 Redis 카운트를 PostgreSQL에 반영
    scheduler.start()
    print("Scheduler started.")
