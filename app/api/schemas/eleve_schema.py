"""Schémas Pydantic pour la ressource Élève.

- EleveCreate : payload attendu en création (POST)
- EleveUpdate : mise à jour partielle (PATCH), tout optionnel
- EleveOut    : forme sérialisée renvoyée par l'API
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class EleveCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Si un champ non présent dans le schema est ajouté -- erreur 400
    nom: str = Field(min_length=1, max_length=50)
    prenom: str = Field(min_length=1, max_length=50)
    annee: int = Field(ge=1)
    familier: str = Field(min_length=1, max_length=50)
    statut: Literal["inscrit", "diplome", "renvoye"] = Field(default="inscrit")
    maison_id: int
    #ge=1 --> capacité et id toujours strictement positifs ; pattern --> format "YYYY-YYYY" imposé


class EleveUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nom: str | None = Field(default=None, min_length=1, max_length=50)
    prenom: str | None = Field(default=None, min_length=1, max_length=50)
    annee: int | None = Field(ge=1,default=None)
    familier: str | None = Field(min_length=1, max_length=50, default=None)
    statut: Literal["inscrit", "diplome", "renvoye"] | None = Field(default="inscrit")
    maison_id: int | None = Field(default=None, ge=1)


class EleveOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    prenom: str
    annee: int
    familier: str
    statut: Literal["inscrit", "diplome", "renvoye"]
    maison_id: int
    created_at: datetime
    updated_at: datetime
