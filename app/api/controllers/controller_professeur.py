"""Controller Professeur : orchestre la logique HTTP de la ressource.

Valide l'entrée via les schémas Pydantic, délègue la persistance au
repository, renvoie une réponse JSON avec le bon code HTTP.
"""

from flask import jsonify, abort, make_response
from app.common.validation import validate_body
from app.api.schemas.professeur_schema import ProfesseurCreate, ProfesseurUpdate, ProfesseurOut
from app.dal.repositories import professeur_repository as repo


def _serialize(professeur):
    return ProfesseurOut.model_validate(professeur).model_dump(mode="json")


def lister():
    professeurs = repo.lister_professeurs()
    return jsonify([_serialize(p) for p in professeurs]), 200


def recuperer(professeur_id):
    professeur = repo.get_by_id(professeur_id)
    if professeur is None:
        abort(make_response(jsonify({"error": "Professeur introuvable"}), 404))
    return jsonify(_serialize(professeur)), 200


def creer():
    donnees = validate_body(ProfesseurCreate)
    professeur = repo.create_professeur(donnees.model_dump())
    return jsonify(_serialize(professeur)), 201


def modifier(professeur_id):
    donnees = validate_body(ProfesseurUpdate)
    professeur = repo.update_professeur(professeur_id, donnees.model_dump(exclude_unset=True))
    # Avec exclude_unset=True, seuls les champs réellement envoyés par le client sont dans le dict. Les autres sont absents
    if professeur is None:
        abort(make_response(jsonify({"error": "Professeur introuvable"}), 404))
    return jsonify(_serialize(professeur)), 200


def supprimer(professeur_id):
    professeur = repo.get_by_id(professeur_id)
    if professeur is None:
        abort(make_response(jsonify({"error": "Professeur introuvable"}), 404))

    nb_cours = len(professeur.cours)
    if nb_cours > 0:
        abort(make_response(jsonify({
            "error": f"Impossible de supprimer : ce professeur est responsable de {nb_cours} cours"
        }), 409))

    repo.delete_professeur(professeur_id)
    return "", 204

