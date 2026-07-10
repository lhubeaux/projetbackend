"""Repository Cours : accès aux données pour la ressource Cours.

Seul endroit qui exécute des requêtes SQLAlchemy sur cette table (CRUD).
Aucune logique HTTP ni décision métier ici : sait chercher/écrire, pas décider.
"""

from app.dal.models import Cours
from app.dal.database import db

def lister_cours():
    liste_cours = db.session.execute(db.select(Cours)).scalars().all()
    return liste_cours

def get_by_id(cours_id):
    result = db.session.get(Cours, cours_id) #le .get renvoie None si l'élément est absent, pour éviter les plantages. Pas besoin de rajouter de if non plus.
    return result

def create_cours(data):
    new_cours = Cours(
        intitule = data["intitule"],
        niveau=data["niveau"],
        capacite_max=data["capacite_max"],
        professeur_id=data["professeur_id"],
        annee_academique = data["annee_academique"]
    )
    db.session.add(new_cours)
    db.session.commit()
    return new_cours


def update_cours(cours_id, data):
    cours_to_update = get_by_id(cours_id)
    if cours_to_update is None:
        return None
    cours_to_update.intitule = data.get("intitule", cours_to_update.intitule)
    cours_to_update.niveau = data.get("niveau", cours_to_update.niveau)
    cours_to_update.capacite_max = data.get("capacite_max", cours_to_update.capacite_max)
    cours_to_update.professeur_id = data.get("professeur_id", cours_to_update.professeur_id)
    cours_to_update.annee_academique = data.get("annee_academique", cours_to_update.annee_academique)
    db.session.commit()
    return cours_to_update

def delete_cours(cours_id):
    cours_to_delete = get_by_id(cours_id)
    if cours_to_delete is None:
        return False
    db.session.delete(cours_to_delete)
    db.session.commit()
    return True #les réponses True et False seront gérées dans le controller.