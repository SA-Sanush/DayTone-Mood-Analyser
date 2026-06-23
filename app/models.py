"""DayTone database models.

Encryption at Rest (notes field):
  Sensitive journal entries in MoodLog.notes are encrypted using Fernet
  symmetric encryption from the `cryptography` package.

  - Key source: ENCRYPTION_KEY environment variable (must be 32 URL-safe
    base64-encoded bytes, generated with `Fernet.generate_key()`).
  - If `cryptography` is not installed or the key is missing/invalid, the
    system falls back to plain-text storage with a one-time warning log.
  - Encryption is transparent: reading `log.notes` always returns plain text;
    writing `log.notes = value` encrypts automatically via the hybrid property.
"""
import logging
import os
import warnings
from datetime import date, datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Fernet encryption helper (graceful fallback if library unavailable)
# ---------------------------------------------------------------------------


def _build_fernet():
    """Attempt to instantiate a Fernet cipher using ENCRYPTION_KEY env var.

    Returns a Fernet instance on success, or None if unavailable.
    Falls back gracefully so the app still runs without the `cryptography`
    package installed, printing one startup warning.
    """
    try:
        from cryptography.fernet import Fernet, InvalidToken  # noqa: F401

        raw_key = os.environ.get("ENCRYPTION_KEY", "")
        if raw_key:
            try:
                return Fernet(raw_key.encode())
            except Exception:
                warnings.warn(
                    "ENCRYPTION_KEY is set but is not a valid Fernet key. "
                    "Notes will be stored in plain text. "
                    'Generate a key with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"',
                    stacklevel=2,
                )
                return None
        else:
            warnings.warn(
                "ENCRYPTION_KEY is not set. MoodLog notes will be stored in plain text. "
                "Set ENCRYPTION_KEY to enable encryption at rest for sensitive data.",
                stacklevel=2,
            )
            return None
    except ImportError:
        warnings.warn(
            "cryptography package not installed; notes will be stored in plain text. "
            "Install with: pip install cryptography",
            stacklevel=2,
        )
        return None


_fernet = _build_fernet()


def encrypt_text(value: str | None) -> str | None:
    """Encrypt a string using Fernet, returning a base64-encoded ciphertext string.
    Returns the original value unchanged if encryption is unavailable.
    """
    if not value or _fernet is None:
        return value
    try:
        return _fernet.encrypt(value.encode("utf-8")).decode("ascii")
    except Exception:
        return value


def decrypt_text(value: str | None) -> str | None:
    """Decrypt a Fernet-encrypted string. Returns value unchanged if decryption unavailable or fails."""
    if not value or _fernet is None:
        return value
    try:
        return _fernet.decrypt(value.encode("ascii")).decode("utf-8")
    except Exception:
        # Value might be plain text from before encryption was enabled
        return value


def utcnow():
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    profile = db.relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    mood_logs = db.relationship(
        "MoodLog", back_populates="user", cascade="all, delete-orphan"
    )
    goals = db.relationship("Goal", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="scrypt")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"


class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    occupation = db.Column(db.String(100))
    preferred_activity = db.Column(
        db.String(50),
        nullable=False,
        default="Walk",
    )
    daily_reminder = db.Column(db.Boolean, default=False, nullable=False)
    # Accessibility: disables 3D orb simplex deformation and Chart.js animations
    calm_mode = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship("User", back_populates="profile")


class MoodLog(db.Model):
    __table_args__ = (
        db.UniqueConstraint("user_id", "log_date", name="uq_user_log_date"),
        db.Index("ix_moodlog_user_date", "user_id", db.text("log_date DESC")),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    log_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    mood_score = db.Column(db.Integer, nullable=False)
    sleep_hours = db.Column(db.Float, nullable=False)
    stress_level = db.Column(db.Integer, nullable=False)
    activity_done = db.Column(db.Boolean, nullable=False, default=False)
    social_interaction = db.Column(db.Integer, nullable=False)
    # Stored encrypted at rest when ENCRYPTION_KEY is set. Access via .notes property.
    _notes_encrypted = db.Column("notes", db.Text)
    sentiment_score = db.Column(db.Float, nullable=False, default=0.0)
    burnout_risk = db.Column(
        db.Enum("Low", "Medium", "High", name="burnout_risk_enum"),
        nullable=False,
        default="Low",
    )
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user = db.relationship("User", back_populates="mood_logs")
    suggestions = db.relationship(
        "Suggestion", back_populates="log", cascade="all, delete-orphan"
    )
    burnout_history = db.relationship(
        "BurnoutHistory", back_populates="log", cascade="all, delete-orphan"
    )

    @property
    def notes(self):
        """Return decrypted notes text."""
        return decrypt_text(self._notes_encrypted)

    @notes.setter
    def notes(self, value):
        """Encrypt and store notes text."""
        self._notes_encrypted = encrypt_text(value)

    @property
    def mood_label(self):
        mapping = {1: "Sick", 2: "Sad", 3: "Anxious", 4: "Calm", 5: "Happy"}
        return mapping.get(self.mood_score, str(self.mood_score))

    @property
    def mood_emoji(self):
        mapping = {1: "🤒", 2: "😢", 3: "😰", 4: "😌", 5: "😊"}
        return mapping.get(self.mood_score, "")


class BurnoutHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    log_id = db.Column(
        db.Integer,
        db.ForeignKey("mood_log.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    prediction = db.Column(db.String(10), nullable=False)
    confidence = db.Column(db.Float, nullable=False, default=0.0)
    algorithm_used = db.Column(db.String(50), nullable=False, default="Rules")
    predicted_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    # User feedback: did this prediction match their actual state?
    # None = not yet rated; True = accurate; False = inaccurate
    is_accurate = db.Column(db.Boolean, nullable=True)

    user = db.relationship("User")
    log = db.relationship("MoodLog", back_populates="burnout_history")


class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    log_id = db.Column(
        db.Integer,
        db.ForeignKey("mood_log.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    suggestion_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    user = db.relationship("User")
    log = db.relationship("MoodLog", back_populates="suggestions")


class Goal(db.Model):
    """User-defined personal wellness targets for sleep, mood, or activity frequency."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # target_type: 'sleep' | 'mood' | 'active_days' | 'journal_days' | 'stress'
    target_type = db.Column(db.String(30), nullable=False)
    target_value = db.Column(
        db.Float, nullable=False
    )  # e.g. 7.0 hours, mood score 4, 5 days
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    end_date = db.Column(db.Date, nullable=True)  # None = ongoing
    completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    user = db.relationship("User", back_populates="goals")

    @property
    def display_name(self):
        labels = {
            "sleep": "Sleep Duration Goal",
            "mood": "Average Mood Goal",
            "active_days": "Active Days Goal",
            "journal_days": "Journaling Streak Goal",
            "stress": "Stress Level Goal",
        }
        return labels.get(self.target_type, self.target_type.replace("_", " ").title())

    @property
    def unit(self):
        units = {
            "sleep": "hrs/night",
            "mood": "/5 avg",
            "active_days": "days/week",
            "journal_days": "days/week",
            "stress": "/5 or less",
        }
        return units.get(self.target_type, "")


class AuditLog(db.Model):
    """Records admin actions for compliance and accountability."""

    __tablename__ = "audit_log"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    action = db.Column(
        db.String(100), nullable=False
    )  # e.g. 'delete_user', 'toggle_role'
    target_type = db.Column(db.String(50), nullable=True)  # e.g. 'User', 'MoodLog'
    target_id = db.Column(db.Integer, nullable=True)
    detail = db.Column(db.Text, nullable=True)  # Free text or JSON snippet
    ip_address = db.Column(db.String(45), nullable=True)
    performed_at = db.Column(
        db.DateTime(timezone=True), default=utcnow, nullable=False, index=True
    )

    admin = db.relationship("User", foreign_keys=[admin_id])


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
