from flask import Blueprint, render_template, flash, abort, redirect, url_for, request
from flask_login import current_user
from app.auth.decorators import roles_required
from app.models import Attempt, GradeHistory
from app import db
from datetime import datetime, timezone
from app.services.grading_service import apply_grades


grading_bp = Blueprint("grading", __name__, url_prefix="/grading")

@grading_bp.route("/")
@roles_required("admin", "grader")
def index():
    pending_count = Attempt.query.filter_by(status="pending_grading").count()
    my_claims_count = Attempt.query.filter_by(
        status="pending_grading", claimed_by=current_user.id
    ).count()
    return render_template(
        "grading/dashboard.html", pending_count=pending_count, my_claims_count=my_claims_count
    )

@grading_bp.route("/queue")
@roles_required('admin', 'grader')
def queue():
    unclaimed = (
        Attempt.query
        .filter_by(status='pending_grading', claimed_by=None)
        .order_by(Attempt.submitted_at.asc())
        .all()
    )

    my_claims = (
        Attempt.query
        .filter_by(status='pending_grading', claimed_by=current_user.id)
        .order_by(Attempt.submitted_at.asc())
        .all()
    )

    return render_template('grading/queue.html', unclaimed=unclaimed, my_claims=my_claims)


@grading_bp.route("/attempts/<int:attempt_id>/claim", methods=["POST"])
@roles_required("admin", "grader")
def claim_attempt(attempt_id):
    attempt = Attempt.query.get_or_404(attempt_id)

    if attempt.status != "pending_grading":
        flash("This attempt is not available for grading.", "error")
        return redirect(url_for("grading.queue"))
    
    if attempt.claimed_by is not None and attempt.claimed_by != current_user.id:
        flash("This attempt has already been claimed by another grader.", "error")
        return redirect(url_for("grading.queue"))
    
    attempt.claimed_by = current_user.id
    attempt.claimed_at = datetime.now(timezone.utc)
    db.session.commit()

    return redirect(url_for("grading.grade_attempt", attempt_id=attempt.id))


@grading_bp.route("/attempts/<int:attempt_id>/grade", methods=["GET", "POST"])
@roles_required("admin", "grader")
def grade_attempt(attempt_id):
    attempt = Attempt.query.get_or_404(attempt_id)

    if attempt.status != "pending_grading" or attempt.claimed_by != current_user.id:
        flash("This attempt is not available for grading.", "error")
        return redirect(url_for("grading.queue"))
    
    if request.method == "POST":
        still_pending = apply_grades(attempt, request.form, current_user.id)
        flash(
            "Grading saved — some answers still need grading." if still_pending else "Grading complete.",
            "success",
        )
        return redirect(url_for("grading.queue"))
    
    answers = sorted(attempt.answers, key=lambda a: a.question_id)

    return render_template("grading/grade_attempt.html", attempt=attempt, answers=answers)   


@grading_bp.route("/attempts/<int:attempt_id>/history")
@roles_required("admin", "grader")
def grade_history(attempt_id):
    attempt = Attempt.query.get_or_404(attempt_id)
    answer_ids = [a.id for a in attempt.answers]
    history = (
        GradeHistory.query
        .filter(GradeHistory.answer_id.in_(answer_ids))
        .order_by(GradeHistory.changed_at.desc())
        .all()
    )
    return render_template("grading/history.html", attempt=attempt, history=history)


@grading_bp.route("/history")
@roles_required("admin", "grader")
def all_history():
    history = (
        GradeHistory.query
        .order_by(GradeHistory.changed_at.desc())
        .limit(50)
        .all()
    )
    return render_template("grading/all_history.html", history=history)