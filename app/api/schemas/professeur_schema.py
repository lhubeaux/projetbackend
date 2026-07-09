"""Schémas Pydantic pour la ressource Professeur.

- ProfesseurCreate : payload attendu en création (POST)
- ProfesseurUpdate : mise à jour partielle (PATCH), tout optionnel
- ProfesseurOut    : forme sérialisée renvoyée par l'API
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ProfesseurCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Si un champ non présent dans le schema est ajouté -- erreur 400
    nom: str = Field(min_length=1, max_length=50)
    prenom: str = Field(min_length=1, max_length=50)
    matiere: str = Field(min_length=1, max_length=50)
    anciennete: int = Field(ge=0, default=0)
    #ge=0 veut dire greather or equal --> pas d'ancienneté négative


class ProfesseurUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nom: str | None = Field(default=None, min_length=1, max_length=50)
    prenom: str | None = Field(default=None, min_length=1, max_length=50)
    matiere: str | None = Field(default=None, min_length=1, max_length=50)
    anciennete: int | None = Field(default=None, ge=0)


class ProfesseurOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    prenom: str
    matiere: str
    anciennete: int
    created_at: datetime
    updated_at: datetime
