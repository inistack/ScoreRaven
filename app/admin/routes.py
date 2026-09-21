from app import db
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import Test, Subject, test
from app.auth.decorators import roles_required
from app.admin.forms import TestForm
from flask_login import current_user

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/tests/new', methods=['GET', 'POST'])
@roles_required('admin')
def new_test():
    form = TestForm()
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.order_by(Subject.name).all()]

    if form.validate_on_submit():
        test = Test(
            title = form.title.data,
            subject = form.suject_id.data,
            difficulty = form.difficulty.data,
            release_mode = form.release_mode.data,
            show_correct_answers=(
                form.show_correct_answers.data if form.difficulty.data == "basic" else False
            ),
            time_limit_seconds=form.time_limit_minutes.data * 60,
            validity_hours=form.validity_hours.data,
            created_by=current_user.id
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
        return render_template('admin/test_locked.html', test=test)
    
    form = TestForm(obj=test)
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.order_by(Subject.name).all()]
    if request.method == "GET":
        form.time_limit_minutes.data = test.time_limit_seconds // 60

    if form.validate_on_submit():
        test.title = form.title.data
        test.subject_id = form.subject_id.data
        test.difficulty = form.difficulty.data
        test.release_mode = form.release_mode.data
        test.show_correct_answers = (
            form.show_correct_answers.data if form.difficulty.data == "basic" else False
        )
        test.time_limit_seconds = form.time_limit_minutes.data * 60
        test.validity_hours = form.validity_hours.data
        db.session.commit()
        flash("Test updated.", "success")
        return redirect(url_for("admin.edit_test", test_id=test.id))
    
    return render_template("admin/test_form.html", form=form, test=test)
        





