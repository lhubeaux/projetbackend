"""Routes (blueprint) de la ressource Professeur.

Mappe les URLs HTTP vers les fonctions du controller. Aucune logique métier
ni validation ici : uniquement le routage. Le blueprint est enregistré dans
l'app factory.
"""
from flask import Blueprint

from app.api.controllers import controller_professeur as controller

professeur_bp = Blueprint("professeurs", __name__, url_prefix="/professeurs")

professeur_bp.add_url_rule("", view_func=controller.lister, methods=["GET"])
professeur_bp.add_url_rule("/<int:professeur_id>", view_func=controller.recuperer, methods=["GET"])
professeur_bp.add_url_rule("", view_func=controller.creer, methods=["POST"])
professeur_bp.add_url_rule("/<int:professeur_id>", view_func=controller.modifier, methods=["PATCH"])
professeur_bp.add_url_rule("/<int:professeur_id>", view_func=controller.supprimer, methods=["DELETE"])
