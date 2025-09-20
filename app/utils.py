import sqlalchemy as sa
from app import db
from app.models import Prediction

def calculate_points(match_id: int):
    # TODO Implementatie van het berekenen van de punten
    # * Update points earned in de predictions tabel
    # * Update totaal aantal punten in de users tabel
    print("Hier moeten de punten nog berekend worden")

    # Stap 1: Ophalen alle predictions horende bij de match

    pass


def pred_by_id(match_id: int, user_id: int):
    pred = db.session.scalar(
        sa.select(Prediction).where(
            Prediction.match_id == match_id, Prediction.user_id == user_id
        )
    )
    return pred