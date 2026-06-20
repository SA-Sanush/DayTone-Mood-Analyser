import json
from functools import wraps
from pathlib import Path

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, logout_user

from app.extensions import db, cache
from app.models import BurnoutHistory, MoodLog, User, UserProfile, Suggestion
from app.utils.analytics import dashboard_data, platform_stats
from app.ml.predictor import build_features, predict_burnout
from app.nlp.sentiment import get_sentiment_score, get_sentiment_backend
from app.utils.suggestions import get_suggestions
from app.admin.forms import AdminUserProfileForm, AdminMoodLogForm

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


def update_log_analysis(user_id, log, form):
    sentiment = get_sentiment_score(form.notes.data)
    features = build_features(
        user_id,
        form.log_date.data,
        form.mood_score.data,
        form.sleep_hours.data,
        form.stress_level.data,
        form.activity_done.data,
        form.social_interaction.data,
        sentiment,
    )
    prediction = predict_burnout(features)
    log.log_date = form.log_date.data
    log.mood_score = form.mood_score.data
    log.sleep_hours = form.sleep_hours.data
    log.stress_level = form.stress_level.data
    log.activity_done = form.activity_done.data
    log.social_interaction = form.social_interaction.data
    log.notes = form.notes.data
    log.sentiment_score = sentiment
    log.burnout_risk = prediction["prediction"]

    # Update BurnoutHistory
    BurnoutHistory.query.filter_by(log_id=log.id).delete()
    history = BurnoutHistory(
        user_id=user_id,
        log_id=log.id,
        prediction=prediction["prediction"],
        confidence=prediction["confidence"],
        algorithm_used=prediction["algorithm"],
    )
    db.session.add(history)

    # Update suggestions
    Suggestion.query.filter_by(log_id=log.id).delete()
    user = User.query.get(user_id)
    preferred = user.profile.preferred_activity if user.profile else "Walk"
    for text in get_suggestions(
        log.burnout_risk,
        log.sleep_hours,
        log.stress_level,
        log.social_interaction,
        log.activity_done,
        preferred,
    ):
        db.session.add(Suggestion(user_id=user_id, log_id=log.id, suggestion_text=text))


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
    return render_template("admin/users.html", users=all_users, q=q, role_filter=role_filter)


@admin_bp.route("/user/<int:user_id>")
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    logs = MoodLog.query.filter_by(user_id=user.id).order_by(MoodLog.log_date.desc()).all()
    return render_template("admin/user_detail.html", user=user, logs=logs, data=dashboard_data(user.id))


@admin_bp.route("/user/<int:user_id>/toggle-role", methods=["POST"])
@admin_required
def toggle_role(user_id):
    user = User.query.get_or_404(user_id)
    is_self = (user.id == current_user.id)
    
    user.role = "user" if user.role == "admin" else "admin"
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
    is_self = (user.id == current_user.id)
    
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
        
        role_changed_self = (user.id == current_user.id and form.role.data == "user")
        user.role = form.role.data
        
        profile.age = form.age.data
        profile.gender = form.gender.data
        profile.occupation = form.occupation.data.strip() if form.occupation.data else None
        profile.preferred_activity = form.preferred_activity.data
        profile.daily_reminder = form.daily_reminder.data
        
        db.session.commit()
        cache.delete_memoized(dashboard_data, user.id)
        
        if role_changed_self:
            logout_user()
            flash("You have demoted yourself. You no longer have admin access.", "warning")
            return redirect(url_for("auth.login"))
            
        flash(f"Profile for {user.name} has been updated.", "success")
        return redirect(url_for("admin.user_detail", user_id=user.id))
        
    return render_template("admin/edit_profile.html", user=user, form=form)


@admin_bp.route("/user/<int:user_id>/log/<int:log_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_user_log(user_id, log_id):
    user = User.query.get_or_404(user_id)
    log = MoodLog.query.filter_by(id=log_id, user_id=user.id).first_or_404()
    form = AdminMoodLogForm(obj=log)
    
    if form.validate_on_submit():
        existing = MoodLog.query.filter_by(user_id=user.id, log_date=form.log_date.data).filter(MoodLog.id != log.id).first()
        if existing:
            flash(f"{user.name} already has a log for {form.log_date.data}.", "warning")
            return render_template("admin/edit_log.html", user=user, log=log, form=form)
            
        update_log_analysis(user.id, log, form)
        db.session.commit()
        cache.delete_memoized(dashboard_data, user.id)
        
        flash(f"Mood log for {user.name} updated.", "success")
        return redirect(url_for("admin.user_detail", user_id=user.id))
        
    return render_template("admin/edit_log.html", user=user, log=log, form=form)


@admin_bp.route("/user/<int:user_id>/log/<int:log_id>/delete", methods=["POST"])
@admin_required
def delete_user_log(user_id, log_id):
    user = User.query.get_or_404(user_id)
    log = MoodLog.query.filter_by(id=log_id, user_id=user.id).first_or_404()
    
    db.session.delete(log)
    db.session.commit()
    cache.delete_memoized(dashboard_data, user.id)
    
    flash("Mood log has been deleted.", "danger")
    return redirect(url_for("admin.user_detail", user_id=user.id))


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
