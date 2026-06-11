from flask import current_app
from flask_mail import Message

from app.extensions import mail


def _mail_ready():
    return bool(current_app.config.get("MAIL_USERNAME") and current_app.config.get("MAIL_PASSWORD"))


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
