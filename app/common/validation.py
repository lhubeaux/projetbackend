"""Glue entre Pydantic et Flask.

Point d'entrée unique qui parse le JSON de la requête vers un schéma Pydantic
et, en cas d'échec, renvoie un 400 indiquant précisément le champ fautif.
Conçu une fois, réutilisé sur tous les endpoints d'écriture (exigence jour 4).
"""
from flask import request, abort, make_response, jsonify
from pydantic import ValidationError


def validate_body(schema):
    data = request.get_json(silent=True)
    if data is None:
        abort(make_response(
            jsonify({"error": "Corps JSON manquant ou invalide"}), 400
        ))
    try:
        return schema.model_validate(data)
    except ValidationError as exc:
        details = [
            {"champ": ".".join(str(p) for p in err["loc"]), "message": err["msg"]}
            for err in exc.errors()
        ]
        abort(make_response(
            jsonify({"error": "Validation échouée", "details": details}), 400
        ))