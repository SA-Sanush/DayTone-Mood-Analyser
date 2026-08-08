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


@pytest.fixture()
def logged_in_client(client):
    register(client)
    login(client)
    return client


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


def test_mood_log_prediction_suggestion_and_exports(logged_in_client, app):
    response = logged_in_client.post(
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

    assert logged_in_client.get("/history").status_code == 200
    assert logged_in_client.get("/heatmap").status_code == 200
    assert logged_in_client.get("/api/heatmap").json
    export = logged_in_client.get("/export/csv")
    assert export.status_code == 200
    assert b"notes" not in export.data.splitlines()[0]
    private_export = logged_in_client.get("/export/csv?include_notes=1")
    assert b"notes" in private_export.data.splitlines()[0]
    
    pdf_response = logged_in_client.get("/report/pdf")
    assert pdf_response.status_code == 200
    assert pdf_response.headers["Content-Type"] == "application/pdf"
    assert pdf_response.headers["X-Content-Type-Options"] == "nosniff"
    assert pdf_response.data.startswith(b"%PDF-")
    assert b"DayTone" in pdf_response.data


def test_duplicate_log_date_warns_without_creating_second_log(logged_in_client, app):
    payload = {
        "log_date": date.today().isoformat(),
        "mood_score": 3,
        "sleep_hours": 7,
        "stress_level": 2,
        "activity_done": "y",
        "social_interaction": 2,
        "notes": "",
    }
    logged_in_client.post("/log", data=payload, follow_redirects=True)
    response = logged_in_client.post("/log", data=payload, follow_redirects=True)
    assert b"already have a log" in response.data
    with app.app_context():
        assert MoodLog.query.count() == 1


def test_edit_log_recomputes_prediction(logged_in_client, app):
    logged_in_client.post(
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
    response = logged_in_client.post(
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
    assert state["label"] == "Happy"
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
    assert result["prediction"] == BurnoutRisk.HIGH
    assert result["confidence"] == 0.78
    assert result["algorithm"] == "Rules"
    assert len(result["drivers"]) > 0
    predictor._model_payload.cache_clear()


def test_safe_next_url():
    from app.auth.routes import safe_next_url
    
    # Valid relative URLs
    assert safe_next_url("/dashboard") == "/dashboard"
    assert safe_next_url("/profile?edit=1") == "/profile?edit=1"
    
    # Invalid URLs
    assert safe_next_url(None) is None
    assert safe_next_url("") is None
    assert safe_next_url("http://google.com") is None
    assert safe_next_url("https://google.com") is None
    assert safe_next_url("//google.com") is None  # protocol-relative
    assert safe_next_url("///google.com") is None
    assert safe_next_url("dashboard") is None  # must start with /


def test_api_heatmap(logged_in_client):
    logged_in_client.post(
        "/log",
        data={
            "log_date": date.today().isoformat(),
            "mood_score": 4,
            "sleep_hours": 7.5,
            "stress_level": 2,
            "activity_done": "y",
            "social_interaction": 2,
            "notes": "Good day",
        },
    )
    
    response = logged_in_client.get("/api/heatmap")
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    
    assert len(data) >= 1
    day_detail = data[0]
    assert "date" in day_detail
    assert "mood" in day_detail
    assert "risk" in day_detail


def test_production_config_sqlite_and_admin_code_validation():
    # Test SQLite validation
    class ProductionSqliteConfig(Config):
        TESTING = False
        ENV = "production"
        SECRET_KEY = "super-secret-key-123456"
        RATELIMIT_STORAGE_URI = "redis://localhost:6379/0"
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        ADMIN_REGISTRATION_CODE = "admin-code-is-very-long-16chars"

    with pytest.raises(RuntimeError, match="DATABASE_URL must not use SQLite"):
        create_app(ProductionSqliteConfig)

    # Test missing ADMIN_REGISTRATION_CODE
    class ProductionMissingAdminCodeConfig(Config):
        TESTING = False
        ENV = "production"
        SECRET_KEY = "super-secret-key-123456"
        RATELIMIT_STORAGE_URI = "redis://localhost:6379/0"
        SQLALCHEMY_DATABASE_URI = "postgresql://localhost/db"
        ADMIN_REGISTRATION_CODE = None

    with pytest.raises(RuntimeError, match="ADMIN_REGISTRATION_CODE must be set"):
        create_app(ProductionMissingAdminCodeConfig)

    # Test too short ADMIN_REGISTRATION_CODE
    class ProductionShortAdminCodeConfig(Config):
        TESTING = False
        ENV = "production"
        SECRET_KEY = "super-secret-key-123456"
        RATELIMIT_STORAGE_URI = "redis://localhost:6379/0"
        SQLALCHEMY_DATABASE_URI = "postgresql://localhost/db"
        ADMIN_REGISTRATION_CODE = "shortcode"

    with pytest.raises(RuntimeError, match="ADMIN_REGISTRATION_CODE must be at least 16 characters"):
        create_app(ProductionShortAdminCodeConfig)


def test_send_daily_reminder(app):
    from app.utils.mailer import send_daily_reminder
    from app.models import User
    from unittest.mock import patch
    
    with app.app_context():
        user = User(name="Test User", email="test@example.com")
        
        with patch("app.utils.mailer._mail_ready", return_value=True), \
             patch("app.extensions.mail.send") as mock_send:
            
            success = send_daily_reminder(user)
            assert success is True
            mock_send.assert_called_once()
            args, _ = mock_send.call_args
            msg = args[0]
            assert msg.subject == "DayTone daily check-in"
            assert msg.recipients == ["test@example.com"]
            assert "Test User" in msg.body


def test_send_high_risk_alert(app):
    from app.utils.mailer import send_high_risk_alert
    from app.models import User, MoodLog
    from unittest.mock import patch
    
    with app.app_context():
        user = User(name="High Risk User", email="hr@example.com")
        log = MoodLog(mood_score=1, stress_level=5, sleep_hours=4.0)
        
        with patch("app.utils.mailer._mail_ready", return_value=True), \
             patch("app.extensions.mail.send") as mock_send:
            
            app.config["ADMIN_ALERT_EMAIL"] = "admin@example.com"
            success = send_high_risk_alert(user, log)
            assert success is True
            mock_send.assert_called_once()
            args, _ = mock_send.call_args
            msg = args[0]
            assert msg.subject == "DayTone high-risk alert: High Risk User"
            assert msg.recipients == ["admin@example.com"]
            assert "hr@example.com" in msg.body


def test_send_reminders_cli(app):
    from run import send_reminders
    from app.models import User, UserProfile
    from app.extensions import db
    from unittest.mock import patch
    
    if "send-reminders" not in app.cli.commands:
        app.cli.add_command(send_reminders)
        
    with app.app_context():
        user1 = User(name="Remind Me", email="remind@example.com")
        user1.set_password("secret12")
        user1.profile = UserProfile(daily_reminder=True)
        
        user2 = User(name="No Reminder", email="noremind@example.com")
        user2.set_password("secret12")
        user2.profile = UserProfile(daily_reminder=False)
        
        db.session.add_all([user1, user2])
        db.session.commit()
        
        runner = app.test_cli_runner()
        with patch("app.utils.mailer._mail_ready", return_value=True), \
             patch("app.extensions.mail.send") as mock_send:
            
            result = runner.invoke(args=["send-reminders"])
            assert "Daily reminder run complete" in result.output
            assert "Sent reminder to Remind Me" in result.output
            assert "No Reminder" not in result.output
            assert mock_send.call_count == 1


def test_high_risk_mood_log_sends_email_alert(logged_in_client, app):
    from unittest.mock import patch
    
    with patch("app.utils.mailer._mail_ready", return_value=True), \
         patch("app.extensions.mail.send") as mock_send:
        
        app.config["ADMIN_ALERT_EMAIL"] = "admin@example.com"
        
        logged_in_client.post(
            "/log",
            data={
                "log_date": date.today().isoformat(),
                "mood_score": 1,
                "sleep_hours": 3.0,
                "stress_level": 5,
                "activity_done": "",
                "social_interaction": 1,
                "notes": "Extremely burnt out.",
            },
            follow_redirects=True,
        )
        
        assert mock_send.call_count == 1
        args, _ = mock_send.call_args
        msg = args[0]
        assert msg.subject.startswith("DayTone high-risk alert:")
        assert msg.recipients == ["admin@example.com"]


def test_admin_user_detail_view(client, app):
    # 1. As anonymous user
    assert client.get("/admin/user/1").status_code == 302

    # 2. Register a normal user and login
    register(client, email="normal@example.com")
    login(client, email="normal@example.com")
    assert client.get("/admin/user/1").status_code == 403
    client.get("/logout")

    # 3. Register an admin user and login
    register(client, email="admin@example.com", admin=True)
    login(client, email="admin@example.com")
    
    with app.app_context():
        target_user = User.query.filter_by(email="normal@example.com").first()
        assert target_user is not None
        target_id = target_user.id
        
    response = client.get(f"/admin/user/{target_id}")
    assert response.status_code == 200
    assert b"normal@example.com" in response.data

    # 4. View non-existent user
    assert client.get("/admin/user/99999").status_code == 404


def test_admin_management_actions(client, app):
    # Register a normal user with log
    register(client, email="user_to_manage@example.com")
    login(client, email="user_to_manage@example.com")
    # Log mood
    client.post("/log", data={
        "log_date": "2026-06-10",
        "mood_score": 4,
        "sleep_hours": 7.5,
        "stress_level": 3,
        "social_interaction": 2,
        "activity_done": "y",
        "notes": "Original notes text."
    })
    client.get("/logout")

    # Register admin user and login
    register(client, email="super_admin@example.com", admin=True)
    login(client, email="super_admin@example.com")

    with app.app_context():
        target = User.query.filter_by(email="user_to_manage@example.com").first()
        target_id = target.id
        log = MoodLog.query.filter_by(user_id=target_id).first()
        log_id = log.id

    # 1. Edit User Profile
    res = client.get(f"/admin/user/{target_id}/profile")
    assert res.status_code == 200
    res = client.post(f"/admin/user/{target_id}/profile", data={
        "name": "Updated Managed User",
        "email": "user_to_manage@example.com",
        "role": "user",
        "age": 35,
        "gender": "male",
        "occupation": "Software Dev",
        "preferred_activity": "Yoga",
        "daily_reminder": "y"
    })
    assert res.status_code == 302 # redirect to user detail
    with app.app_context():
        target = User.query.get(target_id)
        assert target.name == "Updated Managed User"
        assert target.profile.age == 35
        assert target.profile.preferred_activity == "Yoga"

    # 2. Edit User Log should be disabled (404)
    res = client.get(f"/admin/user/{target_id}/log/{log_id}/edit")
    assert res.status_code == 404
    res = client.post(f"/admin/user/{target_id}/log/{log_id}/edit", data={
        "log_date": "2026-06-10",
        "mood_score": 5,
        "sleep_hours": 9.0,
        "stress_level": 1,
        "social_interaction": 3,
        "activity_done": "",
        "notes": "Admin updated notes."
    })
    assert res.status_code == 404

    # 3. Delete User Log should be disabled (404)
    res = client.post(f"/admin/user/{target_id}/log/{log_id}/delete")
    assert res.status_code == 404

    # 4. Self Demotion
    # We must register another admin first so this user is not the last admin
    client.get("/logout")
    register(client, email="second_temp_admin@example.com", admin=True)
    login(client, email="super_admin@example.com")
    with app.app_context():
        admin_user = User.query.filter_by(email="super_admin@example.com").first()
        admin_id = admin_user.id
    res = client.post(f"/admin/user/{admin_id}/toggle-role")
    assert res.status_code == 302 # redirect to login
    with app.app_context():
        assert User.query.get(admin_id).role == "user"

    # 5. Self Deletion
    # Log back in as admin (demoted user above is now normal user, let's register a new one)
    register(client, email="another_admin@example.com", admin=True)
    login(client, email="another_admin@example.com")
    with app.app_context():
        another_admin = User.query.filter_by(email="another_admin@example.com").first()
        another_id = another_admin.id
    res = client.post(f"/admin/user/{another_id}/delete")
    assert res.status_code == 302 # redirect to register
    with app.app_context():
        assert User.query.get(another_id) is None


def test_notes_encryption_at_rest(app, monkeypatch):
    from app.models import encrypt_text, decrypt_text, MoodLog
    from cryptography.fernet import Fernet
    import app.models as models
    
    key = Fernet.generate_key()
    cipher = Fernet(key)
    monkeypatch.setattr(models, "_fernet", cipher)
    
    raw_note = "Highly confidential note about mood."
    enc = encrypt_text(raw_note)
    assert enc != raw_note
    assert decrypt_text(enc) == raw_note
    
    with app.app_context():
        log = MoodLog(
            user_id=1,
            mood_score=3,
            sleep_hours=7.0,
            stress_level=3,
            social_interaction=2,
            activity_done=True,
            notes=raw_note
        )
        assert log._notes_encrypted != raw_note
        assert log.notes == raw_note


def test_notes_encryption_fallback(app, monkeypatch):
    from app.models import encrypt_text, decrypt_text, MoodLog
    import app.models as models
    
    monkeypatch.setattr(models, "_fernet", None)
    
    raw_note = "Fall back to plain text note."
    enc = encrypt_text(raw_note)
    assert enc == raw_note
    assert decrypt_text(enc) == raw_note
    
    with app.app_context():
        log = MoodLog(
            user_id=1,
            mood_score=3,
            sleep_hours=7.0,
            stress_level=3,
            social_interaction=2,
            activity_done=True,
            notes=raw_note
        )
        assert log._notes_encrypted == raw_note
        assert log.notes == raw_note


def test_gdpr_account_deletion_cascade(client, app):
    from app.models import User, UserProfile, MoodLog, Goal, Suggestion, BurnoutHistory
    register(client, email="gdpr-delete@example.com")
    login(client, email="gdpr-delete@example.com")
    
    with app.app_context():
        user = User.query.filter_by(email="gdpr-delete@example.com").first()
        user_id = user.id
        
        assert user.profile is not None
        
        goal = Goal(user_id=user_id, target_type="sleep", target_value=8.0)
        db.session.add(goal)
        
        log = MoodLog(
            user_id=user_id,
            mood_score=3,
            sleep_hours=7.0,
            stress_level=3,
            social_interaction=2,
            activity_done=True,
            notes="Notes to be deleted."
        )
        db.session.add(log)
        db.session.flush()
        
        sugg = Suggestion(user_id=user_id, log_id=log.id, suggestion_text="Do a walk")
        hist = BurnoutHistory(user_id=user_id, log_id=log.id, prediction="Low", confidence=0.7)
        db.session.add(sugg)
        db.session.add(hist)
        db.session.commit()
        
        db.session.delete(user)
        db.session.commit()
        
        assert User.query.get(user_id) is None
        assert UserProfile.query.filter_by(user_id=user_id).first() is None
        assert Goal.query.filter_by(user_id=user_id).first() is None
        assert MoodLog.query.filter_by(user_id=user_id).first() is None
        assert Suggestion.query.filter_by(user_id=user_id).first() is None
        assert BurnoutHistory.query.filter_by(user_id=user_id).first() is None


def test_prediction_feedback_endpoint(logged_in_client, app):
    from app.models import User, BurnoutHistory, MoodLog
    with app.app_context():
        user = User.query.filter_by(email="user@example.com").first()
        log = MoodLog.query.filter_by(user_id=user.id).first()
        if not log:
            log = MoodLog(
                user_id=user.id,
                mood_score=3,
                sleep_hours=7.0,
                stress_level=3,
                social_interaction=2,
                activity_done=True,
            )
            db.session.add(log)
            db.session.flush()
        
        history = BurnoutHistory(
            user_id=user.id,
            log_id=log.id,
            prediction="Low",
            confidence=0.75,
            algorithm_used="Rules"
        )
        db.session.add(history)
        db.session.commit()
        history_id = history.id
        
    res = logged_in_client.post(
        f"/api/feedback/{history_id}",
        json={"accurate": True}
    )
    assert res.status_code == 200
    assert res.get_json()["success"] is True
    
    with app.app_context():
        updated_history = BurnoutHistory.query.get(history_id)
        assert updated_history.is_accurate is True
        
    res = logged_in_client.post(
        f"/api/feedback/{history_id}",
        json={"accurate": False}
    )
    assert res.status_code == 200
    with app.app_context():
        updated_history = BurnoutHistory.query.get(history_id)
        assert updated_history.is_accurate is False
        
    res = logged_in_client.post(
        f"/api/feedback/{history_id}",
        json={}
    )
    assert res.status_code == 400


def test_explainability_driver_generation():
    from app.ml.predictor import explain_prediction
    
    features = {
        "mood_score": 1,
        "sleep_hours": 8.0,
        "stress_level": 2,
        "activity_done": 1,
        "social_interaction": 3,
        "sentiment_score": 0.5,
        "avg_mood_7d": 4.0,
        "avg_stress_7d": 2.0,
        "avg_sleep_7d": 8.0,
        "consecutive_bad_days": 1,
        "mood_variability": 0.1,
        "is_weekend": 0,
    }
    drivers = explain_prediction(features, "High")
    assert any("mood score" in d for d in drivers)
    assert any("mood is 75% below" in d for d in drivers)
    
    features = {
        "mood_score": 4,
        "sleep_hours": 5.0,
        "stress_level": 5,
        "activity_done": 1,
        "social_interaction": 3,
        "sentiment_score": 0.5,
        "avg_mood_7d": 4.0,
        "avg_stress_7d": 2.0,
        "avg_sleep_7d": 8.0,
        "consecutive_bad_days": 0,
        "mood_variability": 0.1,
        "is_weekend": 0,
    }
    drivers = explain_prediction(features, "Medium")
    assert any("Stress level" in d for d in drivers)
    assert any("Sleep duration" in d for d in drivers)
    assert any("Sleep is 3.0h below" in d for d in drivers)
    
    features = {
        "mood_score": 4,
        "sleep_hours": 8.0,
        "stress_level": 2,
        "activity_done": 1,
        "social_interaction": 3,
        "sentiment_score": -0.5,
        "avg_mood_7d": 4.0,
        "avg_stress_7d": 2.0,
        "avg_sleep_7d": 8.0,
        "consecutive_bad_days": 0,
        "mood_variability": 0.1,
        "is_weekend": 0,
    }
    drivers = explain_prediction(features, "Medium")
    assert any("emotional tone" in d for d in drivers)


def test_admin_lockout_guards(client, app):
    # Register and login as sole admin
    register(client, email="sole_admin@example.com", admin=True)
    login(client, email="sole_admin@example.com")
    
    with app.app_context():
        admin = User.query.filter_by(email="sole_admin@example.com").first()
        admin_id = admin.id
        assert admin.role == "admin"
        
    # Attempt self-demotion via toggle-role
    res = client.post(f"/admin/user/{admin_id}/toggle-role", follow_redirects=True)
    assert b"Cannot demote the last remaining administrator" in res.data
    
    # Attempt self-deletion
    res = client.post("/profile/delete", data={"confirm_delete": "DELETE"}, follow_redirects=True)
    assert b"You are the last remaining administrator" in res.data
    
    # Register a second admin (logout first, register, then log back in as sole_admin)
    client.get("/logout")
    register(client, email="second_admin@example.com", admin=True)
    login(client, email="sole_admin@example.com")
    
    # Try self-demotion again - should succeed now
    res = client.post(f"/admin/user/{admin_id}/toggle-role", follow_redirects=True)
    assert b"You have demoted yourself" in res.data
    
    with app.app_context():
        demoted_admin = User.query.get(admin_id)
        assert demoted_admin.role == "user"


def test_admin_change_request_flow(client, app):
    # Register sole admin and standard user
    register(client, email="sole@example.com", admin=True)
    register(client, email="trusted@example.com")
    login(client, email="sole@example.com")
    
    with app.app_context():
        sole_admin = User.query.filter_by(email="sole@example.com").first()
        trusted_user = User.query.filter_by(email="trusted@example.com").first()
        sole_id = sole_admin.id
        trusted_id = trusted_user.id
        
    # Submit change request
    res = client.post("/admin/change-request/submit", data={
        "action_type": "demote",
        "target_user_id": trusted_id
    }, follow_redirects=True)
    
    assert b"Request submitted" in res.data
    
    with app.app_context():
        from app.models import AdminChangeRequest
        req = AdminChangeRequest.query.filter_by(requester_id=sole_id).first()
        assert req is not None
        assert req.status == "pending"
        assert req.target_user_id == trusted_id
        token = req.token
        
    # Approve request via email link
    res = client.get(f"/admin/change-request/{token}/approve", follow_redirects=True)
    assert b"Your request has been approved" in res.data
    
    with app.app_context():
        updated_sole = User.query.get(sole_id)
        updated_trusted = User.query.get(trusted_id)
        assert updated_sole.role == "user"
        assert updated_trusted.role == "admin"


def test_developer_dashboard_requests(client, app):
    # Register sole admin and user first
    register(client, email="admin_req@example.com", admin=True)
    register(client, email="user_req@example.com")
    
    login(client, email="admin_req@example.com")
    
    with app.app_context():
        admin = User.query.filter_by(email="admin_req@example.com").first()
        user = User.query.filter_by(email="user_req@example.com").first()
        admin_id = admin.id
        user_id = user.id
        
    # Submit change request (will succeed since admin_req is currently the sole admin)
    client.post("/admin/change-request/submit", data={
        "action_type": "demote",
        "target_user_id": user_id
    })
    
    # Register developer in database
    with app.app_context():
        dev = User(name="Developer User", email="dev@example.com", role="developer")
        dev.set_password("secret12")
        db.session.add(dev)
        db.session.commit()
    
    # Log out admin and log in developer
    client.get("/logout")
    login(client, email="dev@example.com")
    
    # Access developer requests dashboard
    res = client.get("/admin/developer/dashboard")
    assert res.status_code == 200
    assert b"Admin Change Requests" in res.data
    
    with app.app_context():
        from app.models import AdminChangeRequest
        req = AdminChangeRequest.query.filter_by(requester_id=admin_id).first()
        req_id = req.id
        
    # Approve via dashboard
    res = client.post(f"/admin/developer/requests/{req_id}/approve", follow_redirects=True)
    assert res.status_code == 200
    
    with app.app_context():
        updated_admin = User.query.get(admin_id)
        updated_user = User.query.get(user_id)
        assert updated_admin.role == "user"
        assert updated_user.role == "admin"
        assert AdminChangeRequest.query.get(req_id).status == "approved"


def test_developer_authority_and_admin_protection(client, app):
    with app.app_context():
        admin = User(name="Regular Admin", email="admin_test@example.com", role="admin")
        admin.set_password("secret12")
        dev = User(name="Dev Leader", email="dev_test@example.com", role="developer")
        dev.set_password("secret12")
        db.session.add_all([admin, dev])
        db.session.commit()
        dev_id = dev.id
        admin_id = admin.id

    # 1. Developer login -> redirected to Developer Dashboard
    res = client.post("/login", data={"email": "dev_test@example.com", "password": "secret12"}, follow_redirects=False)
    assert res.status_code == 302
    assert "/admin/developer/dashboard" in res.headers["Location"]

    login(client, email="dev_test@example.com")
    # 2. Developer accessing /admin/dashboard -> redirected to /admin/developer/dashboard
    res = client.get("/admin/dashboard", follow_redirects=False)
    assert res.status_code == 302
    assert "/admin/developer/dashboard" in res.headers["Location"]

    client.get("/logout")

    # 3. Regular Admin tries to demote Developer -> Blocked
    login(client, email="admin_test@example.com")
    res = client.post(f"/admin/user/{dev_id}/toggle-role", follow_redirects=True)
    assert b"Only developers can modify developer accounts." in res.data

    with app.app_context():
        assert User.query.get(dev_id).role == "developer"



