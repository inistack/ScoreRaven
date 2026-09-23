from datetime import datetime, timezone
from app import db
from app.models import Answer


def submit_attempt(attempt, form_data):
    attempt.submitted_at = datetime.now(timezone.utc)
    attempt.status = 'submitted'

    questions = attempt.dispatch.test.questions
    has_pending_written = False
    total_score = 0

    for question in questions:
        answer = Answer(attempt_id=attempt.id, question_id=question.id)

        if question.type == "written":
            answer.written_text = form_data.get(f"question_{question.id}", "").strip()
            answer.is_correct = None
            answer.points_awarded = None
            has_pending_written = True
        else:
            raw_ids = form_data.getlist(f"question_{question.id}")
            selected_ids = {int(i) for i in raw_ids if i.isdigit()}
            correct_ids = {o.id for o in question.options if o.is_correct}

            is_correct = selected_ids == correct_ids
            points_awarded = question.points if is_correct else 0

            answer.selected_option_ids = list(selected_ids)
            answer.is_correct = is_correct
            answer.points_awarded = points_awarded
            total_score += points_awarded
        
    db.session.add(answer)

    if has_pending_written:
        attempt.status = 'pending_review'
        attempt.score = None
    else:
        attempt.status = 'completed'
        attempt.score = total_score

    attempt.dispatch.status = 'completed'
    db.session.commit()
    
