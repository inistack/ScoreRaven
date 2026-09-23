import random
from app import db
from datetime import datetime, timezone
from app.models import Attempt, AttemptQuestion


class DispatchExpiredError(Exception):
    pass

class AttemptNotResumableError(Exception):
    pass

def start_or_resume_attempt(dispatch):
    now = datetime.now(timezone.utc)

    if dispatch.attempt:
        if dispatch.attempt.status == 'in_progress':
            return dispatch.attempt
        raise AttemptNotResumableError("This test has already been submitted.")
    
    if dispatch.expires_at < now:
        dispatch.status = 'expired_no_attempt'
        db.session.commit()
        raise DispatchExpiredError("This test's validity window has expired.")

    attempt = Attempt(dispatch_id=dispatch.id, started_at=now, status="in_progress")
    db.session.add(attempt)
    db.session.flush()

    questions = list(dispatch.test.questions)
    random.shuffle(questions)

    for order, question in enumerate(questions):
        attempt_question= AttemptQuestion(
            attempt_id=attempt.id,
            question_id=question.id,
            display_order=order,
        )
        db.session.add(attempt_question)

    dispatch.status = "started"
    db.session.commit()

    return attempt