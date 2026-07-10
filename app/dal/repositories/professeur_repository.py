"""Repository Professeur : accès aux données pour la ressource Professeur.

Seul endroit qui exécute des requêtes SQLAlchemy sur cette table (CRUD).
Aucune logique HTTP ni décision métier ici : sait chercher/écrire, pas décider.
"""

from app.dal.models import Professeur
from app.dal.database import db

def lister_professeurs():
    liste_professeurs = db.session.execute(db.select(Professeur)).scalars().all()
    return liste_professeurs

def get_by_id(professeur_id):
    result = db.session.get(Professeur, professeur_id) #le .get renvoie None si l'élément est absent, pour éviter les plantages. Pas besoin de rajouter de if non plus.
    return result

def create_professeur(data):
    new_professeur = Professeur(
        nom = data["nom"],
        prenom=data["prenom"],
        matiere=data["matiere"],
        anciennete=data.get("anciennete", 0)
    )
    db.session.add(new_professeur)
    db.session.commit()
    return new_professeur


def update_professeur(professeur_id, data):
    professeur_to_update = get_by_id(professeur_id)
    if professeur_to_update is None:
        return None
    professeur_to_update.nom = data.get("nom", professeur_to_update.nom)
    professeur_to_update.prenom = data.get("prenom", professeur_to_update.prenom)
    professeur_to_update.matiere = data.get("matiere", professeur_to_update.matiere)
    professeur_to_update.anciennete = data.get("anciennete", professeur_to_update.anciennete)
    db.session.commit()
    return professeur_to_update

def delete_professeur(professeur_id):
    professeur_to_delete = get_by_id(professeur_id)
    if professeur_to_delete is None:
        return False
    db.session.delete(professeur_to_delete)
    db.session.commit()
    return True #les réponses True et False seront gérées dans le controller.