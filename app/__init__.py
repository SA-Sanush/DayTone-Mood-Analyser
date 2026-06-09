from flask import Flask

from config import Config

from .extensions import db, limiter, login_manager, mail


def create_app(config_object=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    app.instance_path and __import__("os").makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    from .auth.routes import auth_bp
    from .mood.routes import mood_bp
    from .admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(mood_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

    return app
