from datetime import datetime, timedelta, timezone
from flask import Blueprint, abort, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app.auth.decorators import roles_required
from app.models import Dispatch, AttemptQuestion, Question
from app.services.attempt_service import start_or_resume_attempt, DispatchExpiredError, AttemptNotResumableError
from app.services.scoring_service import submit_attempt
from app.services.attempt_service import save_answer
from app.services.time_utils import as_utc
from app.services.results_service import is_result_released

candidate_bp = Blueprint('candidate', __name__, url_prefix='/candidate')

@candidate_bp.route('/tests')
@roles_required('candidate')
def my_tests():

    DONE_PAGE_SIZE = 10

    now = datetime.now(timezone.utc)

    outstanding_dispatches = (
        Dispatch.query
        .filter(Dispatch.candidate_id == current_user.id, Dispatch.status != "completed")
        .order_by(Dispatch.invited_at.desc())
        .all()
    )

    available, expired, in_progress = [], [], []

    for dispatch in outstanding_dispatches:
        
        if dispatch.attempt and dispatch.status == 'in_progress':
            in_progress.append(dispatch)
        elif dispatch.status == 'expired_no_attempt' and dispatch.status == "invited" and as_utc(dispatch.expires_at) < now:
            expired.append(dispatch)
        else:
            available.append(dispatch)
    
    done_page = request.args.get("done_page", 1, type=int)
    done_pagination = (
        Dispatch.query
        .filter(Dispatch.candidate_id == current_user.id, Dispatch.status == "completed")
        .order_by(Dispatch.invited_at.desc())
        .paginate(page=done_page, per_page=DONE_PAGE_SIZE, error_out=False)
    )
    
    return render_template(
        'candidate/my_tests.html', 
        available=available, expired=expired, in_progress=in_progress, done_pagination=done_pagination, is_result_released=is_result_released,
    )


@candidate_bp.route("/tests/<int:dispatch_id>/take")
@roles_required('candidate')
def take_test(dispatch_id):
    dispatch = Dispatch.query.get_or_404(dispatch_id)

    if dispatch.candidate_id != current_user.id:
        abort(403)
    
    try:
        attempt = start_or_resume_attempt(dispatch)
    except DispatchExpiredError as e:
        flash(str(e), "error")
        return redirect(url_for("candidate.my_tests"))
    except AttemptNotResumableError as e:
        flash(str(e), "error")
        return redirect(url_for("candidate.my_tests"))
    
    remaining_seconds = (
        as_utc(attempt.started_at)
        + timedelta(seconds=dispatch.test.time_limit_seconds)
        - datetime.now(timezone.utc)
    ).total_seconds()

    attempt_questions = (
        AttemptQuestion.query
        .filter_by(attempt_id=attempt.id)
        .order_by(AttemptQuestion.display_order)
        .all()
    )

    return render_template(
        'candidate/take_test.html',
        dispatch=dispatch,
        attempt=attempt,
        attempt_questions=attempt_questions,
        remaining_seconds=max(0, int(remaining_seconds)),
    )


@candidate_bp.route('/tests/<int:dispatch_id>/submit', methods=['POST'])
@roles_required('candidate')
def submit_test(dispatch_id):
    dispatch = Dispatch.query.get_or_404(dispatch_id)

    if dispatch.candidate_id != current_user.id:
        abort(403)

    attempt = dispatch.attempt
    if attempt is None or attempt.status != "in_progress":
        flash("This test is not available for submission.", "error")
        return redirect(url_for("candidate.my_tests"))

    submit_attempt(attempt, request.form)

    flash("Test submitted.", "success")
    return redirect(url_for("candidate.my_tests"))


@candidate_bp.route("/tests/<int:dispatch_id>/autosave", methods=["POST"])
@roles_required("candidate")
def autosave(dispatch_id):
    dispatch = Dispatch.query.get_or_404(dispatch_id)

    if dispatch.candidate_id != current_user.id:
        abort(403)
    
    attempt = dispatch.attempt
    if attempt is None or attempt.status != 'in_progress':
        return jsonify({"error": "not available"}), 409

    data = request.get_json(silent=True) or {}
    question = Question.query.get_or_404(data.get("question_id"))

    if question.test_id != dispatch.test_id:
        abort(400)
    
    save_answer(
        attempt, question,
        selected_option_ids=data.get("selected_option_ids"),
        written_text=data.get("written_text"),
    )
    return jsonify({"status": "ok"})


@candidate_bp.route("/tests/<int:dispatch_id>/results")
@roles_required("candidate")
def view_results(dispatch_id):
    dispatch = Dispatch.query.get_or_404(dispatch_id)
    if dispatch.candidate_id != current_user.id:
        abort(403)

    if not is_result_released(dispatch):
        flash("Results for this test aren't available yet.", "info")
        return redirect(url_for("candidate.my_tests"))

    attempt = dispatch.attempt
    answers = {a.question_id: a for a in attempt.answers}
    questions = dispatch.test.questions

    return render_template(
        "candidate/results.html",
        dispatch=dispatch, attempt=attempt, questions=questions, answers=answers,
    )