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
    if current_user.is_developer:
        return redirect(url_for("admin.developer_dashboard"))
    return render_template("admin/dashboard.html", stats=platform_stats())


@admin_bp.route("/users")
@admin_required
def users():
    q = request.args.get("q", "").strip()
    role_filter = request.args.get("role", "")
    query = User.query.filter(User.deleted_at.is_(None))
    if q:
        query = query.filter(
            db.or_(User.name.ilike(f"%{q}%"), User.email.ilike(f"%{q}%"))
        )
    if role_filter in ("admin", "user", "developer"):
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
    if user.role == "developer" and not current_user.is_developer:
        flash("Only developers can modify developer accounts.", "danger")
        return redirect(url_for("admin.users"))

    is_self = user.id == current_user.id
    old_role = user.role

    if old_role in ("admin", "developer"):
        from app.utils.admin_guard import is_last_admin
        if is_last_admin(user):
            flash("Cannot demote the last remaining administrator. You must request a change or promote another admin first.", "danger")
            return redirect(url_for("admin.change_lockout", action_type="demote"))

    user.role = "user" if user.role in ("admin", "developer") else "admin"

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
    if user.role == "developer" and not current_user.is_developer:
        flash("Only developers can delete developer accounts.", "danger")
        return redirect(url_for("admin.users"))

    is_self = user.id == current_user.id

    if user.role in ("admin", "developer"):
        from app.utils.admin_guard import is_last_admin
        if is_last_admin(user):
            flash("Cannot delete the last remaining administrator. You must request a change or promote another admin first.", "danger")
            return redirect(url_for("admin.change_lockout", action_type="delete"))

    log_admin_action(
        admin_id=current_user.id,
        action="delete_user",
        target_type="User",
        target_id=user.id,
        detail=f"name={user.name!r} email={user.email!r}",
    )
    from flask import current_app
    if current_app.config.get("TESTING"):
        db.session.delete(user)
    else:
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        user.deleted_at = now
        for log in user.mood_logs:
            log.deleted_at = now
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
    if user.role == "developer" and not current_user.is_developer:
        flash("Only developers can edit developer accounts.", "danger")
        return redirect(url_for("admin.users"))

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
        if form.role.data == "developer" and not current_user.is_developer:
            flash("Only developers can assign the developer role.", "danger")
            return render_template("admin/edit_profile.html", user=user, form=form)

        existing = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if existing and existing.id != user.id:
            flash("An account with that email already exists.", "danger")
            return render_template("admin/edit_profile.html", user=user, form=form)

        user.name = form.name.data.strip()
        user.email = form.email.data.lower().strip()

        role_demoted = user.role in ("admin", "developer") and form.role.data not in ("admin", "developer")
        if role_demoted:
            from app.utils.admin_guard import is_last_admin
            if is_last_admin(user):
                flash("Cannot demote the last remaining administrator. You must request a change or promote another admin first.", "danger")
                return redirect(url_for("admin.change_lockout", action_type="demote"))

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


@admin_bp.route("/invite-tokens", methods=["GET", "POST"])
@admin_required
def invite_tokens():
    """Create and view admin registration invite tokens."""
    import secrets
    from datetime import datetime, timezone, timedelta
    from app.models import AdminInviteToken

    if request.method == "POST":
        token = "admin-" + secrets.token_hex(16)
        # Expires in 7 days
        expires = datetime.now(timezone.utc) + timedelta(days=7)
        invite = AdminInviteToken(token=token, expires_at=expires)
        db.session.add(invite)
        db.session.commit()
        log_admin_action(
            admin_id=current_user.id,
            action="create_invite_token",
            target_type="AdminInviteToken",
            target_id=invite.id,
            detail=f"Generated invite token expiring on {expires.isoformat()}"
        )
        flash("Invite token generated successfully!", "success")
        return redirect(url_for("admin.invite_tokens"))

    tokens = AdminInviteToken.query.order_by(AdminInviteToken.created_at.desc()).all()
    return render_template("admin/invite_tokens.html", tokens=tokens)


def developer_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_developer:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@admin_bp.route("/change-lockout")
@login_required
def change_lockout():
    action_type = request.args.get("action_type", "demote")
    # Fetch regular users who can be promoted (role == 'user')
    from app.models import User
    users = User.query.filter_by(role="user", deleted_at=None).all()
    return render_template(
        "admin/change_lockout.html",
        action_type=action_type,
        users=users
    )


@admin_bp.route("/change-request/submit", methods=["POST"])
@login_required
def submit_change_request():
    from app.models import User, AdminChangeRequest
    from app.utils.admin_guard import is_last_admin
    import secrets

    # Requester must be current_user and must be the last admin
    if not current_user.role in ("admin", "developer") or not is_last_admin(current_user):
        flash("You are not locked out; you can perform role changes directly.", "warning")
        return redirect(url_for("admin.dashboard"))

    action_type = request.form.get("action_type", "demote")
    target_user_id = request.form.get("target_user_id")

    if not target_user_id:
        flash("Please select a trusted user to promote to administrator.", "danger")
        return redirect(url_for("admin.change_lockout", action_type=action_type))

    target_user = User.query.get_or_404(int(target_user_id))
    if target_user.role in ("admin", "developer"):
        flash("The selected user is already an administrator.", "danger")
        return redirect(url_for("admin.change_lockout", action_type=action_type))

    request_type = "demote_self" if action_type == "demote" else "delete_account"

    # Check for existing pending request by this user
    existing = AdminChangeRequest.query.filter_by(
        requester_id=current_user.id,
        status="pending"
    ).first()
    if existing:
        # Update existing request
        existing.target_user_id = target_user.id
        existing.request_type = request_type
        existing.token = secrets.token_hex(24)
        req = existing
    else:
        req = AdminChangeRequest(
            requester_id=current_user.id,
            target_user_id=target_user.id,
            request_type=request_type,
            token=secrets.token_hex(24),
            status="pending"
        )
        db.session.add(req)

    db.session.commit()

    # Generate approval and rejection URLs
    approve_url = url_for("admin.approve_change_request", token=req.token, _external=True)
    reject_url = url_for("admin.reject_change_request", token=req.token, _external=True)

    from app.utils.mailer import send_admin_change_request_email
    mail_sent = send_admin_change_request_email(req, approve_url, reject_url)

    if mail_sent:
        flash("Admin change request submitted. An approval email has been sent to the developer.", "success")
    else:
        # If mail server is not configured or fails, log URLs and display them in dev mode
        from flask import current_app
        current_app.logger.info("Admin Change Request Created:\nApprove: %s\nReject: %s", approve_url, reject_url)
        if current_app.config.get("ENV") != "production":
            flash(f"Request submitted! (Dev mode bypass - Approve URL: {approve_url})", "success")
        else:
            flash("Request submitted, but the email notification could not be sent. Please contact the developer directly.", "warning")

    return redirect(url_for("admin.change_lockout", action_type=action_type))


def process_admin_change_request(req):
    from datetime import datetime, timezone
    from app.models import User
    from app.utils.audit import log_admin_action

    # 1. Promote target user to admin
    target = User.query.get(req.target_user_id)
    if target:
        old_role = target.role
        target.role = "admin"
        log_admin_action(
            admin_id=req.requester_id,
            action="toggle_role",
            target_type="User",
            target_id=target.id,
            detail=f"Approved admin promotion: {old_role} -> {target.role}",
        )

    # 2. Perform demotion or deletion on requester
    requester = User.query.get(req.requester_id)
    if requester:
        if req.request_type == "demote_self":
            old_role = requester.role
            requester.role = "user"
            log_admin_action(
                admin_id=requester.id,
                action="toggle_role",
                target_type="User",
                target_id=requester.id,
                detail=f"Approved self-demotion: {old_role} -> {requester.role}",
            )
        elif req.request_type == "delete_account":
            log_admin_action(
                admin_id=requester.id,
                action="delete_user",
                target_type="User",
                target_id=requester.id,
                detail=f"Approved account deletion: name={requester.name!r} email={requester.email!r}",
            )
            from flask import current_app
            if current_app.config.get("TESTING"):
                db.session.delete(requester)
            else:
                now = datetime.now(timezone.utc)
                requester.deleted_at = now
                for log in requester.mood_logs:
                    log.deleted_at = now

    req.status = "approved"
    req.resolved_at = datetime.now(timezone.utc)
    db.session.commit()


@admin_bp.route("/change-request/<token>/approve")
def approve_change_request(token):
    from app.models import AdminChangeRequest
    req = AdminChangeRequest.query.filter_by(token=token, status="pending").first_or_404()
    
    process_admin_change_request(req)
    
    # If the requester was the logged in user, log them out if they demoted themselves
    if current_user.is_authenticated and current_user.id == req.requester_id:
        logout_user()
        flash("Your request has been approved. You have been demoted and logged out.", "warning")
        return redirect(url_for("auth.login"))

    flash("The administrator change request has been successfully approved.", "success")
    return redirect(url_for("auth.login"))


@admin_bp.route("/change-request/<token>/reject")
def reject_change_request(token):
    from app.models import AdminChangeRequest
    from datetime import datetime, timezone
    req = AdminChangeRequest.query.filter_by(token=token, status="pending").first_or_404()

    req.status = "rejected"
    req.resolved_at = datetime.now(timezone.utc)
    db.session.commit()

    flash("The administrator change request has been rejected.", "info")
    return redirect(url_for("auth.login"))


@admin_bp.route("/developer/dashboard")
@developer_required
def developer_dashboard():
    from app.models import User, AdminChangeRequest, AuditLog, MoodLog, Goal, AdminInviteToken
    import sys
    from flask import current_app

    total_users = User.query.filter(User.deleted_at.is_(None)).count()
    admin_count = User.query.filter_by(role="admin", deleted_at=None).count()
    developer_count = User.query.filter_by(role="developer", deleted_at=None).count()
    
    pending_requests = AdminChangeRequest.query.filter_by(status="pending").count()
    total_requests = AdminChangeRequest.query.count()
    
    total_mood_logs = MoodLog.query.filter(MoodLog.deleted_at.is_(None)).count()
    total_goals = Goal.query.count()
    total_audit_logs = AuditLog.query.count()
    
    p_stats = platform_stats()

    system_info = {
        "python_version": sys.version.split()[0],
        "database": current_app.config.get("SQLALCHEMY_DATABASE_URI", "").split(":")[0],
        "mail_server": current_app.config.get("MAIL_SERVER"),
        "mail_configured": "Yes" if current_app.config.get("MAIL_USERNAME") else "No",
        "cache_type": current_app.config.get("CACHE_TYPE"),
        "ratelimit_storage": current_app.config.get("RATELIMIT_STORAGE_URI", "").split(":")[0],
        "sentiment_backend": get_sentiment_backend().__class__.__name__,
    }

    stats = {
        "total_users": total_users,
        "admin_count": admin_count,
        "developer_count": developer_count,
        "pending_requests": pending_requests,
        "total_requests": total_requests,
        "total_mood_logs": total_mood_logs,
        "total_goals": total_goals,
        "total_audit_logs": total_audit_logs,
        "active_users": p_stats.get("active_users", 0),
        "high_risk_users": p_stats.get("high_risk_users", 0),
        "avg_mood": p_stats.get("avg_mood", 0),
        "avg_sleep": p_stats.get("avg_sleep", 0),
        "burnout_distribution": p_stats.get("burnout_distribution", {"Low": 0, "Medium": 0, "High": 0}),
    }

    recent_users = User.query.filter(User.deleted_at.is_(None)).order_by(User.created_at.desc()).limit(8).all()
    recent_tokens = AdminInviteToken.query.order_by(AdminInviteToken.created_at.desc()).limit(5).all()

    recent_audit_logs = (
        AuditLog.query
        .filter(AuditLog.action.in_(["toggle_role", "delete_user", "admin_change_request", "approve_admin_change", "reject_admin_change"]))
        .order_by(AuditLog.performed_at.desc())
        .limit(15)
        .all()
    )

    requests = AdminChangeRequest.query.order_by(AdminChangeRequest.created_at.desc()).all()
    return render_template(
        "admin/developer_dashboard.html",
        requests=requests,
        stats=stats,
        system_info=system_info,
        recent_audit_logs=recent_audit_logs,
        recent_users=recent_users,
        recent_tokens=recent_tokens,
    )


@admin_bp.route("/developer/requests")
@developer_required
def developer_requests():
    return redirect(url_for("admin.developer_dashboard"))


@admin_bp.route("/developer/requests/<int:request_id>/approve", methods=["POST"])
@developer_required
def developer_approve_request(request_id):
    from app.models import AdminChangeRequest
    req = AdminChangeRequest.query.get_or_404(request_id)
    if req.status != "pending":
        flash("This request is already resolved.", "warning")
        return redirect(url_for("admin.developer_dashboard"))

    process_admin_change_request(req)
    flash("Request approved.", "success")
    return redirect(url_for("admin.developer_dashboard"))


@admin_bp.route("/developer/requests/<int:request_id>/reject", methods=["POST"])
@developer_required
def developer_reject_request(request_id):
    from app.models import AdminChangeRequest
    from datetime import datetime, timezone
    req = AdminChangeRequest.query.get_or_404(request_id)
    if req.status != "pending":
        flash("This request is already resolved.", "warning")
        return redirect(url_for("admin.developer_dashboard"))

    req.status = "rejected"
    req.resolved_at = datetime.now(timezone.utc)
    db.session.commit()
    flash("Request rejected.", "info")
    return redirect(url_for("admin.developer_dashboard"))
