import sqlalchemy as sa
from app import db
from app.models import Prediction

def calculate_points(match_id: int):
    print("Hier moeten de punten nog berekend worden")

    # Stap 1: Ophalen alle predictions horende bij de match
    #match = db.session.get(Match, match_id)
    predictions = db.session.scalars(
        sa.select(Prediction).where(Prediction.match_id == match_id)
    ).all()
    
    # buitenFor aangezien dit zelfde is voro elke prediction
    match_home = predictions[0].predicted_match.home_score
    match_away = predictions[0].predicted_match.away_score
    match_GD = match_home - match_away
    for prediction in predictions:
        pred_GD = prediction.predicted_home_score - prediction.predicted_away_score
        prev_points_earned = prediction.points_earned # Correctie doorvoeren indien match al eens als done gezet is
        if (match_GD == pred_GD):
            # Kijken of volledig juist of enkel GD juist
            if ((match_home == prediction.predicted_home_score) and (match_away == prediction.predicted_away_score)):
                prediction.points_earned = 10
            else:
                prediction.points_earned = 6
        # correcte winnaar maar foute GD
        elif (((match_GD > 0) and (pred_GD > 0)) or ((match_GD < 0) and (pred_GD < 0))):
            prediction.points_earned = 3
        else:
            prediction.points_earned = 1
        print(prediction.points_earned - prev_points_earned)
        prediction.user.score = prediction.user.score + prediction.points_earned - prev_points_earned
    # Update the DB
    db.session.commit()


def pred_by_id(match_id: int, user_id: int):
    pred = db.session.scalar(
        sa.select(Prediction).where(
            Prediction.match_id == match_id, Prediction.user_id == user_id
        )
    )
    return pred