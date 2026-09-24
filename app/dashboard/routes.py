from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Test, Dispatch, Attempt

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    if current_user.role == "candidate":
        return redirect(url_for("candidate.my_tests"))
    if current_user.role == "grader":
        return redirect(url_for("grading.index"))
    return render_template("dashboard/admin_index.html", **admin_dashboard_data())

def admin_dashboard_data():
    return {
        "test_count": Test.query.count(),
        "active_dispatches": Dispatch.query.filter(
            Dispatch.status.in_(["invited", "started"])
        ).count(),
        "pending_grading_count": Attempt.query.filter_by(status="pending_grading").count(),
        "recent_tests": Test.query.order_by(Test.created_at.desc()).limit(5).all(),
    }