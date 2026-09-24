from datetime import datetime, timedelta, timezone
from werkzeug.datastructures import ImmutableMultiDict
from app.celery_app import celery
from app import db
from app.models import Attempt, Dispatch
from app.services.scoring_service import submit_attempt


@celery.task
def expire_stale_dispatches():
    now = datetime.now(timezone.utc)
    stale = Dispatch.query.filter(Dispatch.status == 'invited', Dispatch.expires_at < now).all()

    for dispatch in stale:
        dispatch.status = 'expired_no_attempt'
    
    db.session.commit()

    return len(stale)


@celery.task
def auto_submit_expired_attempts():
    now = datetime.now(timezone.utc)
    in_progress = Attempt.query.filter_by(status='in_progress').all()

    submitted_count = 0

    for attempt in in_progress:
        deadline = attempt.started_at.replace(tzinfo=timezone.utc) + timedelta(
            seconds=attempt.dispatch.test.time_limit_seconds
        )
        if deadline < now:
            submit_attempt(attempt, ImmutableMultiDict([]))
            submitted_count += 1

    return submitted_count


@celery.task
def release_stale_claims():
    now = datetime.now(timezone.utc)
    claimed = Attempt.query.filter(
        Attempt.status == "pending_grading",
        Attempt.claimed_by.isnot(None),
    ).all()

    released_count = 0
    for attempt in claimed:
        timeout = timedelta(hours=attempt.dispatch.test.validity_hours)
        if attempt.claimed_at.replace(tzinfo=timezone.utc) + timeout < now:
            attempt.claimed_by = None
            attempt.claimed_at = None
            released_count += 1

    db.session.commit()
    return released_count