from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_token(email, salt):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=salt)

def verify_token(token, salt, max_age_seconds=86400):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=salt, max_age=max_age_seconds)
    except Exception:
        return None
    return email


