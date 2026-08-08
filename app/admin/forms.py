from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    FloatField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional


class AdminUserProfileForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    role = SelectField(
        "Role",
        choices=[("user", "User"), ("admin", "Admin"), ("developer", "Developer")],
        validators=[DataRequired()],
    )
    age = IntegerField("Age", validators=[Optional(), NumberRange(min=10, max=100)])
    gender = SelectField(
        "Gender",
        choices=[
            ("", "Prefer not to say"),
            ("female", "Female"),
            ("male", "Male"),
            ("other", "Other"),
        ],
        validators=[Optional()],
    )
    occupation = StringField("Occupation", validators=[Optional(), Length(max=100)])
    preferred_activity = SelectField(
        "Preferred Activity",
        choices=[
            ("Walk", "Walk"),
            ("Run", "Run"),
            ("Cycle", "Cycle"),
            ("Yoga", "Yoga"),
            ("Gym", "Gym"),
            ("Swim", "Swim"),
            ("Music", "Music"),
            ("Reading", "Reading"),
        ],
    )
    daily_reminder = BooleanField("Send daily check-in email reminder")
    submit = SubmitField("Save Changes")


class AdminMoodLogForm(FlaskForm):
    log_date = DateField("Log Date", validators=[DataRequired()])
    mood_score = SelectField(
        "Mood",
        coerce=int,
        choices=[
            (5, "😊 Happy"),
            (4, "😌 Calm"),
            (3, "😰 Anxious"),
            (2, "😢 Sad"),
            (1, "🤒 Sick"),
        ],
        validators=[DataRequired()],
    )
    sleep_hours = FloatField(
        "Sleep Hours", validators=[DataRequired(), NumberRange(min=0, max=24)]
    )
    stress_level = SelectField(
        "Stress Level",
        coerce=int,
        choices=[
            (1, "1 - Very Low"),
            (2, "2 - Low"),
            (3, "3 - Moderate"),
            (4, "4 - High"),
            (5, "5 - Extreme"),
        ],
        validators=[DataRequired()],
    )
    social_interaction = SelectField(
        "Social Interaction",
        coerce=int,
        choices=[(1, "👤 Alone"), (2, "👥 Group"), (3, "🗣️ Social")],
        validators=[DataRequired()],
    )
    activity_done = BooleanField("Activity Completed")
    submit = SubmitField("Save Changes")
