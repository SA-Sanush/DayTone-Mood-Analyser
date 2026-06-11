import hashlib
from urllib.parse import urlparse

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from flask_limiter.util import get_remote_address

from app.extensions import db, limiter
from app.models import User, UserProfile

from . import auth_bp
from .forms import LoginForm, RegistrationForm


def safe_next_url(next_url):
    if not next_url:
        return None

    parsed = urlparse(next_url)
    if parsed.scheme or parsed.netloc or not next_url.startswith("/") or next_url.startswith("//"):
        return None
    return next_url


def _login_limit_key():
    if request.method == "POST":
        email = (request.form.get("email") or "").lower().strip()
        return f"{email}:{get_remote_address()}"
    return get_remote_address()


@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("mood.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per hour")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("mood.dashboard"))

    form = RegistrationForm()
    show_admin = request.args.get("admin") == "1"
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower()).first()
        if existing:
            flash("An account with that email already exists.", "danger")
            return render_template("auth/register.html", form=form, show_admin=show_admin)

        admin_code = current_app.config.get("ADMIN_REGISTRATION_CODE")
        wants_admin = bool(admin_code and form.admin_code.data and form.admin_code.data == admin_code)
        user = User(
            name=form.name.data.strip(),
            email=form.email.data.lower().strip(),
            role="admin" if wants_admin else "user",
        )
        user.set_password(form.password.data)
        user.profile = UserProfile(
            age=form.age.data,
            gender=form.gender.data or None,
            occupation=(form.occupation.data or "").strip() or None,
            preferred_activity=form.preferred_activity.data or "Walk",
            daily_reminder=form.daily_reminder.data,
        )
        db.session.add(user)
        db.session.commit()
        flash("Welcome to DayTone. You can sign in now.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form, show_admin=show_admin)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", key_func=_login_limit_key)
def login():
    if current_user.is_authenticated:
        return redirect(url_for("mood.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash("Signed in successfully.", "success")
            next_url = request.args.get("next")
            return redirect(safe_next_url(next_url) or url_for("mood.dashboard"))
        email_hash = hashlib.sha256(form.email.data.lower().strip().encode("utf-8")).hexdigest()[:12]
        current_app.logger.info("Failed login attempt email_hash=%s", email_hash)
        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))
