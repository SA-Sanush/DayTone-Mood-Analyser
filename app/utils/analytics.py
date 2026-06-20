from datetime import date, timedelta

import numpy as np
from sqlalchemy import and_, func
from sqlalchemy.orm import joinedload

from app.constants import BurnoutRisk
from app.models import BurnoutHistory, Goal, MoodLog, User, Suggestion
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


def _pearson_correlation(xs: list, ys: list) -> float | None:
    """Compute Pearson correlation coefficient. Returns None if insufficient data."""
    if len(xs) < 5 or len(ys) < 5:
        return None
    try:
        arr_x = np.array(xs, dtype=float)
        arr_y = np.array(ys, dtype=float)
        coeff = float(np.corrcoef(arr_x, arr_y)[0, 1])
        return round(coeff, 2) if not np.isnan(coeff) else None
    except Exception:
        return None


def compute_correlation_insight(logs: list) -> dict | None:
    """Compute proactive correlation insights from recent logs.

    Returns a dict with 'text' (human-readable insight) and 'strength' (-1 to 1),
    or None if there are insufficient data points.
    Currently computes: sleep↔mood, stress↔mood.
    The strongest significant correlation is returned.
    """
    if len(logs) < 5:
        return None

    sleeps = [log.sleep_hours for log in logs]
    moods = [log.mood_score for log in logs]
    stresses = [log.stress_level for log in logs]

    sleep_mood_r = _pearson_correlation(sleeps, moods)
    stress_mood_r = _pearson_correlation(stresses, moods)

    insights = []

    if sleep_mood_r is not None and abs(sleep_mood_r) >= 0.3:
        direction = "positively" if sleep_mood_r > 0 else "inversely"
        strength_word = "strongly" if abs(sleep_mood_r) >= 0.6 else "moderately"
        insights.append({
            "text": f"Your sleep and mood are {strength_word} {direction} correlated (r={sleep_mood_r:+.2f}) — more sleep tends to {'lift' if sleep_mood_r > 0 else 'lower'} your mood.",
            "strength": sleep_mood_r,
            "type": "sleep_mood",
        })

    if stress_mood_r is not None and abs(stress_mood_r) >= 0.3:
        direction = "inversely" if stress_mood_r < 0 else "positively"
        strength_word = "strongly" if abs(stress_mood_r) >= 0.6 else "moderately"
        insights.append({
            "text": f"Your stress and mood are {strength_word} {direction} correlated (r={stress_mood_r:+.2f}) — {'higher stress tends to lower your mood' if stress_mood_r < 0 else 'stress and mood move together'}.",
            "strength": stress_mood_r,
            "type": "stress_mood",
        })

    if not insights:
        return None

    # Return the insight with the strongest (absolute) correlation
    return max(insights, key=lambda x: abs(x["strength"]))


def goal_progress(goal: "Goal", user_id: int) -> dict:
    """Compute current progress toward a user goal and return as a display dict.

    Returns:
        current_value: current measured value
        target_value: goal target value
        pct: 0-100 percentage completion
        status: 'on_track' | 'behind' | 'achieved'
    """
    today = date.today()
    start = goal.start_date
    recent_logs = (
        MoodLog.query.filter(
            MoodLog.user_id == user_id,
            MoodLog.log_date >= start,
            MoodLog.log_date <= today,
        )
        .order_by(MoodLog.log_date.asc())
        .all()
    )

    if not recent_logs:
        return {"current_value": 0.0, "target_value": goal.target_value, "pct": 0, "status": "behind"}

    target_type = goal.target_type
    if target_type == "sleep":
        current_value = round(sum(log.sleep_hours for log in recent_logs) / len(recent_logs), 1)
    elif target_type == "mood":
        current_value = round(sum(log.mood_score for log in recent_logs) / len(recent_logs), 1)
    elif target_type == "active_days":
        # Count distinct active days in the last 7 days
        cutoff = today - timedelta(days=7)
        week_logs = [log for log in recent_logs if log.log_date >= cutoff]
        current_value = float(sum(1 for log in week_logs if log.activity_done))
    elif target_type == "journal_days":
        cutoff = today - timedelta(days=7)
        week_logs = [log for log in recent_logs if log.log_date >= cutoff]
        current_value = float(len(week_logs))
    elif target_type == "stress":
        current_value = round(sum(log.stress_level for log in recent_logs) / len(recent_logs), 1)
    else:
        current_value = 0.0

    # For stress, lower is better — invert progress calculation
    if target_type == "stress":
        # goal.target_value is the desired maximum stress
        if current_value <= goal.target_value:
            pct = 100
            status = "achieved"
        else:
            # Progress toward target: how close to target from worst case (5)
            pct = max(0, round((5 - current_value) / (5 - goal.target_value) * 100))
            status = "behind"
    else:
        pct = min(100, round(current_value / goal.target_value * 100)) if goal.target_value > 0 else 0
        if pct >= 100:
            status = "achieved"
        elif pct >= 70:
            status = "on_track"
        else:
            status = "behind"

    return {
        "current_value": current_value,
        "target_value": goal.target_value,
        "pct": pct,
        "status": status,
    }


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

    # Compute burnout prediction drivers from the latest log's BurnoutHistory
    drivers = []
    if latest:
        bh = BurnoutHistory.query.filter_by(log_id=latest.id).order_by(BurnoutHistory.predicted_at.desc()).first()
        # drivers are regenerated at prediction time; fetch from the latest history record
        # (they are not stored — we regenerate them here from the stored features)
        from app.ml.predictor import explain_prediction
        synthetic_features = {
            "mood_score": latest.mood_score,
            "sleep_hours": latest.sleep_hours,
            "stress_level": latest.stress_level,
            "activity_done": int(latest.activity_done),
            "social_interaction": latest.social_interaction,
            "sentiment_score": latest.sentiment_score,
            "avg_mood_7d": avg_mood,
            "avg_stress_7d": avg_stress,
            "avg_sleep_7d": avg_sleep,
            "consecutive_bad_days": sum(1 for log in reversed(logs) if log.mood_score <= 2),
            "mood_variability": 0.0,
            "is_weekend": 1 if latest.log_date.weekday() >= 5 else 0,
        }
        drivers = explain_prediction(synthetic_features, latest.burnout_risk)

    # Latest burnout history entry for the latest log
    latest_history = None
    if latest:
        latest_history = BurnoutHistory.query.filter_by(log_id=latest.id).order_by(BurnoutHistory.predicted_at.desc()).first()

    return {
        "latest": latest,
        "latest_history": latest_history,
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
        "drivers": drivers,
        "correlation_insight": compute_correlation_insight(logs),
    }


def heatmap_data(user_id, year=None):
    year = year or date.today().year
    start = date(year, 1, 1)
    end = date(year, 12, 31)
    logs = (
        MoodLog.query.with_entities(MoodLog.id, MoodLog.log_date, MoodLog.mood_score, MoodLog.burnout_risk)
        .filter(MoodLog.user_id == user_id, MoodLog.log_date >= start, MoodLog.log_date <= end)
        .order_by(MoodLog.log_date.asc())
        .all()
    )
    return [{"id": log.id, "date": log.log_date.isoformat(), "mood": log.mood_score, "risk": log.burnout_risk} for log in logs]


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

    # Feedback accuracy rate across all users
    total_feedback = BurnoutHistory.query.filter(BurnoutHistory.is_accurate.isnot(None)).count()
    accurate_feedback = BurnoutHistory.query.filter(BurnoutHistory.is_accurate == True).count()  # noqa: E712
    feedback_accuracy = round(accurate_feedback / total_feedback * 100, 1) if total_feedback > 0 else None

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
        "feedback_accuracy": feedback_accuracy,
        "total_feedback_responses": total_feedback,
    }
