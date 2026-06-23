from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    FloatField,
    IntegerField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, NumberRange


class MoodLogForm(FlaskForm):
    log_date = DateField("Date", default=date.today, validators=[DataRequired()])
    mood_score = IntegerField(
        "Mood", validators=[DataRequired(), NumberRange(min=1, max=5)]
    )
    sleep_hours = FloatField(
        "Sleep Hours", validators=[DataRequired(), NumberRange(min=0, max=24)]
    )
    stress_level = IntegerField(
        "Stress", validators=[DataRequired(), NumberRange(min=1, max=5)]
    )
    activity_done = BooleanField("Physical activity done")
    social_interaction = IntegerField(
        "Social Interaction", validators=[DataRequired(), NumberRange(min=1, max=3)]
    )
    notes = TextAreaField("Notes", validators=[Length(max=1000)])
    submit = SubmitField("Save log")
