"""Modèle Maison — une maison de l'Académie (possède plusieurs élèves, 1-N)."""

from app.dal.database import db
from app.dal.models.timestamps import TimestampMixin
from sqlalchemy import Column, Integer, String

class Maison(TimestampMixin, db.Model):
    __tablename__ = "maisons"
    id = Column(Integer, primary_key=True)
    nom = Column(String(50), unique=True, nullable=False)
    couleur = Column(String(50))
    fondateur = Column(String(50))
    valeurs = Column(String(255))
    reputation = Column(Integer, default=0, nullable=False)


    def __repr__(self): #permet une représenation plus propre pour le dev
        return f"<Maison {self.id} {self.nom}>"

