import os

from app import create_app
from app.extensions import db


app = create_app()


@app.cli.command("send-reminders")
def send_reminders():
    """Send daily email check-in reminders to users who opted in and have not logged today."""
    from datetime import date
    from app.models import User, UserProfile, MoodLog
    from app.utils.mailer import send_daily_reminder

    today = date.today()
    users_to_remind = User.query.join(UserProfile).filter(UserProfile.daily_reminder == True).all()

    sent_count = 0
    for user in users_to_remind:
        has_log = MoodLog.query.filter_by(user_id=user.id, log_date=today).first() is not None
        if not has_log:
            if send_daily_reminder(user):
                sent_count += 1
                print(f"Sent reminder to {user.name} ({user.email})")

    print(f"Daily reminder run complete. Sent {sent_count} email(s).")


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
