"""Controller Élève : orchestre la logique HTTP de la ressource.

Valide l'entrée via les schémas Pydantic, délègue la persistance au
repository, renvoie une réponse JSON avec le bon code HTTP.
"""

from flask import jsonify, abort, make_response
from app.common.validation import validate_body
from app.api.schemas.eleve_schema import EleveCreate, EleveUpdate, EleveOut
from app.dal.repositories import eleve_repository as repo
from app.dal.repositories import maison_repository as maison_repo



def _serialize(eleve):
    return EleveOut.model_validate(eleve).model_dump(mode="json")

def _verifier_maison(maison_id):
    """Interrompt la requête (400) si le maison référencé n'existe pas."""
    if maison_repo.get_by_id(maison_id) is None:
        abort(make_response(jsonify({"error": f"Maison {maison_id} introuvable"}), 400))


def lister():
    eleve = repo.lister_eleve()
    return jsonify([_serialize(c) for c in eleve]), 200


def recuperer(eleve_id):
    eleve = repo.get_by_id(eleve_id)
    if eleve is None:
        abort(make_response(jsonify({"error": "Eleve introuvable"}), 404))
    return jsonify(_serialize(eleve)), 200

def creer():
    donnees = validate_body(EleveCreate)
    _verifier_maison(donnees.maison_id)
    eleve = repo.create_eleve(donnees.model_dump())
    return jsonify(_serialize(eleve)), 201



def modifier(eleve_id):
    donnees = validate_body(EleveUpdate)
    champs = donnees.model_dump(exclude_unset=True)
    # Avec exclude_unset=True, seuls les champs réellement envoyés par le client sont dans le dict. Les autres sont absents
    if "maison_id" in champs:
        _verifier_maison(champs["maison_id"])
    eleve = repo.update_eleve(eleve_id, champs)
    if eleve is None:
        abort(make_response(jsonify({"error": "Eleve introuvable"}), 404))
    return jsonify(_serialize(eleve)), 200



def supprimer(eleve_id):
    supprime = repo.delete_eleve(eleve_id)
    if not supprime:
        abort(make_response(jsonify({"error": "Eleve introuvable"}), 404))
    return "", 204