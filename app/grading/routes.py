from flask import Blueprint, render_template
from flask_login import current_user
from app.auth.decorators import roles_required
from app.models import Attempt

grading_bp = Blueprint("grading", __name__, url_prefix="/grading")

