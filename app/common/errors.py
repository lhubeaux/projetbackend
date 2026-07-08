"""Handlers d'erreur pour des réponses JSON cohérentes.

Centralise la mise en forme des erreurs (404, 405, 409...) afin que tous les
endpoints renvoient un corps JSON homogène avec le bon code HTTP, au lieu des
pages HTML par défaut. Enregistrés dans l'app factory via
register_error_handlers(app).
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError

from app.dal.database import db

def register_error_handlers(app):

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(err):
        db.session.rollback()
        return jsonify(
            {"error": "Conflit : violation d'une contrainte d'unicité ou d'intégrité"}
        ), 409

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        return jsonify({"error": err.description}), err.code
