from datetime import datetime, timezone
from app import db
from app.models import Test

def is_result_released(dispatch):
    attempt = dispatch.attempt
    if attempt is None or attempt.status not in ("graded", "completed"):
        return False
    if dispatch.test.release_mode == "immediate":
        return True
    return dispatch.results_released_at is not None

def release_results(dispatch):
    attempt = dispatch.attempt
    if attempt is None or attempt.status not in ("graded", "completed"):
        raise ValueError("Cannot release results for an attempt that isn't graded yet.")

    dispatch.results_released_at = datetime.now(timezone.utc)
    db.session.commit()

def release_results_for_test(test):
    released_count = 0
    for dispatch in test.dispatches:
        attempt = dispatch.attempt
        if attempt and attempt.status in ("graded", "completed") and not dispatch.results_released_at:
            dispatch.results_released_at = datetime.now(timezone.utc)
            released_count += 1

    db.session.commit()
    return released_count

def release_due_scheduled_tests():
    now = datetime.now(timezone.utc)
    due_tests = Test.query.filter(
        Test.release_mode == "scheduled",
        Test.scheduled_release_at <= now,
    ).all()

    released_total = 0
    for test in due_tests:
        released_total += release_results_for_test(test)

    return released_total