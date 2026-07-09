"""Controller Cours : orchestre la logique HTTP de la ressource.

Valide l'entrée via les schémas Pydantic, délègue la persistance au
repository, renvoie une réponse JSON avec le bon code HTTP.
"""

from flask import jsonify, abort, make_response
from app.common.validation import validate_body
from app.api.schemas.cours_schema import CoursCreate, CoursUpdate, CoursOut
from app.dal.repositories import cours_repository as repo
from app.dal.repositories import professeur_repository as prof_repo



def _serialize(cours):
    return CoursOut.model_validate(cours).model_dump(mode="json")

def _verifier_professeur(professeur_id):
    """Interrompt la requête (400) si le professeur référencé n'existe pas."""
    if prof_repo.get_by_id(professeur_id) is None:
        abort(make_response(jsonify({"error": f"Professeur {professeur_id} introuvable"}), 400))


def lister():
    cours = repo.lister_cours()
    return jsonify([_serialize(c) for c in cours]), 200


def recuperer(cours_id):
    cours = repo.get_by_id(cours_id)
    if cours is None:
        abort(make_response(jsonify({"error": "Cours introuvable"}), 404))
    return jsonify(_serialize(cours)), 200

def creer():
    donnees = validate_body(CoursCreate)
    _verifier_professeur(donnees.professeur_id)
    cours = repo.create_cours(donnees.model_dump())
    return jsonify(_serialize(cours)), 201



def modifier(cours_id):
    donnees = validate_body(CoursUpdate)
    champs = donnees.model_dump(exclude_unset=True)
    # Avec exclude_unset=True, seuls les champs réellement envoyés par le client sont dans le dict. Les autres sont absents
    if "professeur_id" in champs:
        _verifier_professeur(champs["professeur_id"])
    cours = repo.update_cours(cours_id, champs)
    if cours is None:
        abort(make_response(jsonify({"error": "Cours introuvable"}), 404))
    return jsonify(_serialize(cours)), 200



def supprimer(cours_id):
    supprime = repo.delete_cours(cours_id)
    if not supprime:
        abort(make_response(jsonify({"error": "Cours introuvable"}), 404))
    return "", 204