from datetime import date
from flask import current_app
from app.extensions import db, cache
from app.models import MoodLog, BurnoutHistory, Suggestion, Goal
from app.constants import BurnoutRisk
from app.nlp.sentiment import get_sentiment_score
from app.ml.predictor import build_features, predict_burnout
from app.utils.suggestions import get_suggestions
from app.utils.mailer import send_high_risk_alert

class MoodLogService:
    @staticmethod
    def create_log(user, form_data) -> MoodLog:
        # Calculate sentiment score
        sentiment = get_sentiment_score(form_data.notes.data)
        
        # Check predictions preference
        if user.profile and not user.profile.predict_burnout:
            prediction = {
                "prediction": "Low",
                "confidence": 0.0,
                "algorithm": "Opted Out",
                "drivers": [],
            }
        else:
            features = build_features(
                user.id,
                form_data.log_date.data,
                form_data.mood_score.data,
                form_data.sleep_hours.data,
                form_data.stress_level.data,
                form_data.activity_done.data,
                form_data.social_interaction.data,
                sentiment,
            )
            prediction = predict_burnout(features)
            
        log = MoodLog(
            user_id=user.id,
            log_date=form_data.log_date.data,
            mood_score=form_data.mood_score.data,
            sleep_hours=form_data.sleep_hours.data,
            stress_level=form_data.stress_level.data,
            activity_done=form_data.activity_done.data,
            social_interaction=form_data.social_interaction.data,
            sentiment_score=sentiment,
            burnout_risk=prediction["prediction"],
        )
        log.notes = form_data.notes.data
        
        db.session.add(log)
        db.session.flush()
        
        # Save BurnoutHistory
        history = BurnoutHistory(
            user_id=user.id,
            log_id=log.id,
            prediction=prediction["prediction"],
            confidence=prediction["confidence"],
            algorithm_used=prediction["algorithm"],
        )
        db.session.add(history)
        
        # Suggestions
        MoodLogService._replace_suggestions(user, log)
        
        db.session.commit()
        
        # Invalidate dashboard and goals caching
        from app.utils.analytics import dashboard_data
        cache.delete_memoized(dashboard_data, user.id)
        cache.delete(f"goals_with_progress_{user.id}")
        cache.delete(f"heatmap_data_{user.id}_current")
        cache.delete(f"heatmap_data_{user.id}_{log.log_date.year}")
        
        # Send alert if High Risk
        if log.burnout_risk == BurnoutRisk.HIGH:
            current_app.logger.info("High-risk alert queued user_id=%s log_id=%s", user.id, log.id)
            send_high_risk_alert(user, log)
            
        return log

    @staticmethod
    def update_log(user, log, form_data) -> MoodLog:
        sentiment = get_sentiment_score(form_data.notes.data)
        
        if user.profile and not user.profile.predict_burnout:
            prediction = {
                "prediction": "Low",
                "confidence": 0.0,
                "algorithm": "Opted Out",
                "drivers": [],
            }
        else:
            features = build_features(
                user.id,
                form_data.log_date.data,
                form_data.mood_score.data,
                form_data.sleep_hours.data,
                form_data.stress_level.data,
                form_data.activity_done.data,
                form_data.social_interaction.data,
                sentiment,
            )
            prediction = predict_burnout(features)
            
        log.log_date = form_data.log_date.data
        log.mood_score = form_data.mood_score.data
        log.sleep_hours = form_data.sleep_hours.data
        log.stress_level = form_data.stress_level.data
        log.activity_done = form_data.activity_done.data
        log.social_interaction = form_data.social_interaction.data
        log.notes = form_data.notes.data
        log.sentiment_score = sentiment
        log.burnout_risk = prediction["prediction"]
        
        # Remove old history and add new
        BurnoutHistory.query.filter_by(log_id=log.id).delete()
        db.session.add(
            BurnoutHistory(
                user_id=user.id,
                log_id=log.id,
                prediction=prediction["prediction"],
                confidence=prediction["confidence"],
                algorithm_used=prediction["algorithm"],
            )
        )
        
        # Update suggestions
        MoodLogService._replace_suggestions(user, log)
        
        db.session.commit()
        
        # Invalidate cache
        from app.utils.analytics import dashboard_data
        cache.delete_memoized(dashboard_data, user.id)
        cache.delete(f"goals_with_progress_{user.id}")
        cache.delete(f"heatmap_data_{user.id}_current")
        cache.delete(f"heatmap_data_{user.id}_{log.log_date.year}")
        
        if log.burnout_risk == BurnoutRisk.HIGH:
            current_app.logger.info("High-risk alert queued user_id=%s log_id=%s", user.id, log.id)
            send_high_risk_alert(user, log)
            
        return log

    @staticmethod
    def _replace_suggestions(user, log) -> None:
        Suggestion.query.filter_by(log_id=log.id).delete()
        preferred = user.profile.preferred_activity if user.profile else "Walk"
        for text in get_suggestions(
            log.burnout_risk,
            log.sleep_hours,
            log.stress_level,
            log.social_interaction,
            log.activity_done,
            preferred,
        ):
            db.session.add(
                Suggestion(user_id=user.id, log_id=log.id, suggestion_text=text)
            )

class GoalService:
    @staticmethod
    def create_goal(user, target_type: str, target_value: float) -> Goal:
        goal = Goal(
            user_id=user.id,
            target_type=target_type,
            target_value=target_value,
        )
        db.session.add(goal)
        db.session.commit()
        
        # Invalidate caching
        from app.utils.analytics import dashboard_data
        cache.delete_memoized(dashboard_data, user.id)
        cache.delete(f"goals_with_progress_{user.id}")
        return goal

    @staticmethod
    def complete_goal(user, goal_id: int) -> Goal | None:
        goal = Goal.query.filter_by(id=goal_id, user_id=user.id).first()
        if goal:
            goal.completed = True
            db.session.commit()
            cache.delete(f"goals_with_progress_{user.id}")
        return goal

    @staticmethod
    def delete_goal(user, goal_id: int) -> Goal | None:
        goal = Goal.query.filter_by(id=goal_id, user_id=user.id).first()
        if goal:
            db.session.delete(goal)
            db.session.commit()
            cache.delete(f"goals_with_progress_{user.id}")
        return goal
