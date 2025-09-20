from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True, index=True)
    score: so.Mapped[int] = so.mapped_column(default=0)
    isAdmin: so.Mapped[bool] = so.mapped_column(default=False)
    # ! geen actuele field maar verwijzing naar de relatie in de prediction map
    predictions: so.WriteOnlyMapped["Prediction"] = so.relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self):
        return f"<User {self.username}> with score: {self.score}"


class Team(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True, index=True)
    logo_url: so.Mapped[str] = so.mapped_column(
        sa.String(256), nullable=True
    )  # stored in static folder

    def __repr__(self):
        return f"<Team {self.name}>"


# * Acttual match data model
class Match(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    home_score: so.Mapped[int] = so.mapped_column(default=0)
    away_score: so.Mapped[int] = so.mapped_column(default=0)
    # home_team: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    # away_team: so.Mapped[str] = so.mapped_column(sa.String(64), index=True)
    home_team_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(Team.id, name="fk_match_home_team_id", ondelete="CASCADE"),
        index=True,
    )
    away_team_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(Team.id, name="fk_match_away_team_id", ondelete="CASCADE"),
        index=True,
    )

    home_team: so.Mapped["Team"] = so.relationship(foreign_keys=[home_team_id])
    away_team: so.Mapped["Team"] = so.relationship(foreign_keys=[away_team_id])

    match_done: so.Mapped[bool] = so.mapped_column(default=False)
    # TODO controleer of dit ook uur meegeeft
    match_date: so.Mapped[datetime] = so.mapped_column(index=True)

    match_predictions: so.WriteOnlyMapped["Prediction"] = so.relationship(
        back_populates="predicted_match", passive_deletes=True
    )

    def __repr__(self):
        return f"<Match {self.home_team} vs {self.away_team} on {self.match_date}>"


class Prediction(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(User.id, name="fk_prediction_user_id", ondelete="CASCADE"),
        index=True,
    )
    match_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(Match.id, name="fk_prediction_match_id", ondelete="CASCADE"),
        index=True,
    )
    predicted_home_score: so.Mapped[int] = so.mapped_column(nullable=True)
    predicted_away_score: so.Mapped[int] = so.mapped_column(nullable=True)
    points_earned: so.Mapped[int] = so.mapped_column(default=0)

    # Geen actual relatie maar verwijzing naar user
    # ? Is er ook een verwijzing nodig naar de match?
    user: so.Mapped[User] = so.relationship(back_populates="predictions")
    predicted_match: so.Mapped[Match] = so.relationship(
        back_populates="match_predictions"
    )

    def __repr__(self):
        return f"<Prediction {self.user} predicts {self.predicted_home_score}-{self.predicted_away_score} for match {self.predicted_match}>"
