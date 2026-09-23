from datetime import datetime, timezone
from flask import Blueprint, render_template, request
from flask_login import current_user
from app.auth.decorators import roles_required
from app.models import Dispatch

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
        elif dispatch.status == 'expired_no_attempt' and dispatch.status == "invited" and dispatch.expires_at < now:
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
        available=available, expired=expired, in_progress=in_progress, done_pagination=done_pagination,
    )


