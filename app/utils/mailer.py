from flask import current_app
from flask_mail import Message

from app.extensions import mail


def _mail_ready():
    return bool(
        current_app.config.get("MAIL_USERNAME")
        and current_app.config.get("MAIL_PASSWORD")
    )


def send_high_risk_alert(user, log):
    if not _mail_ready() or not current_app.config.get("ADMIN_ALERT_EMAIL"):
        return False
    msg = Message(
        subject=f"DayTone high-risk alert: {user.name}",
        recipients=[current_app.config["ADMIN_ALERT_EMAIL"]],
        body=(
            f"{user.name} ({user.email}) has a High burnout risk entry on {log.log_date}.\n"
            f"Mood: {log.mood_label} ({log.mood_score}), Stress: {log.stress_level}, Sleep: {log.sleep_hours}"
        ),
    )
    mail.send(msg)
    return True


def send_daily_reminder(user):
    if not _mail_ready():
        return False
    msg = Message(
        subject="DayTone daily check-in",
        recipients=[user.email],
        body=f"Hi {user.name}, remember to log today's DayTone mood check-in.",
    )
    mail.send(msg)
    return True


def send_admin_change_request_email(req, approve_url, reject_url):
    if not _mail_ready() or not current_app.config.get("ADMIN_ALERT_EMAIL"):
        return False
    msg = Message(
        subject="DayTone Action Required: Admin Change Request Pending Approval",
        recipients=[current_app.config["ADMIN_ALERT_EMAIL"]],
        body=(
            f"An administrator change request has been submitted.\n\n"
            f"Requester: {req.requester.name} ({req.requester.email})\n"
            f"Requested Action: {req.request_type.replace('_', ' ').title()}\n"
            f"Proposed Admin to Promote: {req.target_user.name if req.target_user else 'None'} ({req.target_user.email if req.target_user else ''})\n\n"
            f"You can approve or reject this request by clicking one of the links below:\n\n"
            f"Approve Request: {approve_url}\n"
            f"Reject Request: {reject_url}\n"
        ),
    )
    mail.send(msg)
    return True
