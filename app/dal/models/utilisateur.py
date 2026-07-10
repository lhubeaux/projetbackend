from app.dal.database import db
from app.dal.models.timestamps import TimestampMixin
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Utilisateur(TimestampMixin, db.Model):
    __tablename__ = "utilisateurs"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True)
    # TEMPORAIRE — mot de passe stocké en clair (cf. cahier des charges, jour 1).
    # À remplacer par un hash (bcrypt/argon2) si le projet dépasse le cadre pédagogique.
    mot_de_passe: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20)) #eleve, professeur ou admin
    eleve_id: Mapped[int | None] = mapped_column(ForeignKey("eleves.id"), unique=True)
    professeur_id: Mapped[int | None] = mapped_column(ForeignKey("professeurs.id"), unique=True)

    eleve: Mapped["Eleve | None"] = relationship(back_populates="utilisateur")
    professeur: Mapped["Professeur | None"] = relationship(back_populates="utilisateur")


    

    def __repr__(self): #permet une représenation plus propre pour le dev
        return f"<ID: {self.id} - Utilisateur : {self.email}>"
