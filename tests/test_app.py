from datetime import date, timedelta
from types import SimpleNamespace

import pytest

from app import create_app
from app.extensions import db
from app.constants import BurnoutRisk
from app.models import BurnoutHistory, MoodLog, Suggestion, User
from app.utils.analytics import badge_states, current_streak, dashboard_data, orb_state, trend_summary
from config import Config, TestConfig
from app.ml.generate_data import generate
from app.ml.predictor import FEATURE_NAMES, predict_burnout


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def register(client, email="user@example.com", admin=False):
    return client.post(
        "/register",
        data={
            "name": "Test User",
            "email": email,
            "password": "secret12",
            "confirm_password": "secret12",
            "age": 22,
            "gender": "other",
            "occupation": "Student",
            "preferred_activity": "Walk",
            "admin_code": TestConfig.ADMIN_REGISTRATION_CODE if admin else "",
        },
        follow_redirects=True,
    )


def login(client, email="user@example.com"):
    return client.post(
        "/login",
        data={"email": email, "password": "secret12"},
        follow_redirects=True,
    )


def test_auth_register_login_logout(client, app):
    response = register(client)
    assert b"sign in" in response.data.lower()
    response = login(client)
    assert b"Dashboard" in response.data
    response = client.get("/logout", follow_redirects=True)
    assert b"Sign in" in response.data
    with app.app_context():
        assert User.query.filter_by(email="user@example.com").first() is not None


def test_login_rejects_external_next_redirect(client):
    register(client)
    response = client.post(
        "/login?next=https://evil.example/phish",
        data={"email": "user@example.com", "password": "secret12"},
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    assert "evil.example" not in response.headers["Location"]


def test_mood_log_prediction_suggestion_and_exports(client, app):
    register(client)
    login(client)
    response = client.post(
        "/log",
        data={
            "log_date": date.today().isoformat(),
            "mood_score": 2,
            "sleep_hours": 4.5,
            "stress_level": 5,
            "activity_done": "",
            "social_interaction": 1,
            "notes": "I feel exhausted and overwhelmed.",
        },
        follow_redirects=True,
    )
    assert b"moodOrb" in response.data
    assert b"DAYTONE_DASHBOARD" in response.data
    assert b"Day streak" in response.data
    with app.app_context():
        log = MoodLog.query.first()
        assert log is not None
        assert log.sentiment_score <= 0
        assert BurnoutHistory.query.count() == 1
        assert Suggestion.query.count() >= 1
        data = dashboard_data(log.user_id)
        assert data["burnout_risk_trend"] == [log.burnout_risk]

    assert client.get("/history").status_code == 200
    assert client.get("/heatmap").status_code == 200
    assert client.get("/api/heatmap").json
    export = client.get("/export/csv")
    assert export.status_code == 200
    assert b"notes" not in export.data.splitlines()[0]
    private_export = client.get("/export/csv?include_notes=1")
    assert b"notes" in private_export.data.splitlines()[0]
    assert client.get("/report/pdf").status_code == 200


def test_duplicate_log_date_warns_without_creating_second_log(client, app):
    register(client)
    login(client)
    payload = {
        "log_date": date.today().isoformat(),
        "mood_score": 3,
        "sleep_hours": 7,
        "stress_level": 2,
        "activity_done": "y",
        "social_interaction": 2,
        "notes": "",
    }
    client.post("/log", data=payload, follow_redirects=True)
    response = client.post("/log", data=payload, follow_redirects=True)
    assert b"already have a log" in response.data
    with app.app_context():
        assert MoodLog.query.count() == 1


def test_edit_log_recomputes_prediction(client, app):
    register(client)
    login(client)
    client.post(
        "/log",
        data={
            "log_date": date.today().isoformat(),
            "mood_score": 5,
            "sleep_hours": 8,
            "stress_level": 1,
            "activity_done": "y",
            "social_interaction": 3,
            "notes": "A steady day.",
        },
    )
    with app.app_context():
        log_id = MoodLog.query.first().id
    response = client.post(
        f"/log/{log_id}/edit",
        data={
            "log_date": date.today().isoformat(),
            "mood_score": 1,
            "sleep_hours": 3,
            "stress_level": 5,
            "activity_done": "",
            "social_interaction": 1,
            "notes": "Exhausted and overwhelmed.",
        },
        follow_redirects=True,
    )
    assert b"updated" in response.data.lower()
    with app.app_context():
        log = db.session.get(MoodLog, log_id)
        assert log.burnout_risk == BurnoutRisk.HIGH
        assert BurnoutHistory.query.filter_by(log_id=log_id).count() == 1


def test_dashboard_derived_state_helpers():
    today = date(2026, 6, 10)
    logs = [
        SimpleNamespace(log_date=today - timedelta(days=2), mood_score=3, sleep_hours=6.5, stress_level=2, activity_done=True, burnout_risk=BurnoutRisk.LOW),
        SimpleNamespace(log_date=today - timedelta(days=1), mood_score=4, sleep_hours=7.0, stress_level=2, activity_done=True, burnout_risk=BurnoutRisk.LOW),
        SimpleNamespace(log_date=today, mood_score=5, sleep_hours=8.0, stress_level=1, activity_done=True, burnout_risk=BurnoutRisk.LOW),
    ]

    streak = current_streak(logs, today=today)
    badges = badge_states(logs, streak, avg_mood=4)
    state = orb_state(logs[-1])
    trend = trend_summary(logs)

    assert streak == 3
    assert state["mood"] == 5
    assert state["label"] == "Radiant"
    assert trend["direction"] == "up"
    assert any(badge["name"] == "Bright Average" and badge["unlocked"] for badge in badges)
    assert any(badge["name"] == "Calm Pocket" and badge["unlocked"] for badge in badges)


def test_production_config_requires_secret_and_shared_rate_limit_store():
    class BadProductionConfig(Config):
        TESTING = False
        ENV = "production"
        SECRET_KEY = None
        RATELIMIT_STORAGE_URI = "redis://localhost:6379/0"
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app(BadProductionConfig)

    class BadRateLimitConfig(BadProductionConfig):
        SECRET_KEY = "private-production-secret"
        RATELIMIT_STORAGE_URI = "memory://"

    with pytest.raises(RuntimeError, match="RATELIMIT_STORAGE_URI"):
        create_app(BadRateLimitConfig)


def test_admin_access_control(client):
    register(client)
    login(client)
    assert client.get("/admin/dashboard").status_code == 403
    client.get("/logout")
    register(client, email="admin@example.com", admin=True)
    login(client, email="admin@example.com")
    assert client.get("/admin/dashboard").status_code == 200


def test_invalid_admin_registration_code_does_not_grant_admin(client, app):
    response = client.post(
        "/register",
        data={
            "name": "Admin Nope",
            "email": "not-admin@example.com",
            "password": "secret12",
            "confirm_password": "secret12",
            "age": 22,
            "gender": "other",
            "occupation": "Student",
            "preferred_activity": "Walk",
            "admin_code": "wrong-code",
        },
        follow_redirects=True,
    )
    assert b"sign in" in response.data.lower()
    with app.app_context():
        assert User.query.filter_by(email="not-admin@example.com").first().role == "user"


def test_trained_model_artifact_loads_and_predicts(app):
    row = generate(rows=1).iloc[0].to_dict()
    features = {name: row[name] for name in FEATURE_NAMES}
    with app.app_context():
        result = predict_burnout(features)
    assert result["prediction"] in BurnoutRisk.ALL
    assert 0 <= result["confidence"] <= 1
    assert result["algorithm"] in {"DecisionTree", "LogisticRegression", "RandomForest", "Rules"}


def test_missing_model_artifact_uses_rule_fallback(monkeypatch, app):
    from app.ml import predictor

    monkeypatch.setattr(predictor, "MODEL_PATH", predictor.MODEL_PATH.with_name("missing-model.pkl"))
    predictor._model_payload.cache_clear()
    features = {
        "mood_score": 1,
        "sleep_hours": 4,
        "stress_level": 5,
        "activity_done": 0,
        "social_interaction": 1,
        "sentiment_score": -0.5,
        "avg_mood_7d": 2,
        "avg_stress_7d": 5,
        "avg_sleep_7d": 4,
        "consecutive_bad_days": 3,
        "mood_variability": 0.5,
        "is_weekend": 0,
    }
    with app.app_context():
        result = predictor.predict_burnout(features)
    assert result == {"prediction": BurnoutRisk.HIGH, "confidence": 0.78, "algorithm": "Rules"}
    predictor._model_payload.cache_clear()
