from collections import Counter
from datetime import date, timedelta

from sqlalchemy import func

from app.models import MoodLog, User


def user_logs(user_id, limit=None):
    query = MoodLog.query.filter_by(user_id=user_id).order_by(MoodLog.log_date.asc())
    if limit:
        return query.order_by(MoodLog.log_date.desc()).limit(limit).all()[::-1]
    return query.all()


def dashboard_data(user_id):
    logs = user_logs(user_id, limit=30)
    latest = logs[-1] if logs else None
    distribution = Counter(log.burnout_risk for log in logs)

    return {
        "latest": latest,
        "suggestions": [s.suggestion_text for s in latest.suggestions] if latest else [],
        "labels": [log.log_date.isoformat() for log in logs],
        "mood": [log.mood_score for log in logs],
        "sleep": [log.sleep_hours for log in logs],
        "stress": [log.stress_level for log in logs],
        "burnout_distribution": {
            "Low": distribution.get("Low", 0),
            "Medium": distribution.get("Medium", 0),
            "High": distribution.get("High", 0),
        },
        "scatter": [{"x": log.sleep_hours, "y": log.mood_score} for log in logs],
        "avg_mood": round(sum(log.mood_score for log in logs) / len(logs), 2) if logs else 0,
        "avg_sleep": round(sum(log.sleep_hours for log in logs) / len(logs), 2) if logs else 0,
        "avg_stress": round(sum(log.stress_level for log in logs) / len(logs), 2) if logs else 0,
    }


def heatmap_data(user_id, year=None):
    year = year or date.today().year
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    logs = (
        MoodLog.query.filter(MoodLog.user_id == user_id, MoodLog.log_date >= start, MoodLog.log_date <= end)
        .order_by(MoodLog.log_date.asc())
        .all()
    )
    return [{"date": log.log_date.isoformat(), "mood": log.mood_score, "risk": log.burnout_risk} for log in logs]


def platform_stats():
    cutoff = date.today() - timedelta(days=7)
    total_users = User.query.count()
    active_users = MoodLog.query.with_entities(MoodLog.user_id).filter(MoodLog.log_date >= cutoff).distinct().count()
    avg_mood = MoodLog.query.with_entities(func.avg(MoodLog.mood_score)).scalar() or 0
    avg_sleep = MoodLog.query.with_entities(func.avg(MoodLog.sleep_hours)).scalar() or 0

    latest_logs = []
    for user in User.query.all():
        latest = MoodLog.query.filter_by(user_id=user.id).order_by(MoodLog.log_date.desc()).first()
        if latest:
            latest_logs.append(latest)
    distribution = Counter(log.burnout_risk for log in latest_logs)

    return {
        "total_users": total_users,
        "active_users": active_users,
        "high_risk_users": distribution.get("High", 0),
        "avg_mood": round(avg_mood, 2),
        "avg_sleep": round(avg_sleep, 2),
        "burnout_distribution": {
            "Low": distribution.get("Low", 0),
            "Medium": distribution.get("Medium", 0),
            "High": distribution.get("High", 0),
        },
    }
