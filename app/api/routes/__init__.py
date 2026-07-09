"""Registre des blueprints de l'API."""
from app.api.routes.maison_route import maison_bp
from app.api.routes.professeur_route import professeur_bp

ALL_BLUEPRINTS = (
    maison_bp,
    professeur_bp,
)
