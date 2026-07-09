"""Modèle Professeur — un enseignant de l'Académie (responsable de plusieurs cours, 1-N)."""

from app.dal.database import db
from app.dal.models.timestamps import TimestampMixin
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Professeur(TimestampMixin, db.Model):
    __tablename__ = "professeurs"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(50))
    prenom: Mapped[str] = mapped_column(String(50))
    matiere: Mapped[str] = mapped_column(String(50))
    anciennete: Mapped[int] = mapped_column(default=0)

    def __repr__(self): #permet une représenation plus propre pour le dev
        return f"<ID: {self.id} - Professeur : {self.nom}>"