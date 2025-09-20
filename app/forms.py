from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    BooleanField,
    SelectField,
    DateTimeField,
    IntegerField,
)
from wtforms.validators import DataRequired, ValidationError
from app import db
from app.models import Team
import sqlalchemy as sa


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class TeamForm(FlaskForm):
    teamname = StringField("Team name", validators=[DataRequired()])
    logo_url = StringField("Logo URL", default="placeholder.png")
    submit = SubmitField("Add new team")

    def validate_teamname(self, teamname):
        team = db.session.scalar(sa.select(Team).where(Team.name == teamname.data))
        if team is not None:
            raise ValidationError("Please use a different teamname.")


class AddMatchForm(FlaskForm):
    # Choices is dynamisch --> best vanuit de view opvullen form.home_team.choices
    home_team = SelectField("Thuis team", coerce=int, validators=[DataRequired()])
    away_team = SelectField("Uit team", coerce=int, validators=[DataRequired()])
    match_date = DateTimeField(
        "Match Date & Time (dd/mm/yyyy H:M)",
        format="%d/%m/%Y %H:%M",
        validators=[DataRequired()],
    )
    submit = SubmitField("Add new match")


class EditMatchForm(FlaskForm):
    homescore = IntegerField("Home team score", validators=[])
    awayscore = IntegerField("Away team score", validators=[])
    match_done = BooleanField("Match played")
    confirm_delete = BooleanField("Confirm deletion")
    submit = SubmitField("Update match")
    delete = SubmitField("Delete match")

    def validate_homescore(self, homescore):
        if homescore.data < 0 and homescore.data is not None:
            raise ValidationError("Score cannot be negative.")

    def validate_awayscore(self, awayscore):
        if awayscore.data < 0 and awayscore.data is not None:
            raise ValidationError("Score cannot be negative.")
