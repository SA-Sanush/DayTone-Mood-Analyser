import logging
import os
import warnings

from flask import Flask, jsonify
from flask_talisman import Talisman
try:
    from flask_migrate import Migrate
except ImportError:  # pragma: no cover
    class Migrate:
        def init_app(self, app, db):
            app.logger.warning("Flask-Migrate is not installed; migration commands are unavailable.")

from config import Config

from .extensions import db, limiter, login_manager, mail, cache, csrf


migrate = Migrate()


def validate_runtime_config(app):
    if app.config.get("TESTING"):
        return

    if app.config.get("ENV") != "production":
        admin_code = app.config.get("ADMIN_REGISTRATION_CODE")
        if admin_code and len(admin_code) < 12:
            warnings.warn("ADMIN_REGISTRATION_CODE is too short.", stacklevel=2)
        return

    secret_key = app.config.get("SECRET_KEY")
    if not secret_key or secret_key in {"dev-only-insecure-key", "dev-daytone-secret", "change-me"}:
        raise RuntimeError("SECRET_KEY must be set to a strong private value in production.")

    if app.config.get("RATELIMIT_STORAGE_URI") == "memory://":
        raise RuntimeError("RATELIMIT_STORAGE_URI must use shared storage such as Redis in production.")

    database_url = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if database_url.startswith("sqlite:") or database_url.endswith(".db"):
        raise RuntimeError("DATABASE_URL must not use SQLite in production.")

    mail_username = app.config.get("MAIL_USERNAME")
    mail_password = app.config.get("MAIL_PASSWORD")
    if bool(mail_username) != bool(mail_password):
        warnings.warn("MAIL_USERNAME and MAIL_PASSWORD should be set together.", stacklevel=2)

    admin_code = app.config.get("ADMIN_REGISTRATION_CODE")
    if not admin_code:
        raise RuntimeError("ADMIN_REGISTRATION_CODE must be set when admin routes are enabled.")
    if len(admin_code) < 16:
        raise RuntimeError("ADMIN_REGISTRATION_CODE must be at least 16 characters in production.")
    if admin_code and not app.config.get("ADMIN_ALERT_EMAIL"):
        warnings.warn("ADMIN_ALERT_EMAIL should be set when admin registration is enabled.", stacklevel=2)


def create_app(config_object=Config):
    if config_object.ENV == "production":
        from pythonjsonlogger import jsonlogger
        # Clear default handlers to prevent duplicate logging output
        for h in logging.getLogger().handlers[:]:
            logging.getLogger().removeHandler(h)
        handler = logging.StreamHandler()
        handler.setFormatter(jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    validate_runtime_config(app)
    app.instance_path and os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)

    # Initialize Talisman with CSP
    Talisman(
        app,
        content_security_policy={
            "default-src": "'self'",
            "script-src": ["'self'", "cdn.jsdelivr.net", "unpkg.com", "'unsafe-inline'"],
            "style-src": ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "fonts.googleapis.com"],
            "font-src": ["'self'", "fonts.gstatic.com"],
            "img-src": ["'self'", "data:"],
        },
        force_https=(config_object.ENV == "production"),
    )

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    from .auth.routes import auth_bp
    from .mood.routes import mood_bp
    from .admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(mood_bp)
    app.register_blueprint(admin_bp)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.cli.command("reload-model")
    def reload_model():
        from app.ml.predictor import _model_payload

        _model_payload.cache_clear()
        print("Model cache cleared. Next prediction will load the current artifact.")

    return app
