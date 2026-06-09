from functools import wraps

from flask import abort, render_template
from flask_login import current_user, login_required

from app.models import MoodLog, User
from app.utils.analytics import dashboard_data, platform_stats

from . import admin_bp


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
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)


@admin_bp.route("/user/<int:user_id>")
@admin_required
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    logs = MoodLog.query.filter_by(user_id=user.id).order_by(MoodLog.log_date.desc()).all()
    return render_template("admin/user_detail.html", user=user, logs=logs, data=dashboard_data(user.id))
