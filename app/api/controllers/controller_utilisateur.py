"""Controller Utilisateur : orchestre la logique HTTP de la ressource.

Valide l'entrée via les schémas Pydantic, délègue la persistance au
repository, renvoie une réponse JSON avec le bon code HTTP.
"""

from flask import jsonify, abort, make_response
from app.common.validation import validate_body
from app.api.schemas.utilisateur_schema import UtilisateurCreate, UtilisateurUpdate, UtilisateurOut
from app.dal.repositories import utilisateur_repository as repo
from app.dal.repositories import eleve_repository as eleve_repo
from app.dal.repositories import professeur_repository as prof_repo


def _serialize(utilisateur):
    return UtilisateurOut.model_validate(utilisateur).model_dump(mode="json")


def _verifier_eleve(eleve_id):
    """Interrompt la requête (400) si l'élève référencé n'existe pas."""
    if eleve_repo.get_by_id(eleve_id) is None:
        abort(make_response(jsonify({"error": f"Eleve {eleve_id} introuvable"}), 400))


def _verifier_professeur(professeur_id):
    """Interrompt la requête (400) si le professeur référencé n'existe pas."""
    if prof_repo.get_by_id(professeur_id) is None:
        abort(make_response(jsonify({"error": f"Professeur {professeur_id} introuvable"}), 400))


def _verifier_email_libre(email, utilisateur_id=None):
    """Interrompt la requête (409) si l'email appartient déjà à un AUTRE utilisateur.

    utilisateur_id : l'utilisateur en cours de modification (PATCH), exclu de la
    comparaison — sinon lui renvoyer son propre email déclencherait un conflit.
    """
    existant = repo.get_by_email(email)
    if existant is not None and existant.id != utilisateur_id:
        abort(make_response(jsonify({"error": f"L'email {email} est déjà utilisé"}), 409))


def lister():
    utilisateurs = repo.lister_utilisateurs()
    return jsonify([_serialize(u) for u in utilisateurs]), 200


def recuperer(utilisateur_id):
    utilisateur = repo.get_by_id(utilisateur_id)
    if utilisateur is None:
        abort(make_response(jsonify({"error": "Utilisateur introuvable"}), 404))
    return jsonify(_serialize(utilisateur)), 200


def creer():
    donnees = validate_body(UtilisateurCreate)  # 400 : payload mal formé, ou role/lien incohérents
    _verifier_email_libre(donnees.email)        # 409 : email déjà pris
    # Le model_validator garantit qu'une FK non-None correspond bien au role.
    # Ici on ne vérifie plus QUE l'existence en base.
    if donnees.eleve_id is not None:
        _verifier_eleve(donnees.eleve_id)
    if donnees.professeur_id is not None:
        _verifier_professeur(donnees.professeur_id)
    utilisateur = repo.create_utilisateur(donnees.model_dump())
    return jsonify(_serialize(utilisateur)), 201


def modifier(utilisateur_id):
    donnees = validate_body(UtilisateurUpdate)
    champs = donnees.model_dump(exclude_unset=True)
    # Avec exclude_unset=True, seuls les champs réellement envoyés par le client sont dans le dict.
    if "email" in champs:
        _verifier_email_libre(champs["email"], utilisateur_id)
    # Aucune FK à vérifier : UtilisateurUpdate ne les expose pas.
    utilisateur = repo.update_utilisateur(utilisateur_id, champs)
    if utilisateur is None:
        abort(make_response(jsonify({"error": "Utilisateur introuvable"}), 404))
    return jsonify(_serialize(utilisateur)), 200


def supprimer(utilisateur_id):
    supprime = repo.delete_utilisateur(utilisateur_id)
    if not supprime:
        abort(make_response(jsonify({"error": "Utilisateur introuvable"}), 404))
    return "", 204
