import os
import secrets
import warnings
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _bool_env(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    ENV = os.getenv("FLASK_ENV", "development")
    _SECRET_KEY = os.getenv("SECRET_KEY")
    if ENV == "production" and not _SECRET_KEY:
        raise RuntimeError("SECRET_KEY must be set to a strong random value in production.")
    SECRET_KEY = _SECRET_KEY or "dev-only-insecure-key"
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'daytone.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _bool_env("SESSION_COOKIE_SECURE", True)

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = _bool_env("MAIL_USE_TLS", True)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER") or MAIL_USERNAME
    ADMIN_ALERT_EMAIL = os.getenv("ADMIN_ALERT_EMAIL")
    ADMIN_REGISTRATION_CODE = os.getenv("ADMIN_REGISTRATION_CODE")
    if ADMIN_REGISTRATION_CODE and len(ADMIN_REGISTRATION_CODE) < 12:
        warnings.warn("ADMIN_REGISTRATION_CODE is too short.", stacklevel=2)

    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    COUNTRY = os.getenv("COUNTRY", "GLOBAL").upper()


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-daytone-secret"
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    RATELIMIT_ENABLED = False
    SESSION_COOKIE_SECURE = False
    ADMIN_REGISTRATION_CODE = os.getenv("TEST_ADMIN_REGISTRATION_CODE", secrets.token_hex(16))
