from functools import wraps
from flask import abort
from flask_login import current_user, login_required


def roles_required(*allowed_roles):
    def decorator(func):
        @wraps(func)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role not in allowed_roles:
                abort(403)
            return func(*args, **kwargs)
        return wrapped
    return decorator