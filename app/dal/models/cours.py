"""Modèle Cours — un cours de l'Académie (appartenant à un professeur N-1)."""

from app.dal.database import db
from app.dal.models.timestamps import TimestampMixin
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Cours(TimestampMixin, db.Model):
    __tablename__ = "cours"

    id: Mapped[int] = mapped_column(primary_key=True)
    intitule: Mapped[str] = mapped_column(String(50))
    niveau: Mapped[str] = mapped_column(String(50))
    capacite_max: Mapped[int]
    professeur_id: Mapped[int] = mapped_column(ForeignKey("professeurs.id"))
    annee_academique: Mapped[str] = mapped_column(String(9), index=True)
    # string(9) pour avoir "YYYY-YYYY"

    professeur: Mapped["Professeur"] = relationship(back_populates="cours")

    def __repr__(self): #permet une représenation plus propre pour le dev
        return f"<ID: {self.id} - Cours : {self.intitule}>"
