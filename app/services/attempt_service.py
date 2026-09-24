import random
from app import db
from datetime import datetime, timezone
from app.models import Attempt, AttemptQuestion, Answer
from app.services.time_utils import as_utc


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
    
    if as_utc(dispatch.expires_at) < now:
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


def save_answer(attempt, question, selected_option_ids=None, written_text=None):
    answer = Answer.query.filter_by(attempt_id=attempt.id, question_id=question.id).first()
    if answer is None:
        answer = Answer(attempt_id=attempt.id, question_id=question.id)
        db.session.add(answer)

    if question.type == "written":
        answer.written_text = written_text
    else:
        answer.selected_option_ids = selected_option_ids

    db.session.commit()
    return answer