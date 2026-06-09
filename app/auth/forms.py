from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional


class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    age = IntegerField("Age", validators=[Optional(), NumberRange(min=10, max=100)])
    gender = SelectField(
        "Gender",
        choices=[("", "Prefer not to say"), ("female", "Female"), ("male", "Male"), ("other", "Other")],
        validators=[Optional()],
    )
    occupation = StringField("Occupation", validators=[Optional(), Length(max=100)])
    preferred_activity = SelectField(
        "Preferred Activity",
        choices=[("Walk", "Walk"), ("Yoga", "Yoga"), ("Music", "Music"), ("Reading", "Reading")],
    )
    admin_code = StringField("Admin Invite Code", validators=[Optional(), Length(max=100)])
    submit = SubmitField("Create account")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")
