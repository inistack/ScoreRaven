from datetime import datetime, timezone
from app import db

def apply_grades(attempt, form_data, grader_id):
    written_answers = [a for a in attempt.answers if a.question.type == "written"]

    for answer in written_answers:
        is_correct_raw = form_data.get(f"correct_{answer.id}")
        points_raw = form_data.get(f"points_{answer.id}", "").strip()

        answer.is_correct = is_correct_raw == "yes"
        answer.points_awarded = int(points_raw) if points_raw.isdigit() else 0
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


