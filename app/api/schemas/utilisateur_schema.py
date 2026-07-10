"""Schémas Pydantic pour la ressource Utilisateur.

- UtilisateurCreate : payload attendu en création (POST)
- UtilisateurUpdate : mise à jour partielle (PATCH), email et mot de passe seulement
- UtilisateurOut    : forme sérialisée renvoyée par l'API — sans le mot de passe
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Literal

class UtilisateurCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Si un champ non présent dans le schema est ajouté -- erreur 400
    email: str = Field(min_length=1, max_length=120)
    mot_de_passe: str = Field(min_length=1, max_length=255)
    role: Literal["eleve", "professeur", "admin"]
    eleve_id: int | None = Field(default=None, ge=1)
    professeur_id: int | None = Field(default=None, ge=1)
    # FK nullables : l'admin n'est lié ni à un élève ni à un professeur

    @model_validator(mode="after")
    def verifier_coherence_role_lien(self):
        # mode="after" : les champs sont déjà typés et validés, on peut les comparer.
        # Un role hors du Literal n'arrive jamais ici -> aucune branche else à prévoir.
        if self.role == "eleve" and (self.eleve_id is None or self.professeur_id is not None):
            raise ValueError("role 'eleve' : eleve_id obligatoire, professeur_id interdit")
        if self.role == "professeur" and (self.professeur_id is None or self.eleve_id is not None):
            raise ValueError("role 'professeur' : professeur_id obligatoire, eleve_id interdit")
        if self.role == "admin" and (self.eleve_id is not None or self.professeur_id is not None):
            raise ValueError("role 'admin' : ni eleve_id ni professeur_id ne doivent être renseignés")
        return self  # obligatoire : la valeur retournée devient l'objet validé

class UtilisateurUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Seuls email et mot_de_passe sont modifiables : role et FK ne changent pas par un PATCH.
    # extra="forbid" -> tenter de patcher role donne un 400 explicite, pas un silence.
    # Pas de model_validator ici : sur un payload partiel il ne verrait pas l'état en base.
    email: str | None = Field(default=None, min_length=1, max_length=120)
    mot_de_passe: str | None = Field(default=None, min_length=1, max_length=255)

class UtilisateurOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    # mot_de_passe est volontairement absent : il ne sort JAMAIS de l'API.
    role: Literal["eleve", "professeur", "admin"]
    eleve_id: int | None
    professeur_id: int | None
    created_at: datetime
    updated_at: datetime
