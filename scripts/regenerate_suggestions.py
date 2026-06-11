"""
One-shot script: regenerates suggestions for every existing MoodLog
using the updated suggestions engine.

Run from the project root:
  .venv/bin/python scripts/regenerate_suggestions.py
"""
import sys
sys.path.insert(0, "/home/crystal/Desktop/DayTone")

from app import create_app
from app.extensions import db
from app.models import MoodLog, Suggestion, User
from app.utils.suggestions import get_suggestions

app = create_app()

with app.app_context():
    logs = MoodLog.query.all()
    total = len(logs)
    updated = 0

    for log in logs:
        # Fetch preferred activity from user profile
        user = db.session.get(User, log.user_id)
        preferred = "Walk"
        if user and user.profile and user.profile.preferred_activity:
            preferred = user.profile.preferred_activity

        # Delete old suggestions for this log
        Suggestion.query.filter_by(log_id=log.id).delete()

        # Generate fresh suggestions using the new engine
        new_tips = get_suggestions(
            burnout_risk=log.burnout_risk,
            sleep_hours=log.sleep_hours,
            stress_level=log.stress_level,
            social_interaction=log.social_interaction,
            activity_done=log.activity_done,
            preferred_activity=preferred,
        )

        for text in new_tips:
            db.session.add(Suggestion(
                user_id=log.user_id,
                log_id=log.id,
                suggestion_text=text,
            ))

        updated += 1
        print(f"  [{updated}/{total}] Log {log.id} ({log.log_date}) → {len(new_tips)} suggestions")

    db.session.commit()
    print(f"\n✅ Done. Regenerated suggestions for {updated} log(s).")
