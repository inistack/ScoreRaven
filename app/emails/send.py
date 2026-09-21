import resend
from flask import current_app

def _get_client():
    resend_api_key = current_app.config.get("RESEND_API_KEY")
    resend.api_key = resend_api_key
    return resend


def send_email(to, subject, html_body):
    client = _get_client()
    client.Emails.send(
        {
            "from": current_app.config.get("EMAIL_FROM", "noreply@iniarthur.dev"),
            "to": to,
            "subject": subject,
            "html": html_body,
        }
    )
