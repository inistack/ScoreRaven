import resend
from flask import current_app, url_for

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


def external_url(endpoint, **values):
    with current_app.test_request_context(base_url=current_app.config["APP_BASE_URL"]):
        return url_for(endpoint, _external=True, **values)