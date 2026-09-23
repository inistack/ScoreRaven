from flask import url_for
from app.emails.send import send_email

def send_dispatch_invite_email(to_email, token, test, needs_password):
    if needs_password:
        action_url = url_for('auth.set_password', token=token, _external=True)
        action_text = 'Set your password and start the test'
    else:
        action_url = url_for('auth.login', _external=True)
        action_text = 'Log in and start the test'
    
    html_body = f"""
        <p>You've been invited to take <strong>{test.title}</strong> on ScoreRaven.</p>
        <p>You have {test.validity_hours} hours to start this test from the time of this invite.</p>
        <p><a href="{action_url}">{action_text}</a></p>
    """
    send_email(to=to_email, subject=f"Invitation to take {test.title}", html_body=html_body)


def send_test_available_email(to_email, test):
    login_url = url_for('auth.login', _external=True)

    html_body = f"""
        <p>A new test is available for you: <strong>{test.title}</strong>.</p>
        <p>You have {test.validity_hours} hours to start this test from the time of this invite.</p>
        <p><a href="{login_url}">Log in to start</a></p>
    """
    send_email(to=to_email, subject=f"New test available: {test.title}", html_body=html_body)