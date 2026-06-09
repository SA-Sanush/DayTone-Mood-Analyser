from datetime import date, datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    profile = db.relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    mood_logs = db.relationship("MoodLog", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"


class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    occupation = db.Column(db.String(100))
    preferred_activity = db.Column(db.String(50), default="Walk")

    user = db.relationship("User", back_populates="profile")


class MoodLog(db.Model):
    __table_args__ = (db.UniqueConstraint("user_id", "log_date", name="uq_user_log_date"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    log_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    mood_score = db.Column(db.Integer, nullable=False)
    sleep_hours = db.Column(db.Float, nullable=False)
    stress_level = db.Column(db.Integer, nullable=False)
    activity_done = db.Column(db.Boolean, nullable=False, default=False)
    social_interaction = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    sentiment_score = db.Column(db.Float, nullable=False, default=0.0)
    burnout_risk = db.Column(db.String(10), nullable=False, default="Low")
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    user = db.relationship("User", back_populates="mood_logs")
    suggestions = db.relationship("Suggestion", back_populates="log", cascade="all, delete-orphan")
    burnout_history = db.relationship("BurnoutHistory", back_populates="log", cascade="all, delete-orphan")


class BurnoutHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    log_id = db.Column(db.Integer, db.ForeignKey("mood_log.id"), nullable=False, index=True)
    prediction = db.Column(db.String(10), nullable=False)
    confidence = db.Column(db.Float, nullable=False, default=0.0)
    algorithm_used = db.Column(db.String(50), nullable=False, default="Rules")
    predicted_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    user = db.relationship("User")
    log = db.relationship("MoodLog", back_populates="burnout_history")


class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    log_id = db.Column(db.Integer, db.ForeignKey("mood_log.id"), nullable=False, index=True)
    suggestion_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    user = db.relationship("User")
    log = db.relationship("MoodLog", back_populates="suggestions")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
