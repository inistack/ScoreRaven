from datetime import datetime, timezone
from app import db
from app.models import Test
from flask import current_app


def is_result_released(dispatch):
    attempt = dispatch.attempt
    if attempt is None or attempt.status not in ("graded", "completed"):
        return False
    if dispatch.test.release_mode == "immediate":
        return True
    return dispatch.results_released_at is not None


def _stamp_release(dispatch):
    """Marks a dispatch as released. Returns True only the first time."""
    if dispatch.results_released_at is not None:
        return False
    dispatch.results_released_at = datetime.now(timezone.utc)
    return True


def notify_released(dispatch_ids):
    from app.tasks import send_results_released_email_task

    for dispatch_id in dispatch_ids:
        try:
            send_results_released_email_task.delay(dispatch_id)
        except Exception:
            current_app.logger.exception(
                "Could not queue results email for dispatch %s", dispatch_id
            )


def release_immediately_if_due(attempt):
    dispatch = attempt.dispatch
    if dispatch.test.release_mode != "immediate":
        return False
    if attempt.status not in ("graded", "completed"):
        return False
    return _stamp_release(dispatch)


def release_results(dispatch):
    attempt = dispatch.attempt
    if attempt is None or attempt.status not in ("graded", "completed"):
        raise ValueError("Cannot release results for an attempt that isn't graded yet.")

    if _stamp_release(dispatch):
        dispatch_id = dispatch.id
        db.session.commit()
        notify_released([dispatch_id])


def release_results_for_test(test):
    released_ids = []
    for dispatch in test.dispatches:
        attempt = dispatch.attempt
        if attempt and attempt.status in ("graded", "completed") and _stamp_release(dispatch):
            released_ids.append(dispatch.id)

    db.session.commit()
    notify_released(released_ids)
    return len(released_ids)


def release_due_scheduled_tests():
    now = datetime.now(timezone.utc)
    due_tests = Test.query.filter(
        Test.release_mode == "scheduled",
        Test.scheduled_release_at <= now,
    ).all()

    return sum(release_results_for_test(test) for test in due_tests)


def get_test_results_summary(test):
    dispatches = test.dispatches

    scored = [d.attempt.score for d in dispatches if d.attempt and d.attempt.score is not None]
    completed = sum(1 for d in dispatches if d.attempt and d.attempt.status in ("graded", "completed"))
    pending_grading = sum(1 for d in dispatches if d.attempt and d.attempt.status == "pending_grading")
    in_progress = sum(1 for d in dispatches if d.attempt and d.attempt.status == "in_progress")
    no_show = sum(1 for d in dispatches if d.status == "expired_no_attempt")
    released = sum(1 for d in dispatches if d.results_released_at is not None)
    total_points = sum(q.points for q in test.questions)

    return {
        "total_dispatched": len(dispatches),
        "completed": completed,
        "pending_grading": pending_grading,
        "in_progress": in_progress,
        "no_show": no_show,
        "released": released,
        "total_points": total_points,
        "average_score": round(sum(scored) / len(scored), 1) if scored else None,
    }