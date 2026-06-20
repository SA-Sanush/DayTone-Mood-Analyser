import csv
from datetime import date
from io import StringIO

from flask import Response, current_app, flash, jsonify, redirect, render_template, request, send_file, url_for, stream_with_context
from flask_login import current_user, login_required

from app.constants import BurnoutRisk
from app.extensions import db, limiter, cache
from app.ml.predictor import build_features, predict_burnout
from app.models import BurnoutHistory, Goal, MoodLog, Suggestion
from app.nlp.sentiment import get_sentiment_score
from app.utils.analytics import dashboard_data, heatmap_data, goal_progress
from app.utils.mailer import send_high_risk_alert
from app.utils.pdf_report import build_pdf_report
from app.utils.suggestions import get_suggestions

from . import mood_bp
from .forms import MoodLogForm


def _mutate_log_with_analysis(log, form):
    sentiment = get_sentiment_score(form.notes.data)
    features = build_features(
        current_user.id,
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
    return prediction


def _replace_suggestions(log):
    Suggestion.query.filter_by(log_id=log.id).delete()
    preferred = current_user.profile.preferred_activity if current_user.profile else "Walk"
    for text in get_suggestions(
        log.burnout_risk,
        log.sleep_hours,
        log.stress_level,
        log.social_interaction,
        log.activity_done,
        preferred,
    ):
        db.session.add(Suggestion(user_id=current_user.id, log_id=log.id, suggestion_text=text))


@mood_bp.route("/log", methods=["GET", "POST"])
@login_required
def log_mood():
    form = MoodLogForm()
    if request.method == "GET" and request.args.get("date"):
        try:
            form.log_date.data = date.fromisoformat(request.args.get("date"))
        except Exception:
            pass
    if form.validate_on_submit():
        existing = MoodLog.query.filter_by(user_id=current_user.id, log_date=form.log_date.data).first()
        if existing:
            flash("You already have a log for that date. Visit History to edit it.", "warning")
            return render_template("mood/log.html", form=form)

        log = MoodLog(
            user_id=current_user.id,
            log_date=form.log_date.data,
            mood_score=form.mood_score.data,
            sleep_hours=form.sleep_hours.data,
            stress_level=form.stress_level.data,
            activity_done=form.activity_done.data,
            social_interaction=form.social_interaction.data,
        )
        prediction = _mutate_log_with_analysis(log, form)
        db.session.add(log)
        db.session.flush()

        history = BurnoutHistory(
            user_id=current_user.id,
            log_id=log.id,
            prediction=prediction["prediction"],
            confidence=prediction["confidence"],
            algorithm_used=prediction["algorithm"],
        )
        db.session.add(history)

        _replace_suggestions(log)

        db.session.commit()
        # Invalidate dashboard cache for the user
        cache.delete_memoized(dashboard_data, current_user.id)

        if log.burnout_risk == BurnoutRisk.HIGH:
            current_app.logger.info("High-risk alert queued user_id=%s log_id=%s", current_user.id, log.id)
            send_high_risk_alert(current_user, log)
        flash("Mood log saved with DayTone burnout analysis.", "success")
        return redirect(url_for("mood.dashboard"))

    return render_template("mood/log.html", form=form)


@mood_bp.route("/log/<int:log_id>/edit", methods=["GET", "POST"])
@login_required
def edit_log(log_id):
    log = MoodLog.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()
    form = MoodLogForm(obj=log)
    # Pre-populate the notes field from the decrypted property
    if request.method == "GET":
        form.notes.data = log.notes
    if form.validate_on_submit():
        existing = (
            MoodLog.query.filter_by(user_id=current_user.id, log_date=form.log_date.data)
            .filter(MoodLog.id != log.id)
            .first()
        )
        if existing:
            flash("You already have another log for that date.", "warning")
            return render_template("mood/log.html", form=form, editing=True, log=log)

        prediction = _mutate_log_with_analysis(log, form)
        BurnoutHistory.query.filter_by(log_id=log.id).delete()
        db.session.add(
            BurnoutHistory(
                user_id=current_user.id,
                log_id=log.id,
                prediction=prediction["prediction"],
                confidence=prediction["confidence"],
                algorithm_used=prediction["algorithm"],
            )
        )
        _replace_suggestions(log)
        db.session.commit()
        # Invalidate dashboard cache for the user
        cache.delete_memoized(dashboard_data, current_user.id)

        if log.burnout_risk == BurnoutRisk.HIGH:
            current_app.logger.info("High-risk alert queued user_id=%s log_id=%s", current_user.id, log.id)
            send_high_risk_alert(current_user, log)
        flash("Mood log updated with fresh DayTone analysis.", "success")
        return redirect(url_for("mood.history"))

    return render_template("mood/log.html", form=form, editing=True, log=log)


@mood_bp.route("/dashboard")
@login_required
def dashboard():
    data = dashboard_data(current_user.id)
    calm_mode = current_user.profile.calm_mode if current_user.profile else False
    chart_data = {
        "labels": data["labels"],
        "mood": data["mood"],
        "sleep": data["sleep"],
        "stress": data["stress"],
        "burnout_distribution": data["burnout_distribution"],
        "scatter": data["scatter"],
    }
    dashboard_state = {
        "orb": data["latest_orb_state"],
        "streak_count": data["streak_count"],
        "challenge_progress": data["challenge_progress"],
        "badges": data["badges"],
        "trend_summary": data["trend_summary"],
        "insight_bars": data["insight_bars"],
        "calm_mode": calm_mode,
        "drivers": data.get("drivers", []),
        "correlation_insight": data.get("correlation_insight"),
    }
    user_goals = Goal.query.filter_by(user_id=current_user.id, completed=False).all()
    goals_with_progress = [(g, goal_progress(g, current_user.id)) for g in user_goals]
    return render_template(
        "mood/dashboard.html",
        data=data,
        chart_data=chart_data,
        dashboard_state=dashboard_state,
        goals_with_progress=goals_with_progress,
    )


@mood_bp.route("/history")
@login_required
def history():
    from sqlalchemy.orm import joinedload
    page = request.args.get('page', 1, type=int)
    pagination = MoodLog.query.filter_by(user_id=current_user.id) \
        .options(joinedload(MoodLog.suggestions), joinedload(MoodLog.burnout_history)) \
        .order_by(MoodLog.log_date.desc()) \
        .paginate(page=page, per_page=30, error_out=False)
    return render_template("mood/history.html", logs=pagination.items, pagination=pagination)


@mood_bp.route("/heatmap")
@login_required
def heatmap():
    return render_template("mood/heatmap.html")


@mood_bp.route("/api/heatmap")
@login_required
def heatmap_api():
    year = request.args.get("year", type=int)
    return jsonify(heatmap_data(current_user.id, year=year))


@mood_bp.route("/api/feedback/<int:history_id>", methods=["POST"])
@login_required
@limiter.limit("30 per minute")
def prediction_feedback(history_id):
    """Record whether the user found the burnout prediction accurate.

    Accepts JSON body: {"accurate": true|false}
    Returns JSON: {"success": true, "history_id": <int>}
    """
    history = BurnoutHistory.query.filter_by(id=history_id, user_id=current_user.id).first_or_404()
    data = request.get_json(silent=True) or {}
    accurate_value = data.get("accurate")
    if accurate_value is None:
        return jsonify({"error": "Missing 'accurate' field (true/false)"}), 400
    history.is_accurate = bool(accurate_value)
    db.session.commit()
    return jsonify({"success": True, "history_id": history_id})


@mood_bp.route("/goals", methods=["GET", "POST"])
@login_required
def goals():
    """Goal management page: create and view personal wellness goals."""
    if request.method == "POST":
        action = request.form.get("action", "create")
        if action == "create":
            target_type = request.form.get("target_type", "")
            target_value_raw = request.form.get("target_value", "")
            valid_types = {"sleep", "mood", "active_days", "journal_days", "stress"}
            if target_type not in valid_types:
                flash("Invalid goal type.", "danger")
            else:
                try:
                    target_value = float(target_value_raw)
                    goal = Goal(
                        user_id=current_user.id,
                        target_type=target_type,
                        target_value=target_value,
                    )
                    db.session.add(goal)
                    db.session.commit()
                    cache.delete_memoized(dashboard_data, current_user.id)
                    flash(f"Goal '{goal.display_name}' created!", "success")
                except (ValueError, TypeError):
                    flash("Invalid target value.", "danger")

        elif action == "complete":
            goal_id = request.form.get("goal_id", type=int)
            if goal_id:
                goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
                if goal:
                    goal.completed = True
                    db.session.commit()
                    flash("Goal marked as completed!", "success")

        elif action == "delete":
            goal_id = request.form.get("goal_id", type=int)
            if goal_id:
                goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
                if goal:
                    db.session.delete(goal)
                    db.session.commit()
                    flash("Goal removed.", "info")

        return redirect(url_for("mood.goals"))

    active_goals = Goal.query.filter_by(user_id=current_user.id, completed=False).all()
    completed_goals = Goal.query.filter_by(user_id=current_user.id, completed=True).all()
    goals_with_progress = [(g, goal_progress(g, current_user.id)) for g in active_goals]
    return render_template(
        "mood/goals.html",
        goals_with_progress=goals_with_progress,
        completed_goals=completed_goals,
    )


@mood_bp.route("/report/pdf")
@login_required
@limiter.limit("5 per minute")
def report_pdf():
    pdf = build_pdf_report(current_user)
    response = send_file(pdf, mimetype="application/pdf", as_attachment=True, download_name="daytone-report.pdf")
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@mood_bp.route("/export/csv")
@login_required
@limiter.limit("5 per minute")
def export_csv():
    include_notes = request.args.get("include_notes") == "1"
    headers = [
        "date",
        "mood_score",
        "sleep_hours",
        "stress_level",
        "activity_done",
        "social_interaction",
        "sentiment_score",
        "burnout_risk",
    ]
    if include_notes:
        headers.append("notes")

    def generate():
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        yield output.getvalue()

        logs = MoodLog.query.filter_by(user_id=current_user.id).order_by(MoodLog.log_date.asc()).all()
        for log in logs:
            output = StringIO()
            writer = csv.writer(output)
            row = [
                log.log_date,
                log.mood_score,
                log.sleep_hours,
                log.stress_level,
                log.activity_done,
                log.social_interaction,
                log.sentiment_score,
                log.burnout_risk,
            ]
            if include_notes:
                row.append(log.notes or "")
            writer.writerow(row)
            yield output.getvalue()

    return Response(
        stream_with_context(generate()),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=daytone-logs.csv",
            "X-Content-Type-Options": "nosniff"
        },
    )
