from flask import Blueprint

from app.api.controllers import controller_cours as controller

cours_bp = Blueprint("cours", __name__, url_prefix="/cours")

cours_bp.add_url_rule("", view_func=controller.lister, methods=["GET"])
cours_bp.add_url_rule("/<int:cours_id>", view_func=controller.recuperer, methods=["GET"])
cours_bp.add_url_rule("", view_func=controller.creer, methods=["POST"])
cours_bp.add_url_rule("/<int:cours_id>", view_func=controller.modifier, methods=["PATCH"])
cours_bp.add_url_rule("/<int:cours_id>", view_func=controller.supprimer, methods=["DELETE"])
