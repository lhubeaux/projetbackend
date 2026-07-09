"""Modèle Elève — un élève de l'Académie."""

from app.dal.database import db
from app.dal.models.timestamps import TimestampMixin
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Eleve(TimestampMixin, db.Model):
    __tablename__ = "eleves"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(50))
    prenom: Mapped[str] = mapped_column(String(50))
    annee: Mapped[int]
    familier: Mapped[str] = mapped_column(String(50))
    #statuts possibles: "inscrit", "diplome", "renvoye"
    statut: Mapped[str] = mapped_column(String(20), default="inscrit")
    maison_id: Mapped[int] = mapped_column(ForeignKey("maisons.id"))

    maison: Mapped["Maison"] = relationship(back_populates="eleves")

    def __repr__(self): #permet une représenation plus propre pour le dev
        return f"<ID: {self.id} - Eleve : {self.nom}>"
