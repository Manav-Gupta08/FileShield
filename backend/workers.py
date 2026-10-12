"""Celery orchestration with a separate killable parser process."""

import subprocess
import sys
import time

from celery import Celery
from sqlalchemy import delete, select, update

from backend.config import settings
from backend.database import Job, Session, SessionLocal
from backend.security import seal
from backend.storage import remove_job_files


celery_app = Celery("fileshield", broker=settings.redis_url or "memory://")
celery_app.conf.update(task_serializer="json", accept_content=["json"], result_serializer="json",
                       task_ignore_result=True, worker_prefetch_multiplier=1,
                       task_acks_late=False, task_reject_on_worker_lost=False,
                       broker_connection_retry_on_startup=True,
                       beat_schedule={"retention": {"task": "fileshield.cleanup", "schedule": 30.0}})


@celery_app.task(name="fileshield.process")
def process_job(identifier: str):
    with SessionLocal() as database:
        result = database.execute(update(Job).where(Job.id == identifier, Job.status == "queued", Job.expires > time.time()).values(status="processing"))
        database.commit()
        if result.rowcount != 1:
            return
    try:
        subprocess.run([sys.executable, "-m", "backend.runner", identifier], shell=False,
                       timeout=settings.process_timeout, check=True, stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.SubprocessError, OSError):
        with SessionLocal() as database:
            job = database.get(Job, identifier)
            if job:
                job.status, job.error, job.options = "failed", "Processing timed out or worker failed", seal({})
                database.commit()
        remove_job_files(identifier)


@celery_app.task(name="fileshield.cleanup")
def cleanup():
    with SessionLocal() as database:
        now = time.time()
        jobs = database.scalars(select(Job).where(Job.expires <= now)).all()
        for job in jobs:
            if job.status == "processing" and job.created + settings.process_timeout + 120 > now:
                continue
            remove_job_files(job.id)
            database.delete(job)
        database.execute(delete(Session).where(Session.expires <= now))
        database.commit()