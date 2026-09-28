from markupsafe import escape
from app.emails.send import external_url, send_email


def send_results_released_email(to_email, dispatch):
    results_url = external_url("candidate.view_results", dispatch_id=dispatch.id)

    html_body = f"""
        <p>Your results for <strong>{escape(dispatch.test.title)}</strong> are now available.</p>
        <p><a href="{results_url}">View your results</a></p>
    """

    send_email(
        to=to_email,
        subject=f"Your results are ready: {dispatch.test.title}",
        html_body=html_body,
    )