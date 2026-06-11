from datetime import date, timedelta

from sqlalchemy import and_, func
from sqlalchemy.orm import joinedload

from app.constants import BurnoutRisk
from app.models import MoodLog, User, Suggestion
from app.extensions import cache


def user_logs(user_id: int, limit: int | None = None) -> list[MoodLog]:
    """Retrieve mood logs for a given user, ordered chronologically.

    If limit is specified, it returns the N most recent logs.
    """
    if limit:
        logs = (
            MoodLog.query.filter_by(user_id=user_id)
            .options(joinedload(MoodLog.suggestions))
            .order_by(MoodLog.log_date.desc())
            .limit(limit)
            .all()
        )
        logs.reverse()
        return logs
    return MoodLog.query.filter_by(user_id=user_id).order_by(MoodLog.log_date.asc()).all()


def current_streak(logs: list, today: date | None = None) -> int:
    """Calculate the consecutive day logging streak ending today or yesterday."""
    if not logs:
        return 0

    today = today or date.today()
    logged_days = {log.log_date for log in logs}
    cursor = today if today in logged_days else today - timedelta(days=1)
    streak = 0
    while cursor in logged_days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def trend_summary(logs):
    if not logs:
        return {
            "direction": "steady",
            "title": "No trend yet",
            "body": "Log a few days to reveal your rhythm.",
        }

    if len(logs) == 1:
        latest = logs[-1]
        return {
            "direction": "steady",
            "title": "First signal captured",
            "body": f"Your latest mood is {latest.mood_score}/5. A few more logs will make the pattern clearer.",
        }

    previous = logs[-2].mood_score
    latest = logs[-1].mood_score
    delta = latest - previous
    if delta > 0:
        return {
            "direction": "up",
            "title": "Mood is lifting",
            "body": f"Your mood rose by {delta} point{'s' if delta != 1 else ''} since the last check-in.",
        }
    if delta < 0:
        return {
            "direction": "down",
            "title": "Mood dipped",
            "body": f"Your mood moved down by {abs(delta)} point{'s' if delta != -1 else ''}. Keep the next step small and kind.",
        }
    return {
        "direction": "steady",
        "title": "Mood is steady",
        "body": "Your latest mood matches the previous check-in.",
    }


def badge_states(logs, streak_count, avg_mood):
    total_logs = len(logs)
    active_days = sum(1 for log in logs if log.activity_done)
    calm_days = sum(1 for log in logs if log.stress_level <= 2)
    badges = [
        {
            "name": "First Signal",
            "icon": "sparkles",
            "unlocked": total_logs >= 1,
            "detail": "Create your first mood log",
        },
        {
            "name": "7-Day Tone",
            "icon": "flame",
            "unlocked": streak_count >= 7,
            "detail": "Keep a 7-day logging streak",
        },
        {
            "name": "Bright Average",
            "icon": "sun",
            "unlocked": avg_mood >= 4,
            "detail": "Hold a 4+ average mood",
        },
        {
            "name": "Body Moved",
            "icon": "activity",
            "unlocked": active_days >= 5,
            "detail": "Log activity on 5 days",
        },
        {
            "name": "Calm Pocket",
            "icon": "leaf",
            "unlocked": calm_days >= 3,
            "detail": "Log 3 lower-stress days",
        },
    ]
    return badges


def orb_state(log):
    if not log:
        return {}

    mood = max(1, min(5, int(log.mood_score)))
    palette = {
        1: {"primary": "#ef4444", "secondary": "#ea580c", "label": "Sick"},
        2: {"primary": "#f97316", "secondary": "#d97706", "label": "Sad"},
        3: {"primary": "#eab308", "secondary": "#ca8a04", "label": "Anxious"},
        4: {"primary": "#10b981", "secondary": "#34d399", "label": "Calm"},
        5: {"primary": "#22c55e", "secondary": "#16a34a", "label": "Happy"},
    }
    sharpness = round((6 - mood) / 5, 2)
    calm = round(mood / 5, 2)
    return {
        "mood": mood,
        "label": palette[mood]["label"],
        "primary": palette[mood]["primary"],
        "secondary": palette[mood]["secondary"],
        "sharpness": sharpness,
        "calm": calm,
        "sleep": log.sleep_hours,
        "stress": log.stress_level,
        "risk": log.burnout_risk,
        "date": log.log_date.isoformat(),
    }


def challenge_progress(latest: MoodLog | None, streak_count: int) -> int:
    """Calculate progress percentage toward the daily wellness challenge.

    Rubric:
    - Base participation: 20%
    - Checked in today: +30%
    - Done physical activity: +20%
    - Sleep duration >= 7 hours: +15%
    - Stress level <= 3 (low/medium): +15%
    - Streak bonus: +2% per streak day (capped at 5 days, i.e., +10%)
    """
    if not latest:
        return 0

    progress = 20  # Base progress for logging historical data
    if latest.log_date == date.today():
        progress += 30  # Active logging today
    if latest.activity_done:
        progress += 20  # Physical activity logged
    if latest.sleep_hours >= 7:
        progress += 15  # Healthy sleep threshold met
    if latest.stress_level <= 3:
        progress += 15  # Controlled stress level threshold met

    # Cap total progress at 100% including streak bonus
    return min(100, progress + min(streak_count, 5) * 2)


@cache.memoize(timeout=120)
def dashboard_data(user_id: int) -> dict:
    """Compile aggregated analytics metrics for the user's dashboard view."""
    logs = user_logs(user_id, limit=30)
    latest = logs[-1] if logs else None
    distribution = {risk: count for risk, count in db_risk_distribution(user_id=user_id, limit=30)}
    avg_mood = round(sum(log.mood_score for log in logs) / len(logs), 2) if logs else 0
    avg_sleep = round(sum(log.sleep_hours for log in logs) / len(logs), 2) if logs else 0
    avg_stress = round(sum(log.stress_level for log in logs) / len(logs), 2) if logs else 0
    streak_count = current_streak(logs)

    return {
        "latest": latest,
        "suggestions": recent_suggestions(user_id),
        "labels": [log.log_date.isoformat() for log in logs],
        "mood": [log.mood_score for log in logs],
        "sleep": [log.sleep_hours for log in logs],
        "stress": [log.stress_level for log in logs],
        "burnout_risk_trend": [log.burnout_risk for log in logs],
        "burnout_distribution": {
            BurnoutRisk.LOW: distribution.get(BurnoutRisk.LOW, 0),
            BurnoutRisk.MEDIUM: distribution.get(BurnoutRisk.MEDIUM, 0),
            BurnoutRisk.HIGH: distribution.get(BurnoutRisk.HIGH, 0),
        },
        "scatter": [{"x": log.sleep_hours, "y": log.mood_score} for log in logs],
        "avg_mood": avg_mood,
        "avg_sleep": avg_sleep,
        "avg_stress": avg_stress,
        "streak_count": streak_count,
        "challenge_progress": challenge_progress(latest, streak_count),
        "badges": badge_states(logs, streak_count, avg_mood),
        "latest_orb_state": orb_state(latest),
        "trend_summary": trend_summary(logs),
        "insight_bars": {
            "mood": round((avg_mood / 5) * 100) if logs else 0,
            "sleep": round((min(avg_sleep, 10) / 10) * 100) if logs else 0,
            "stress": round(((6 - avg_stress) / 5) * 100) if logs else 0,
        },
    }


def heatmap_data(user_id, year=None):
    year = year or date.today().year
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    logs = (
        MoodLog.query.with_entities(MoodLog.log_date, MoodLog.mood_score, MoodLog.burnout_risk)
        .filter(MoodLog.user_id == user_id, MoodLog.log_date >= start, MoodLog.log_date <= end)
        .order_by(MoodLog.log_date.asc())
        .all()
    )
    return [{"date": log.log_date.isoformat(), "mood": log.mood_score, "risk": log.burnout_risk} for log in logs]


def recent_suggestions(user_id: int, log_limit: int = 3) -> list[str]:
    """Retrieve suggestions from the latest mood log that contains suggestions."""
    latest_log_with_sugg = (
        MoodLog.query.filter_by(user_id=user_id)
        .join(Suggestion)
        .order_by(MoodLog.log_date.desc())
        .first()
    )
    if latest_log_with_sugg:
        return [s.suggestion_text for s in latest_log_with_sugg.suggestions]
    return []


def db_risk_distribution(user_id=None, limit=None):
    query = MoodLog.query
    if user_id is not None:
        query = query.filter(MoodLog.user_id == user_id)
    if limit:
        latest_ids = (
            MoodLog.query.with_entities(MoodLog.id)
            .filter(MoodLog.user_id == user_id)
            .order_by(MoodLog.log_date.desc())
            .limit(limit)
            .subquery()
        )
        query = MoodLog.query.join(latest_ids, MoodLog.id == latest_ids.c.id)
    return (
        query.with_entities(MoodLog.burnout_risk, func.count(MoodLog.id).label("count"))
        .group_by(MoodLog.burnout_risk)
        .all()
    )


def platform_stats():
    cutoff = date.today() - timedelta(days=7)
    total_users = User.query.count()
    active_users = MoodLog.query.with_entities(MoodLog.user_id).filter(MoodLog.log_date >= cutoff).distinct().count()
    avg_mood = MoodLog.query.with_entities(func.avg(MoodLog.mood_score)).scalar() or 0
    avg_sleep = MoodLog.query.with_entities(func.avg(MoodLog.sleep_hours)).scalar() or 0

    latest = (
        MoodLog.query.with_entities(MoodLog.user_id, func.max(MoodLog.log_date).label("latest_date"))
        .group_by(MoodLog.user_id)
        .subquery()
    )
    distribution = {
        risk: count
        for risk, count in MoodLog.query.with_entities(MoodLog.burnout_risk, func.count(MoodLog.id))
        .join(
            latest,
            and_(MoodLog.user_id == latest.c.user_id, MoodLog.log_date == latest.c.latest_date),
        )
        .group_by(MoodLog.burnout_risk)
        .all()
    }

    return {
        "total_users": total_users,
        "active_users": active_users,
        "high_risk_users": distribution.get(BurnoutRisk.HIGH, 0),
        "avg_mood": round(avg_mood, 2),
        "avg_sleep": round(avg_sleep, 2),
        "burnout_distribution": {
            BurnoutRisk.LOW: distribution.get(BurnoutRisk.LOW, 0),
            BurnoutRisk.MEDIUM: distribution.get(BurnoutRisk.MEDIUM, 0),
            BurnoutRisk.HIGH: distribution.get(BurnoutRisk.HIGH, 0),
        },
    }
