"""Repository Élève : accès aux données pour la ressource Élève.

Seul endroit qui exécute des requêtes SQLAlchemy sur cette table (CRUD).
Aucune logique HTTP ni décision métier ici : sait chercher/écrire, pas décider.
"""

from app.dal.models import Eleve
from app.dal.database import db

def lister_eleve():
    liste_eleve = db.session.execute(db.select(Eleve)).scalars().all()
    return liste_eleve

def get_by_id(eleve_id):
    result = db.session.get(Eleve, eleve_id) #le .get renvoie None si l'élément est absent, pour éviter les plantages. Pas besoin de rajouter de if non plus.
    return result

def create_eleve(data):
    new_eleve = Eleve(
        nom = data["nom"],
        prenom=data["prenom"],
        annee=data["annee"],
        maison_id=data["maison_id"],
        familier = data["familier"],
        statut = data["statut"]
    )
    db.session.add(new_eleve)
    db.session.commit()
    return new_eleve


def update_eleve(eleve_id, data):
    eleve_to_update = get_by_id(eleve_id)
    if eleve_to_update is None:
        return None
    eleve_to_update.nom = data.get("nom", eleve_to_update.nom)
    eleve_to_update.prenom = data.get("prenom", eleve_to_update.prenom)
    eleve_to_update.annee = data.get("annee", eleve_to_update.annee)
    eleve_to_update.maison_id = data.get("maison_id", eleve_to_update.maison_id)
    eleve_to_update.familier = data.get("familier", eleve_to_update.familier)
    eleve_to_update.statut = data.get("statut", eleve_to_update.statut)
    db.session.commit()
    return eleve_to_update

def delete_eleve(eleve_id):
    eleve_to_delete = get_by_id(eleve_id)
    if eleve_to_delete is None:
        return False
    db.session.delete(eleve_to_delete)
    db.session.commit()
    return True #les réponses True et False seront gérées dans le controller.