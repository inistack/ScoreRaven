from datetime import timedelta, datetime, timezone
from app import db
from app.models import Dispatch, Test, User
from app.auth.token import generate_token
from app.emails.dispatch_emails import send_dispatch_invite_email, send_test_available_email

def find_or_create_candidate_by_email(email):
    email = email.strip().lower()
    user = User.query.filter(db.func.lower(User.email) == email).first()

    if user:
        if not user.is_verified:
            user.is_verified = True
        return user
    
    user = User(email=email, role="candidate", is_verified=True, has_password_set=False)
    db.session.add(user)
    db.session.flush()
    return user


def dispatch_test_to_email(test, email):
    candidate = find_or_create_candidate_by_email(email)

    dispatch = Dispatch(
        test_id = test.id,
        candidate_id = candidate.id,
        expires_at = datetime.now(timezone.utc) + timedelta(hours=test.validity_hours),
        status = "invited"
    )
    db.session.add(dispatch)
    db.session.flush()

    if not candidate.has_password_set:
        token = generate_token(candidate.email, salt='set-password')
        send_dispatch_invite_email(candidate.email, token, test, needs_password=True)
    else:
        send_test_available_email(candidate.email, test)
    
    return dispatch


def dispatch_test_to_emails(test, emails):
    results = [{"dispatched": [], "skipped": []}]

    for email in emails:
        email = email.strip().lower()
        if not email:
            continue

        try:
            dispatch = dispatch_test_to_email(test, email)
            # results['dispatched'].append(email)
            results[0]["dispatched"].append(email)
        except Exception as e:
            results[0]["skipped"].append(email)

    return results

