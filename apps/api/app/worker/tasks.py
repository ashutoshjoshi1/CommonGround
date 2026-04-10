from __future__ import annotations

from datetime import UTC, datetime

import dramatiq
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Job, JobStatus, Source
from app.services.ingestion import process_source
from app.services.storage import get_storage
from app.worker.broker import redis_broker  # noqa: F401


@dramatiq.actor
def run_source_ingestion(job_id: str) -> None:
    db: Session = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return

        source = db.query(Source).filter(Source.id == job.source_id).first()
        if not source:
            job.status = JobStatus.FAILED
            job.last_error = "Source not found"
            db.commit()
            return

        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(UTC)
        job.attempts += 1
        db.commit()

        payload = get_storage().read_bytes(source.storage_key)
        process_source(db=db, source=source, payload=payload)

        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(UTC)
        job.result_json = {"source_id": source.id, "status": source.status.value}
        db.commit()
    except Exception as exc:  # pragma: no cover
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = JobStatus.FAILED
            job.last_error = str(exc)
            db.commit()
        raise
    finally:
        db.close()
