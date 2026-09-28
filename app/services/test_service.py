from app import db
from app.models import Test, Question, Option

def duplicate_test(source, admin_id):
    release_mode = source.release_mode
    reset_schedule = release_mode == "scheduled"
    if reset_schedule:
        release_mode = "manual"

    copy = Test(
        title=f"Copy of {source.title}"[:255],
        subject_id=source.subject_id,
        difficulty=source.difficulty,
        time_limit_seconds=source.time_limit_seconds,
        validity_hours=source.validity_hours,
        release_mode=release_mode,
        show_correct_answers=source.show_correct_answers,
        created_by=admin_id,
    )
    db.session.add(copy)
    db.session.flush()

    for question in sorted(source.questions, key=lambda q: q.id):
        new_question = Question(
            test_id=copy.id,
            type=question.type,
            prompt=question.prompt,
            points=question.points,
        )
        db.session.add(new_question)
        db.session.flush()

        for option in sorted(question.options, key=lambda o: o.display_order):
            db.session.add(Option(
                question_id=new_question.id,
                text=option.text,
                is_correct=option.is_correct,
                display_order=option.display_order,
            ))

    db.session.commit()
    return copy, reset_schedule