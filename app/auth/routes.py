from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app.extensions import db, limiter
from app.models import User, UserProfile

from . import auth_bp
from .forms import LoginForm, RegistrationForm


@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("mood.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("mood.dashboard"))

    form = RegistrationForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower()).first()
        if existing:
            flash("An account with that email already exists.", "danger")
            return render_template("auth/register.html", form=form)

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
        )
        db.session.add(user)
        db.session.commit()
        flash("Welcome to DayTone. You can sign in now.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("mood.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Signed in successfully.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("mood.dashboard"))
        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))
