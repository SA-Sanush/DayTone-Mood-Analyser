import pickle
from flask import current_app, has_app_context
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import func

from app.models import MoodLog
from app.constants import BurnoutRisk


FEATURE_NAMES = [
    "mood_score",
    "sleep_hours",
    "stress_level",
    "activity_done",
    "social_interaction",
    "sentiment_score",
    "avg_mood_7d",
    "avg_stress_7d",
    "avg_sleep_7d",
    "consecutive_bad_days",
    "mood_variability",
    "is_weekend",
]
BAD_DAY_WINDOW = 7

MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"


@lru_cache(maxsize=1)
def _model_payload():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

    with MODEL_PATH.open("rb") as model_file:
        return pickle.load(model_file)


def _recent_logs(user_id, log_date):
    start_date = log_date - timedelta(days=BAD_DAY_WINDOW - 1)
    return (
        MoodLog.query.filter(MoodLog.user_id == user_id, MoodLog.log_date >= start_date, MoodLog.log_date <= log_date)
        .order_by(MoodLog.log_date.asc())
        .all()
    )


def _consecutive_bad_days(logs, current_mood):
    """Count bad moods in the 7-day window ending with the current entry."""
    moods = [log.mood_score for log in logs] + [current_mood]
    count = 0
    for mood in reversed(moods):
        if mood <= 2:
            count += 1
        else:
            break
    return count


def build_features(
    user_id: int,
    log_date: date,
    mood_score: int,
    sleep_hours: float,
    stress_level: int,
    activity_done: bool,
    social_interaction: int,
    sentiment_score: float,
) -> dict[str, float | int]:
    """Validate inputs and compile a flat features dictionary for model prediction."""
    assert 1 <= mood_score <= 5, "mood_score must be between 1 and 5"
    assert 0 <= sleep_hours <= 24, "sleep_hours must be between 0 and 24"
    assert 1 <= stress_level <= 5, "stress_level must be between 1 and 5"
    assert 1 <= social_interaction <= 3, "social_interaction must be between 1 and 3"

    logs = _recent_logs(user_id, log_date)
    moods = [log.mood_score for log in logs] + [mood_score]
    stresses = [log.stress_level for log in logs] + [stress_level]
    sleeps = [log.sleep_hours for log in logs] + [sleep_hours]

    features = {
        "mood_score": mood_score,
        "sleep_hours": sleep_hours,
        "stress_level": stress_level,
        "activity_done": int(bool(activity_done)),
        "social_interaction": social_interaction,
        "sentiment_score": sentiment_score,
        "avg_mood_7d": float(np.mean(moods)),
        "avg_stress_7d": float(np.mean(stresses)),
        "avg_sleep_7d": float(np.mean(sleeps)),
        "consecutive_bad_days": _consecutive_bad_days(logs, mood_score),
        "mood_variability": float(np.std(moods)) if len(moods) > 1 else 0.0,
        "is_weekend": 1 if log_date.weekday() >= 5 else 0,
    }
    if set(features) != set(FEATURE_NAMES):
        raise RuntimeError("Feature mismatch between training and inference.")
    return features


def _rule_prediction(features):
    score = 0
    score += 2 if features["mood_score"] <= 2 else 0
    score += 2 if features["stress_level"] >= 4 else 0
    score += 1 if features["sleep_hours"] < 6 else 0
    score += 1 if not features["activity_done"] else 0
    score += 1 if features["social_interaction"] == 1 else 0
    score += 1 if features["sentiment_score"] < -0.2 else 0
    score += 1 if features["consecutive_bad_days"] >= 3 else 0

    if score >= 5:
        return BurnoutRisk.HIGH, 0.78
    if score >= 3:
        return BurnoutRisk.MEDIUM, 0.66
    return BurnoutRisk.LOW, 0.72


def _log_prediction_fallback(exc):
    if has_app_context():
        current_app.logger.warning("ML predict failed (%s), using rule fallback", exc)


def predict_burnout(features: dict[str, float | int]) -> dict[str, str | float]:
    """Predict burnout risk using the loaded ML model, falling back to rule-based logic on error or missing model."""
    try:
        payload = _model_payload()
    except FileNotFoundError as exc:
        _log_prediction_fallback(exc)
        payload = None
    except Exception as exc:
        _log_prediction_fallback(exc)
        payload = None

    if payload is None:
        prediction, confidence = _rule_prediction(features)
        return {"prediction": prediction, "confidence": confidence, "algorithm": "Rules"}

    try:
        artifact_features = payload.get("features")
        if artifact_features and list(artifact_features) != FEATURE_NAMES:
            raise RuntimeError("Model feature list does not match inference features.")
        model = payload["model"]
        values = pd.DataFrame([[features[name] for name in FEATURE_NAMES]], columns=FEATURE_NAMES)
        prediction = model.predict(values)[0]
        confidence = None
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(values)[0]
            confidence = float(max(probabilities))
        return {"prediction": prediction, "confidence": confidence, "algorithm": payload.get("name", "ML")}
    except Exception as exc:
        _log_prediction_fallback(exc)
        prediction, confidence = _rule_prediction(features)
        return {"prediction": prediction, "confidence": confidence, "algorithm": "Rules"}


def latest_burnout_subquery():
    return (
        MoodLog.query.with_entities(MoodLog.user_id, func.max(MoodLog.log_date).label("latest_date"))
        .group_by(MoodLog.user_id)
        .subquery()
    )
