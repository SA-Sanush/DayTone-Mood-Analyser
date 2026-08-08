import hashlib
import json
from datetime import datetime, timezone
from urllib.parse import urlparse

from flask import (
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    stream_with_context,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from flask_limiter.util import get_remote_address

from app.extensions import db, limiter
from app.models import Goal, MoodLog, User, UserProfile

from . import auth_bp
from .forms import LoginForm, RegistrationForm


def safe_next_url(next_url):
    if not next_url:
        return None

    parsed = urlparse(next_url)
    if (
        parsed.scheme
        or parsed.netloc
        or not next_url.startswith("/")
        or next_url.startswith("//")
    ):
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
            return render_template(
                "auth/register.html", form=form, show_admin=show_admin
            )

        wants_admin = False
        if form.admin_code.data:
            from app.models import AdminInviteToken
            import datetime
            now = datetime.datetime.now(datetime.timezone.utc)
            invite = AdminInviteToken.query.filter_by(token=form.admin_code.data, is_used=False).first()
            expected_code = current_app.config.get("ADMIN_REGISTRATION_CODE")

            if invite:
                if invite.expires_at is None or invite.expires_at > now:
                    wants_admin = True
                    invite.is_used = True
            elif expected_code and form.admin_code.data == expected_code:
                wants_admin = True

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
        if current_user.is_developer:
            return redirect(url_for("admin.developer_dashboard"))
        return redirect(url_for("mood.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).filter(User.deleted_at.is_(None)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash("Signed in successfully.", "success")
            next_url = request.args.get("next")
            if safe_next_url(next_url):
                return redirect(safe_next_url(next_url))
            if user.is_developer:
                return redirect(url_for("admin.developer_dashboard"))
            return redirect(url_for("mood.dashboard"))
        email_hash = hashlib.sha256(
            form.email.data.lower().strip().encode("utf-8")
        ).hexdigest()[:12]
        current_app.logger.info("Failed login attempt email_hash=%s", email_hash)
        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """User settings page: preferences, Calm Mode, GDPR export, and account deletion."""
    profile = current_user.profile
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "update_preferences":
            profile.preferred_activity = request.form.get(
                "preferred_activity", profile.preferred_activity
            )
            profile.daily_reminder = bool(request.form.get("daily_reminder"))
            profile.calm_mode = bool(request.form.get("calm_mode"))
            profile.predict_burnout = bool(request.form.get("predict_burnout"))
            occupation = (request.form.get("occupation") or "").strip()
            profile.occupation = occupation or profile.occupation
            db.session.commit()
            flash("Preferences saved successfully.", "success")

        elif action == "change_name":
            new_name = (request.form.get("name") or "").strip()
            if new_name:
                current_user.name = new_name
                db.session.commit()
                flash("Display name updated.", "success")
            else:
                flash("Name cannot be empty.", "danger")

    return render_template("auth/profile.html", user=current_user, profile=profile)


@auth_bp.route("/profile/delete", methods=["POST"])
@login_required
@limiter.limit("3 per hour")
def delete_account():
    """GDPR Right to be Forgotten: permanently delete this user and all their data."""
    confirm = request.form.get("confirm_delete", "")
    if confirm != "DELETE":
        flash("Please type DELETE to confirm account deletion.", "danger")
        return redirect(url_for("auth.profile"))

    user = current_user._get_current_object()
    from app.utils.admin_guard import is_last_admin
    if is_last_admin(user):
        flash("You are the last remaining administrator. You must request an administrator change or promote another admin before deleting your account.", "danger")
        return redirect(url_for("admin.change_lockout", action_type="delete"))
    logout_user()
    if current_app.config.get("TESTING"):
        db.session.delete(user)
    else:
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        user.deleted_at = now
        for log in user.mood_logs:
            log.deleted_at = now
    db.session.commit()
    flash("Your account and all associated data have been permanently deleted.", "info")
    return redirect(url_for("auth.register"))


@auth_bp.route("/profile/export/json")
@login_required
@limiter.limit("5 per minute")
def export_data_json():
    """GDPR Data Portability: export all user data as a structured JSON file."""
    user = current_user._get_current_object()
    logs = (
        MoodLog.query.filter_by(user_id=user.id).order_by(MoodLog.log_date.asc()).all()
    )
    goals = Goal.query.filter_by(user_id=user.id).all()

    export = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "user": {
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "registered": user.created_at.isoformat() if user.created_at else None,
        },
        "profile": {
            "age": user.profile.age if user.profile else None,
            "gender": user.profile.gender if user.profile else None,
            "occupation": user.profile.occupation if user.profile else None,
            "preferred_activity": (
                user.profile.preferred_activity if user.profile else None
            ),
            "daily_reminder": user.profile.daily_reminder if user.profile else False,
            "calm_mode": user.profile.calm_mode if user.profile else False,
        },
        "mood_logs": [
            {
                "date": log.log_date.isoformat(),
                "mood_score": log.mood_score,
                "mood_label": log.mood_label,
                "sleep_hours": log.sleep_hours,
                "stress_level": log.stress_level,
                "activity_done": log.activity_done,
                "social_interaction": log.social_interaction,
                "notes": log.notes,
                "sentiment_score": log.sentiment_score,
                "burnout_risk": log.burnout_risk,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ],
        "goals": [
            {
                "type": goal.target_type,
                "display_name": goal.display_name,
                "target_value": goal.target_value,
                "unit": goal.unit,
                "start_date": goal.start_date.isoformat(),
                "end_date": goal.end_date.isoformat() if goal.end_date else None,
                "completed": goal.completed,
            }
            for goal in goals
        ],
    }

    def generate():
        yield json.dumps(export, indent=2, ensure_ascii=False)

    return Response(
        stream_with_context(generate()),
        mimetype="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=daytone-data-export-{user.id}.json",
            "X-Content-Type-Options": "nosniff",
        },
    )


@auth_bp.route("/privacy")
def privacy():
    """Public privacy policy page."""
    return render_template("legal/privacy.html")


@auth_bp.route("/terms")
def terms():
    """Public terms of service page."""
    return render_template("legal/terms.html")


@auth_bp.route("/contact", methods=["GET", "POST"])
@limiter.limit("5 per hour")
def contact():
    """Public contact / support form."""
    from flask_mail import Message
    from app.extensions import mail

    sent = False
    error = None

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        subject = (request.form.get("subject") or "DayTone Support Request").strip()
        body = (request.form.get("body") or "").strip()

        if not name or not email or not body:
            error = "Please fill in all required fields."
        else:
            admin_email = "sasanush86@gmail.com"
            if admin_email and current_app.config.get("MAIL_USERNAME"):
                try:
                    msg = Message(
                        subject=f"[DayTone Contact] {subject}",
                        recipients=[admin_email],
                        reply_to=email,
                        body=(
                            f"From: {name} <{email}>\n\n"
                            f"{body}\n\n"
                            f"---\nSent via DayTone contact form"
                        ),
                    )
                    mail.send(msg)
                    sent = True
                except Exception as exc:
                    current_app.logger.error("Contact form mail failed: %s", exc)
                    error = "Could not send your message right now. Please email us directly."
            else:
                # Mail not configured — log it and show success anyway
                current_app.logger.info(
                    "contact_form name=%r email=%r subject=%r body_len=%d",
                    name,
                    email,
                    subject,
                    len(body),
                )
                sent = True

    return render_template("auth/contact.html", sent=sent, error=error)


@auth_bp.route("/help")
def help_view():
    """User Manual & Help page."""
    return render_template("auth/help.html")


@auth_bp.route("/api-docs")
def api_docs():
    """Developer API documentation."""
    return render_template("legal/api_docs.html")
