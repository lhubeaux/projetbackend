"""Controller Maison : orchestre la logique HTTP de la ressource.

Reçoit la requête (déjà routée), valide l'entrée via les schémas Pydantic,
délègue la persistance au repository, renvoie une réponse JSON avec le bon
code HTTP. Aucune requête SQL ici (rôle du repository).
"""
from flask import jsonify, abort, make_response

from app.common.validation import validate_body
from app.api.schemas.maison_schema import MaisonCreate, MaisonUpdate, MaisonOut
from app.dal.repositories import maison_repository as repo


def _serialize(maison):
    return MaisonOut.model_validate(maison).model_dump(mode="json")


def lister():
    maisons = repo.lister_maisons()
    return jsonify([_serialize(m) for m in maisons]), 200


def recuperer(maison_id):
    maison = repo.get_by_id(maison_id)
    if maison is None:
        abort(make_response(jsonify({"error": "Maison introuvable"}), 404))
    return jsonify(_serialize(maison)), 200


def creer():
    donnees = validate_body(MaisonCreate)
    maison = repo.create_maison(donnees.model_dump())
    return jsonify(_serialize(maison)), 201


def modifier(maison_id):
    donnees = validate_body(MaisonUpdate)
    maison = repo.update_maison(maison_id, donnees.model_dump(exclude_unset=True))
    # Avec exclude_unset=True, seuls les champs réellement envoyés par le client sont dans le dict. Les autres sont absents
    if maison is None:
        abort(make_response(jsonify({"error": "Maison introuvable"}), 404))
    return jsonify(_serialize(maison)), 200


def supprimer(maison_id):
    maison = repo.get_by_id(maison_id)
    if maison is None:
        abort(make_response(jsonify({"error": "Maison introuvable"}), 404))

    nb_eleves = len(maison.eleves)
    if nb_eleves > 0:
        abort(make_response(jsonify({
            "error": f"Impossible de supprimer : cette maison compte {nb_eleves} élèves"
        }), 409))

    repo.delete_maison(maison_id)
    return "", 204

