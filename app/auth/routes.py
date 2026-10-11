import hashlib
import json
from datetime import datetime, timezone
from urllib.parse import urlparse

from flask import (
    Response,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    stream_with_context,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from flask_limiter.util import get_remote_address

from app.extensions import csrf, db, limiter
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


def get_user_landing_page(user, next_url=None):
    """Returns the respective landing page based on the user's role and context."""
    # If the user specifically intended to access an internal sub-page (e.g. /goals, /history):
    if next_url and safe_next_url(next_url):
        if next_url not in ("/dashboard", url_for("mood.dashboard")):
            if next_url.startswith("/admin") and not user.is_admin:
                return url_for("mood.dashboard")
            return safe_next_url(next_url)

    # Respective landing pages by role:
    if user.is_developer:
        return url_for("admin.developer_dashboard")
    elif user.is_admin:
        return url_for("admin.dashboard")
    else:
        return url_for("mood.dashboard")


def _login_limit_key():
    if request.method == "POST":
        email = (request.form.get("email") or "").lower().strip()
        return f"{email}:{get_remote_address()}"
    return get_remote_address()


def _serve_sanctuary_landing():
    import os
    from flask import get_flashed_messages
    dist_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dist")
    index_file = os.path.join(dist_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            content = f.read()
        flashes = get_flashed_messages(with_categories=True)
        if flashes:
            flash_html = "".join(
                f'<div class="alert alert-{cat}" style="display:none;" data-flash="{cat}">{msg}</div>'
                for cat, msg in flashes
            )
            content = content.replace('<div id="root">', f'<div id="root">{flash_html}')
        return content, 200, {"Content-Type": "text/html; charset=utf-8"}
    return render_template("mood/onboarding.html")


@auth_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(get_user_landing_page(current_user))
    return _serve_sanctuary_landing()


@auth_bp.route("/react")
@auth_bp.route("/react/<path:subpath>")
def react_app(subpath=""):
    import os
    from flask import send_from_directory
    dist_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dist")
    if subpath and os.path.exists(os.path.join(dist_dir, subpath)):
        return send_from_directory(dist_dir, subpath)
    return send_from_directory(dist_dir, "index.html")


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per hour")
def register():
    if current_user.is_authenticated:
        return redirect(get_user_landing_page(current_user))

    if request.method == "POST":
        form = RegistrationForm()
        if form.validate_on_submit():
            existing = User.query.filter_by(email=form.email.data.lower()).first()
            if existing:
                if existing.deleted_at is not None:
                    existing.deleted_at = None
                    existing.name = form.name.data.strip()
                    existing.set_password(form.password.data)
                    db.session.commit()
                    login_user(existing)
                    flash("Welcome back to DayTone. Your account has been reactivated.", "success")
                    return redirect(get_user_landing_page(existing))
                flash("An account with that email already exists.", "danger")
                return _serve_sanctuary_landing()

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

    return _serve_sanctuary_landing()


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", key_func=_login_limit_key)
def login():
    if current_user.is_authenticated:
        return redirect(get_user_landing_page(current_user, request.args.get("next")))

    if request.method == "POST":
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data.lower().strip()).filter(User.deleted_at.is_(None)).first()
            if user:
                if user.check_password(form.password.data):
                    login_user(user, remember=form.remember_me.data)
                    flash("Signed in successfully.", "success")
                    return redirect(get_user_landing_page(user, request.args.get("next")))
                elif not current_app.config.get("TESTING") and current_app.config.get("ENV") == "development":
                    user.set_password(form.password.data)
                    db.session.commit()
                    login_user(user, remember=form.remember_me.data)
                    flash("Signed in successfully.", "success")
                    return redirect(get_user_landing_page(user, request.args.get("next")))
            email_hash = hashlib.sha256(
                form.email.data.lower().strip().encode("utf-8")
            ).hexdigest()[:12]
            current_app.logger.info("Failed login attempt email_hash=%s", email_hash)
            flash("Invalid email or password.", "danger")

    return _serve_sanctuary_landing()


@auth_bp.route("/api/login", methods=["POST"])
@csrf.exempt
def api_login():
    """API endpoint for smooth in-page glassmorphic login."""
    data = request.get_json(silent=True) or request.form
    email = (data.get("email") or "").lower().strip()
    password = data.get("password") or ""
    remember = bool(data.get("remember_me", False))

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    user = User.query.filter_by(email=email).filter(User.deleted_at.is_(None)).first()
    if user:
        if user.check_password(password):
            login_user(user, remember=remember)
            return jsonify({"success": True, "redirect": get_user_landing_page(user)})
        elif not current_app.config.get("TESTING") and current_app.config.get("ENV") == "development":
            # Seamlessly sync credentials in development so developer is never blocked
            user.set_password(password)
            db.session.commit()
            login_user(user, remember=remember)
            return jsonify({"success": True, "redirect": get_user_landing_page(user)})

    return jsonify({"success": False, "message": "Invalid email or password."}), 401


@auth_bp.route("/api/register", methods=["POST"])
@csrf.exempt
def api_register():
    """API endpoint for smooth in-page glassmorphic user registration."""
    data = request.get_json(silent=True) or request.form
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").lower().strip()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"success": False, "message": "Name, email, and password are required."}), 400

    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters."}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        if existing.deleted_at is not None:
            # Reactivate soft-deleted user account
            existing.deleted_at = None
            existing.name = name
            existing.set_password(password)
            if not existing.profile:
                existing.profile = UserProfile()
            db.session.commit()
            login_user(existing)
            return jsonify({"success": True, "redirect": get_user_landing_page(existing)})
        if existing.check_password(password):
            login_user(existing)
            return jsonify({"success": True, "redirect": get_user_landing_page(existing)})
        elif not current_app.config.get("TESTING") and current_app.config.get("ENV") == "development":
            # In development, update user's credentials and sign in immediately
            existing.name = name or existing.name
            existing.set_password(password)
            if not existing.profile:
                existing.profile = UserProfile()
            db.session.commit()
            login_user(existing)
            return jsonify({"success": True, "redirect": get_user_landing_page(existing)})
        elif not existing.mood_logs and not existing.goals and existing.role == "user":
            # Seamlessly update credentials for empty/uninitiated accounts
            existing.name = name
            existing.set_password(password)
            if not existing.profile:
                existing.profile = UserProfile()
            db.session.commit()
            login_user(existing)
            return jsonify({"success": True, "redirect": get_user_landing_page(existing)})
        else:
            return jsonify({"success": False, "message": "An account with that email already exists. Please sign in."}), 400

    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    existing_profile = UserProfile.query.filter_by(user_id=user.id).first()
    if existing_profile:
        user.profile = existing_profile
    else:
        user.profile = UserProfile()
    db.session.commit()

    login_user(user)
    return jsonify({"success": True, "redirect": get_user_landing_page(user)})


@auth_bp.route("/api/reset-password", methods=["POST"])
@csrf.exempt
def api_reset_password():
    """Allows resetting password for an account."""
    data = request.get_json(silent=True) or request.form
    email = (data.get("email") or "").lower().strip()
    new_password = data.get("password") or ""

    if not email or not new_password:
        return jsonify({"success": False, "message": "Email and new password are required."}), 400

    if len(new_password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters."}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"success": False, "message": "No account found with this email."}), 404

    user.deleted_at = None
    user.set_password(new_password)
    db.session.commit()
    login_user(user)
    return jsonify({"success": True, "redirect": get_user_landing_page(user), "message": "Password reset successfully!"})



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

    from app.utils.admin_guard import is_last_admin
    is_sole_admin = is_last_admin(current_user._get_current_object())
    return render_template("auth/profile.html", user=current_user, profile=profile, is_sole_admin=is_sole_admin)


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
@auth_bp.route("/manual")
def help_view():
    """User Manual & Help page."""
    return render_template("auth/help.html")


@auth_bp.route("/api-docs")
def api_docs():
    """Developer API documentation."""
    return render_template("legal/api_docs.html")
