import sqlalchemy as sa
from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.models import User, Team, Match, Prediction
from app.forms import LoginForm, TeamForm, AddMatchForm, EditMatchForm
from app.utils import calculate_points, pred_by_id
from datetime import datetime
from pytz import timezone
from flask_login import login_required, current_user, login_user, logout_user


@app.route("/")
@app.route("/index")
@app.route("/matches")
@login_required
def matches():
    matches_not_done_DB = db.session.scalars(
        sa.select(Match)
        .where(Match.match_done.is_(False))
        .order_by(Match.match_date.asc())
    ).all()
    matches_done_DB = db.session.scalars(
        sa.select(Match)
        .where(Match.match_done.is_(True))
        .order_by(Match.match_date.desc())
    ).all()

    matches_done = [
        (
            match.id,
            match.match_date,
            match.home_team,
            match.away_team,
            match.home_score,
            match.away_score,
            pred_by_id(match_id=match.id, user_id=current_user.id),
        )
        for match in matches_done_DB
    ]
    matches_not_done = [
        (
            match.id,
            match.match_date,
            match.home_team,
            match.away_team,
            pred_by_id(match_id=match.id, user_id=current_user.id),
        )
        for match in matches_not_done_DB
    ]

    return render_template(
        "matches.html",
        title="Matches",
        matches_done=matches_done,
        matches_not_done=matches_not_done,
    )


@app.route("/stand")
@login_required
def stand():
    users = db.session.scalars(sa.select(User).order_by(User.score.desc())).all()
    scoreboard = [
        (postion, user.username, user.score, user.id)
        for postion, user in enumerate(users, start=1)
    ]
    return render_template("stand.html", title="Home", scoreboard=scoreboard)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("stand"))
    form = LoginForm()
    if form.validate_on_submit():
        # enkel hoofdletters voorkomt problemen later
        username_upper = form.username.data.upper()
        user = db.session.scalar(sa.select(User).where(User.username == username_upper))
        # user does not exixst create a new user (no authentication needeed)
        if user is None:
            user = User(username=username_upper)
            db.session.add(user)
            db.session.commit()
            flash(f"New user <{username_upper}> is created!")

        user = db.session.scalar(sa.select(User).where(User.username == username_upper))
        if user is None:
            flash("Error: try again")
            return redirect(url_for("login"))
        else:
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for("matches"))
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("matches"))


@app.route("/pronostiek/<int:match_id>", methods=["GET", "POST"])
@login_required
def edit_pronostiek(match_id):
    # Nodig voor een pronostiek: match, user(met bijhorende pronostiek), voorkomen dat match al gedaan is of bezig is
    match = db.session.get(Match, match_id)
    if match is None:
        flash("Error: match bestaat niet")
        return redirect(url_for("matches"))

    # Eigen voorspelling ophalen
    own_pred = db.session.scalar(
        sa.select(Prediction).where(
            Prediction.match_id == match_id, Prediction.user_id == current_user.id
        )
    )
    if (own_pred is None) and (not match.match_done):
        # Aanmaken van een nieuwe voorspelling
        own_pred = Prediction(
            user_id=current_user.id,
            match_id=match_id,
            predicted_home_score=0,
            predicted_away_score=0,
        )
        db.session.add(own_pred)
        db.session.commit()
        print("nieuwe prediction added")

    # Ophalen andere hun voorspelling --> Tonen in tabel
    others_predDB = db.session.scalars(
        sa.select(Prediction).where(
            Prediction.match_id == match_id, Prediction.user_id != current_user.id
        )
    ).all()
    others_pred = [
        (
            prediction.user.username,
            prediction.predicted_home_score,
            prediction.predicted_away_score,
            prediction.points_earned,
        )
        for prediction in others_predDB
    ]

    # * Disable aanpassen indien bezig is (of gedaan is)
    # ? Hoe tijdzones behandelen?
    local_tz = timezone('Europe/Brussels')
    match_date = local_tz.localize(match.match_date)
    match_bezig = True if (datetime.now(local_tz) >= match_date) else False
    print(match_bezig)
    pred_editbaar = not match_bezig and not match.match_done

    return render_template(
        "edit_pronostiek.html",
        title="Edit pronostiek",
        other_pred=others_pred,
        own_pred=own_pred,
        match=match,
        edit=pred_editbaar
    )


@app.route("/update_prono/<int:prono_id>", methods=["POST"])
@login_required
def update_pronostiek(prono_id):
    data = request.get_json()
    home_score = data.get("home_score")
    away_score = data.get("away_score")

    pred = db.session.get(Prediction, prono_id)
    if pred is None:
        flash("Error: Pronostiek niet gevonden")
        return {"success": False, "error": "Prediction not found"}, 404

    pred.predicted_home_score = home_score
    pred.predicted_away_score = away_score
    db.session.commit()
    flash(f"Pronostiek is geüpdatet naar {home_score} - {away_score}")
    return {"success": True}


# ! Admin pages hieronder
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    team_form = TeamForm()

    if not current_user.isAdmin:
        pass  # TODO throw error

    # get all users
    all_users = db.session.scalars(sa.select(User).order_by(User.username)).all()
    users = [(user.id, user.username, user.score) for user in all_users]

    if team_form.validate_on_submit():
        team = Team(name=team_form.teamname.data, logo_url=team_form.logo_url.data)
        db.session.add(team)
        db.session.commit()
        flash(f"New team {team_form.teamname.data} added!")
        return redirect(url_for("admin"))

    # print(request.form)
    if request.method == "POST" and "teamname" not in request.form:
        action = request.form.get("action")
        user_id = int(request.form.get("user_id"))

        user_to_modify = User.query.filter_by(id=user_id).first()

        if not user_to_modify:
            return "User not found", 404

        if action == "delete":
            if request.form.get("delete"):
                flash(f"User {user_to_modify.username} deleted")
                db.session.delete(user_to_modify)
                db.session.commit()
            else:
                flash("Checkbox for deleting user not checked, user not deleted")
            return redirect(url_for("admin"))
        elif action == "change_score":
            new_score = int(request.form.get("new_score"))
            user_to_modify.score = new_score
            db.session.commit()
            return redirect(url_for("admin"))

    return render_template(
        "admin.html", title="Admin panel", users=users, team_form=team_form
    )


@app.route("/admin/matches", methods=["GET", "POST"])
@login_required
def admin_matches():
    form = AddMatchForm()
    teams = db.session.scalars(sa.select(Team)).all()
    team_choices = [(team.id, team.name) for team in teams]

    form.home_team.choices = team_choices
    form.away_team.choices = team_choices

    if not current_user.isAdmin:
        return redirect(url_for("stand"))

    if form.validate_on_submit():
        print(
            f"Home: {form.home_team.data}, Away: {form.away_team.data}, date: {form.match_date.data}"
        )

        if form.home_team.data == form.away_team.data:
            flash("Error: home and away team have to be different")
            return redirect(url_for("admin_matches"))

        # Create the new match
        match = Match(
            home_team_id=form.home_team.data,
            away_team_id=form.away_team.data,
            match_date=form.match_date.data,
        )
        db.session.add(match)
        db.session.commit()

        #return redirect(url_for("admin_matches"))

    # Get all matches
    matchesDB = db.session.scalars(sa.select(Match).order_by(Match.match_date)).all()
    matches = [
        (
            match.id,
            match.home_team,
            match.away_team,
            match.match_date,
            match.home_score,
            match.away_score,
            match.match_done,
        )
        for match in matchesDB
    ]
    #print(matches)
    return render_template(
        "admin_matches.html", title="Admin Matches", form=form, matches=matches
    )


@app.route("/admin/edit_match/<int:match_id>", methods=["GET", "POST"])
@login_required
def edit_match(match_id):
    if not current_user.isAdmin:
        pass  # TODO throw error

    match = db.session.get(Match, match_id)
    form = EditMatchForm(
        homescore=match.home_score,
        awayscore=match.away_score,
        match_done=match.match_done,
    )
    # form.match_done.default = match.match_done  # Oude waarde al klaarzetten in de checkbox

    # TODO add functions to edit score and mark the match as done
    if form.validate_on_submit():
        # Handle delete
        if form.delete.data:
            if form.confirm_delete.data:
                flash(
                    f"Match {match.home_team.name} vs {match.away_team.name} deleted."
                )
                db.session.delete(match)
                db.session.commit()
                return redirect(url_for("admin_matches"))
            else:
                flash("Error: Confirm deletion checkbox not checked.")
                return redirect(url_for("edit_match", match_id=match_id))
        # Handle aanpassen score / match done
        if form.submit.data:
            done_before_submit = match.match_done

            match.home_score = form.homescore.data
            match.away_score = form.awayscore.data
            match.match_done = form.match_done.data
            db.session.commit()

            flash(f"Match {match.home_team.name} vs {match.away_team.name} updated.")

            if match.match_done:
                flash("Leaderboard has been updated after new result.")
                calculate_points(match_id)

            return redirect(url_for("admin_matches"))

    return render_template(
        "edit_matches.html", title="Edit Matches", form=form, match=match
    )
