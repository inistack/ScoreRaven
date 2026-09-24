from datetime import datetime, timezone
from app import db

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