"""Routes (blueprint) de la ressource Maison.

Mappe les URLs HTTP vers les fonctions du controller. Aucune logique métier
ni validation ici : uniquement le routage. Le blueprint est enregistré dans
l'app factory.
"""
from flask import Blueprint

from app.api.controllers import controller_maison as controller

maison_bp = Blueprint("maisons", __name__, url_prefix="/maisons")

maison_bp.add_url_rule("", view_func=controller.lister, methods=["GET"])
maison_bp.add_url_rule("/<int:maison_id>", view_func=controller.recuperer, methods=["GET"])
maison_bp.add_url_rule("", view_func=controller.creer, methods=["POST"])
maison_bp.add_url_rule("/<int:maison_id>", view_func=controller.modifier, methods=["PATCH"])
maison_bp.add_url_rule("/<int:maison_id>", view_func=controller.supprimer, methods=["DELETE"])
