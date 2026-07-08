"""Schémas Pydantic pour la ressource Maison.

Séparation nette avec le modèle SQLAlchemy (persistance) :
- MaisonCreate : payload attendu en création (POST)
- MaisonUpdate : payload de mise à jour partielle (PATCH), tout optionnel
- MaisonOut    : forme sérialisée renvoyée par l'API
"""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class MaisonCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Si un champ non présent dans le schema est ajouté -- erreur 400
    nom: str = Field(min_length=1, max_length=50)
    couleur: str = Field(min_length=1, max_length=50)
    fondateur: str = Field(min_length=1, max_length=50)
    valeurs: str = Field(min_length=1)


class MaisonUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nom: str | None = Field(default=None, min_length=1, max_length=50)
    couleur: str | None = Field(default=None, min_length=1, max_length=50)
    fondateur: str | None = Field(default=None, min_length=1, max_length=50)
    valeurs: str | None = Field(default=None, min_length=1)


class MaisonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    couleur: str
    reputation: int
    fondateur: str
    valeurs: str
    created_at: datetime
    updated_at: datetime
