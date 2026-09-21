from app.emails.send import send_email
from flask import url_for

def send_verification_email(to_email, token):
    verify_url = url_for('auth.verify_email', token=token, _external=True)
    subject = "Verify your ScoreRaven email"
    html_body = f"""
        <p>Welcome to ScoreRaven. Please verify your email to be eligible for test invites.</p>
        <p><a href="{verify_url}">Verify my email</a></p>
        <p>This link expires in 24 hours.</p>
    """

    send_email(to_email, subject, html_body)