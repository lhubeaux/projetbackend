"""Routes (blueprint) de la ressource Élève.

Mappe les URLs HTTP vers les fonctions du controller. Aucune logique métier
ni validation ici : uniquement le routage. Le blueprint est enregistré dans
l'app factory.
"""
from flask import Blueprint

from app.api.controllers import controller_eleve as controller

eleve_bp = Blueprint("eleves", __name__, url_prefix="/eleves")

eleve_bp.add_url_rule("", view_func=controller.lister, methods=["GET"])
eleve_bp.add_url_rule("/<int:eleve_id>", view_func=controller.recuperer, methods=["GET"])
eleve_bp.add_url_rule("", view_func=controller.creer, methods=["POST"])
eleve_bp.add_url_rule("/<int:eleve_id>", view_func=controller.modifier, methods=["PATCH"])
eleve_bp.add_url_rule("/<int:eleve_id>", view_func=controller.supprimer, methods=["DELETE"])
