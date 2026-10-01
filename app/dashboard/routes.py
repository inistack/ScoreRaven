from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import Test, Dispatch, Attempt

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

TESTS_PAGE_SIZE = 10


@dashboard_bp.route("/")
@login_required
def index():
    if current_user.role == "candidate":
        return redirect(url_for("candidate.my_tests"))
    if current_user.role == "grader":
        return redirect(url_for("grading.index"))

    page = request.args.get("page", 1, type=int)
    tests_pagination = (
        Test.query
        .order_by(Test.created_at.desc())
        .paginate(page=page, per_page=TESTS_PAGE_SIZE, error_out=False)
    )

    return render_template(
        "dashboard/admin_index.html",
        tests_pagination=tests_pagination,
        **admin_dashboard_stats(),
    )


def admin_dashboard_stats():
    return {
        "test_count": Test.query.count(),
        "active_dispatches": Dispatch.query.filter(
            Dispatch.status.in_(["invited", "started"])
        ).count(),
        "pending_grading_count": Attempt.query.filter_by(status="pending_grading").count(),
    }
