import json
from functools import wraps
from pathlib import Path

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, logout_user

from app.extensions import db, cache
from app.models import User, UserProfile
from app.utils.analytics import dashboard_data, platform_stats
from app.utils.audit import log_admin_action
from app.nlp.sentiment import get_sentiment_backend
from app.admin.forms import AdminUserProfileForm

from . import admin_bp

_ML_DIR = Path(__file__).resolve().parents[1] / "ml"


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    return render_template("admin/dashboard.html", stats=platform_stats())


@admin_bp.route("/users")
@admin_required
def users():
    q = request.args.get("q", "").strip()
    role_filter = request.args.get("role", "")
    query = User.query
    if q:
        query = query.filter(
            db.or_(User.name.ilike(f"%{q}%"), User.email.ilike(f"%{q}%"))
        )
    if role_filter in ("admin", "user"):
        query = query.filter(User.role == role_filter)
    all_users = query.order_by(User.created_at.desc()).all()
    return render_template(
        "admin/users.html", users=all_users, q=q, role_filter=role_filter
    )


@admin_bp.route("/user/<int:user_id>")
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    return render_template(
        "admin/user_detail.html", user=user
    )


@admin_bp.route("/user/<int:user_id>/toggle-role", methods=["POST"])
@admin_required
def toggle_role(user_id):
    user = User.query.get_or_404(user_id)
    is_self = user.id == current_user.id
    old_role = user.role
    user.role = "user" if user.role == "admin" else "admin"

    log_admin_action(
        admin_id=current_user.id,
        action="toggle_role",
        target_type="User",
        target_id=user.id,
        detail=f"{old_role} -> {user.role}",
    )
    db.session.commit()

    if is_self and user.role == "user":
        logout_user()
        flash("You have demoted yourself. You no longer have admin access.", "warning")
        return redirect(url_for("auth.login"))

    flash(f"{user.name} is now a {user.role}.", "success")
    return redirect(request.referrer or url_for("admin.users"))


@admin_bp.route("/user/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    is_self = user.id == current_user.id

    log_admin_action(
        admin_id=current_user.id,
        action="delete_user",
        target_type="User",
        target_id=user.id,
        detail=f"name={user.name!r} email={user.email!r}",
    )
    db.session.delete(user)
    db.session.commit()

    if is_self:
        logout_user()
        flash("Your admin account has been permanently deleted.", "info")
        return redirect(url_for("auth.register"))

    flash(f"User '{user.name}' has been deleted.", "danger")
    return redirect(url_for("admin.users"))


@admin_bp.route("/user/<int:user_id>/profile", methods=["GET", "POST"])
@admin_required
def edit_user_profile(user_id):
    user = User.query.get_or_404(user_id)
    profile = user.profile
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        db.session.flush()

    form = AdminUserProfileForm()
    if request.method == "GET":
        form.name.data = user.name
        form.email.data = user.email
        form.role.data = user.role
        form.age.data = profile.age
        form.gender.data = profile.gender
        form.occupation.data = profile.occupation
        form.preferred_activity.data = profile.preferred_activity
        form.daily_reminder.data = profile.daily_reminder

    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if existing and existing.id != user.id:
            flash("An account with that email already exists.", "danger")
            return render_template("admin/edit_profile.html", user=user, form=form)

        user.name = form.name.data.strip()
        user.email = form.email.data.lower().strip()

        role_changed_self = user.id == current_user.id and form.role.data == "user"
        user.role = form.role.data

        profile.age = form.age.data
        profile.gender = form.gender.data
        profile.occupation = (
            form.occupation.data.strip() if form.occupation.data else None
        )
        profile.preferred_activity = form.preferred_activity.data
        profile.daily_reminder = form.daily_reminder.data

        db.session.commit()
        cache.delete_memoized(dashboard_data, user.id)

        if role_changed_self:
            logout_user()
            flash(
                "You have demoted yourself. You no longer have admin access.", "warning"
            )
            return redirect(url_for("auth.login"))

        flash(f"Profile for {user.name} has been updated.", "success")
        return redirect(url_for("admin.user_detail", user_id=user.id))

    return render_template("admin/edit_profile.html", user=user, form=form)


@admin_bp.route("/model")
@admin_required
def model_diagnostics():
    """ML diagnostics page: confusion matrix, per-class metrics, and known limitations."""
    metrics = {}
    meta = {}
    error = None

    try:
        metrics_path = _ML_DIR / "model_metrics.json"
        meta_path = _ML_DIR / "model_meta.json"
        if metrics_path.exists():
            metrics = json.loads(metrics_path.read_text())
        if meta_path.exists():
            meta = json.loads(meta_path.read_text())
    except Exception as exc:
        error = str(exc)

    classes = ["High", "Low", "Medium"]
    sentiment_backend = get_sentiment_backend()

    return render_template(
        "admin/model.html",
        metrics=metrics,
        meta=meta,
        classes=classes,
        sentiment_backend=sentiment_backend,
        error=error,
        stats=platform_stats(),
    )


@admin_bp.route("/ml/bias-audit")
@admin_required
def bias_audit():
    """Run the ML bias & fairness audit script and display results inline."""
    import subprocess
    import sys
    from flask import current_app

    script = Path(current_app.root_path).parent / "scripts" / "bias_audit.py"
    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(Path(current_app.root_path).parent),
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = result.stdout or ""
        if result.returncode != 0:
            output += "\n[STDERR]\n" + result.stderr
    except subprocess.TimeoutExpired:
        output = "[ERROR] Audit timed out after 120 seconds."
    except Exception as exc:
        output = f"[ERROR] {exc}"

    return render_template("admin/bias_audit.html", output=output)


@admin_bp.route("/audit-log")
@admin_required
def audit_log():
    """View recent admin audit log entries."""
    from app.models import AuditLog

    entries = AuditLog.query.order_by(AuditLog.performed_at.desc()).limit(200).all()
    return render_template("admin/audit_log.html", entries=entries)
