"""Modèle Maison — une maison de l'Académie (possède plusieurs élèves, 1-N)."""

from app.dal.database import db
from app.dal.models.timestamps import TimestampMixin
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Maison(TimestampMixin, db.Model):
    __tablename__ = "maisons"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(50), unique=True)
    couleur: Mapped[str] = mapped_column(String(50))
    reputation: Mapped[int] = mapped_column(default=0)
    fondateur: Mapped[str] = mapped_column(String(50))
    valeurs: Mapped[str] = mapped_column(Text)

    eleves: Mapped[list["Eleve"]] = relationship(back_populates="maison")



    def __repr__(self): #permet une représenation plus propre pour le dev
        return f"<Maison {self.id} {self.nom}>"

