"""Schémas Pydantic pour la ressource Cours.

- CoursCreate : payload attendu en création (POST)
- CoursUpdate : mise à jour partielle (PATCH), tout optionnel
- CoursOut    : forme sérialisée renvoyée par l'API
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CoursCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Si un champ non présent dans le schema est ajouté -- erreur 400
    intitule: str = Field(min_length=1, max_length=50)
    niveau: str = Field(min_length=1, max_length=50)
    capacite_max: int = Field(ge=1)
    professeur_id: int = Field(ge=1)
    annee_academique: str = Field(min_length=1, max_length=9, pattern=r"^\d{4}-\d{4}$")
    #ge=1 --> capacité et id toujours strictement positifs ; pattern --> format "YYYY-YYYY" imposé


class CoursUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intitule: str | None = Field(default=None, min_length=1, max_length=50)
    niveau: str | None = Field(default=None, min_length=1, max_length=50)
    capacite_max: int | None = Field(ge=1,default=None)
    professeur_id: int | None = Field(default=None, ge=1)
    annee_academique: str | None = Field(min_length=1, max_length=9, pattern=r"^\d{4}-\d{4}$", default=None)


class CoursOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    intitule: str
    niveau: str
    capacite_max: int
    professeur_id: int
    annee_academique: str
    created_at: datetime
    updated_at: datetime
