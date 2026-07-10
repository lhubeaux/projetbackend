"""Registre des blueprints de l'API."""
from app.api.routes.maison_route import maison_bp
from app.api.routes.professeur_route import professeur_bp
from app.api.routes.cours_route import cours_bp
from app.api.routes.eleve_route import eleve_bp

ALL_BLUEPRINTS = (
    maison_bp,
    professeur_bp,
    cours_bp,
    eleve_bp
)
