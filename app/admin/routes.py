from app import db
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from app.models import Test, Dispatch, Question, Option
from app.auth.decorators import roles_required
from app.admin.forms import TestForm, QuestionForm, DispatchForm
from flask_login import current_user
from app.models.subject import Subject
from app.services.question_validation import validate_question_options, QuestionValidationError
from app.services.subject_service import get_or_create_subject
from app.services.dispatch_service import dispatch_test_to_emails
from app.services.csv_parsing import extract_emails_from_csv, CSVParseError
from app.services.test_lock import ensure_test_unlocked
from app.services.results_service import release_results, release_results_for_test



admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/tests/new', methods=['GET', 'POST'])
@roles_required('admin')
def new_test():
    form = TestForm()

    if form.validate_on_submit():
        if form.release_mode.data == "scheduled" and not form.scheduled_release_at.data:
            flash("Set a release date and time for a scheduled test.", "error")
            return render_template("admin/test_form.html", form=form, subjects=Subject.query.order_by(Subject.name).all())
        test = Test(
            title = form.title.data,
            subject = get_or_create_subject(form.subject_name.data),
            difficulty = form.difficulty.data,
            release_mode = form.release_mode.data,
            show_correct_answers=(
                form.show_correct_answers.data if form.difficulty.data == "basic" else False
            ),
            time_limit_seconds=form.time_limit_minutes.data * 60,
            validity_hours=form.validity_hours.data,
            created_by=current_user.id,
            scheduled_release_at=(
            form.scheduled_release_at.data if form.release_mode.data == "scheduled" else None),
        )
        db.session.add(test)
        db.session.commit()
        flash("Test created. Add questions before publishing.", "success")
        return redirect(url_for("admin.edit_test", test_id=test.id))
    
    return render_template("admin/test_form.html", form=form)


@admin_bp.route('/tests/<int:test_id>/edit', methods=['GET', 'POST'])
@roles_required('admin')
def edit_test(test_id):
    test = Test.query.get_or_404(test_id)

    if test.is_locked:
        flash("This test has been dispatched and can no longer be edited.", "error")
        return render_template("admin/test_locked.html", test=test)
    
    form = TestForm(obj=test)
    if request.method == "GET":
        form.subject_name.data = test.subject.name
        form.time_limit_minutes.data = test.time_limit_seconds // 60

    if form.validate_on_submit():
        if form.release_mode.data == "scheduled" and not form.scheduled_release_at.data:
            flash("Set a release date and time for a scheduled test.", "error")
            return render_template("admin/test_form.html", form=form, subjects=Subject.query.order_by(Subject.name).all())
        
        subject = get_or_create_subject(form.subject_name.data)
        test.title = form.title.data
        test.subject_id = subject.id
        test.difficulty = form.difficulty.data
        test.release_mode = form.release_mode.data
        test.show_correct_answers = (
            form.show_correct_answers.data if form.difficulty.data == "basic" else False
        )
        test.time_limit_seconds = form.time_limit_minutes.data * 60
        test.validity_hours = form.validity_hours.data
        test.scheduled_release_at = (form.scheduled_release_at.data if form.release_mode.data == "scheduled" else None)
        db.session.commit()
        flash("Test updated.", "success")
        return redirect(url_for("admin.edit_test", test_id=test.id))
    
    return render_template("admin/test_form.html", form=form, test=test)
        

@admin_bp.route('/tests/<int:test_id>/questions/new', methods=['GET', 'POST'])
@roles_required('admin')
def new_question(test_id):
    test = Test.query.get_or_404(test_id)

    locked_response = ensure_test_unlocked(test)
    if locked_response:
        return locked_response
    
    form = QuestionForm()

    if form.validate_on_submit():
        raw_options = [
            {"text": o.text.data.strip(), "is_correct": o.is_correct.data}
            for o in form.options
            if o.text.data and o.text.data.strip()
        ]

        try:
            validate_question_options(form.type.data, raw_options)
        except QuestionValidationError as e:
            flash(str(e), 'error')
            return render_template("admin/question_form.html", form=form, test=test)
        
        question = Question(
            test_id = test.id,
            type = form.type.data,
            prompt = form.prompt.data.strip(),
            points = form.points.data
        )
        db.session.add(question)
        db.session.flush()

        for i, opt in enumerate(raw_options):
            db.session.add(
                Option(
                    question_id=question.id,
                    text=opt['text'],
                    is_correct=opt['is_correct'],
                    display_order=i
                )
            )
        db.session.commit()
        flash('Question added.', 'success')
        return redirect(url_for("admin.edit_test", test_id=test.id))
    
    return render_template("admin/question_form.html", form=form, test=test)


@admin_bp.route('/tests/<int:test_id>/dispatch', methods=['GET', 'POST'])
@roles_required('admin')
def dispatch_test(test_id):
    test = Test.query.get_or_404(test_id)

    locked_response = ensure_test_unlocked(test)
    if locked_response:
        return locked_response

    if not test.questions:
        flash("Add at least one question before dispatching this test.", "error")
        return redirect(url_for("admin.edit_test", test_id=test.id))
    
    form = DispatchForm()

    if form.validate_on_submit():
        try:
            emails = extract_emails_from_csv(form.csv_file.data)
        except CSVParseError as e:
            flash(str(e), "error")
            return render_template("admin/dispatch_form.html", form=form, test=test)
        
        results = dispatch_test_to_emails(test, emails)
        test.published_at = test.published_at or db.func.now()
        test.is_locked = True
        db.session.commit()

        flash(
            f"Dispatched to {len(results[0]['dispatched'])} candidate(s). "
            f"{len(results[0]['skipped'])} skipped.",
            "success",
        )

        return redirect(url_for("admin.edit_test", test_id=test.id))
    
    return render_template("admin/dispatch_form.html", form=form, test=test)

        
@admin_bp.route("/tests/<int:test_id>/dispatches/<int:dispatch_id>/release", methods=["POST"])
@roles_required("admin")
def release_dispatch_results(test_id, dispatch_id):
    dispatch = Dispatch.query.get_or_404(dispatch_id)
    if dispatch.test_id != test_id:
        abort(404)

    try:
        release_results(dispatch)
        flash("Results released to candidate.", "success")
    except ValueError as e:
        flash(str(e), "error")

    return redirect(url_for("admin.edit_test", test_id=test_id))


@admin_bp.route("/tests/<int:test_id>/release-all", methods=["POST"])
@roles_required("admin")
def release_all_results(test_id):
    test = Test.query.get_or_404(test_id)
    count = release_results_for_test(test)
    flash(f"Released results to {count} candidate(s).", "success")
    return redirect(url_for("admin.edit_test", test_id=test_id))