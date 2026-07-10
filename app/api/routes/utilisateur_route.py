"""Routes (blueprint) de la ressource Utilisateur.

Mappe les URLs HTTP vers les fonctions du controller. Aucune logique métier
ni validation ici : uniquement le routage. Le blueprint est enregistré dans
l'app factory.
"""
from flask import Blueprint

from app.api.controllers import controller_utilisateur as controller

utilisateur_bp = Blueprint("utilisateurs", __name__, url_prefix="/utilisateurs")

utilisateur_bp.add_url_rule("", view_func=controller.lister, methods=["GET"])
utilisateur_bp.add_url_rule("/<int:utilisateur_id>", view_func=controller.recuperer, methods=["GET"])
utilisateur_bp.add_url_rule("", view_func=controller.creer, methods=["POST"])
utilisateur_bp.add_url_rule("/<int:utilisateur_id>", view_func=controller.modifier, methods=["PATCH"])
utilisateur_bp.add_url_rule("/<int:utilisateur_id>", view_func=controller.supprimer, methods=["DELETE"])
