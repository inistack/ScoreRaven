from datetime import datetime, timezone
from app import db
from app.models import GradeHistory

def apply_grades(attempt, form_data, grader_id):
    written_answers = [a for a in attempt.answers if a.question.type == "written"]

    for answer in written_answers:
        is_correct_raw = form_data.get(f"correct_{answer.id}")
        points_raw = form_data.get(f"points_{answer.id}", "").strip()

        new_is_correct = is_correct_raw == "yes"
        new_points = int(points_raw) if points_raw.isdigit() else 0

        was_already_graded = answer.is_correct is not None
        changed = was_already_graded and (
            new_is_correct != answer.is_correct or new_points != answer.points_awarded
        )

        if changed:
            db.session.add(GradeHistory(
                answer_id=answer.id,
                previous_is_correct=answer.is_correct,
                previous_points=answer.points_awarded,
                new_is_correct=new_is_correct,
                new_points=new_points,
                changed_by=grader_id,
                changed_at=datetime.now(timezone.utc),
            ))

        answer.is_correct = new_is_correct
        answer.points_awarded = new_points
        answer.graded_by = grader_id
        answer.graded_at = datetime.now(timezone.utc)

    still_pending = any(a.is_correct is None for a in attempt.answers)

    if not still_pending:
        attempt.status = "graded"
        attempt.score = sum(a.points_awarded or 0 for a in attempt.answers)
        attempt.claimed_by = None
        attempt.claimed_at = None

    db.session.commit()
    return still_pending


