"""Repository Utilisateur : accès aux données pour la ressource Utilisateur.

Seul endroit qui exécute des requêtes SQLAlchemy sur cette table (CRUD).
Aucune logique HTTP ni décision métier ici : sait chercher/écrire, pas décider.
"""

from app.dal.models import Utilisateur
from app.dal.database import db

def lister_utilisateurs():
    liste_utilisateurs = db.session.execute(db.select(Utilisateur)).scalars().all()
    return liste_utilisateurs

def get_by_id(utilisateur_id):
    result = db.session.get(Utilisateur, utilisateur_id) #le .get renvoie None si l'élément est absent, pour éviter les plantages. Pas besoin de rajouter de if non plus.
    return result

def get_by_email(email):
    #le .get ne fonctionne que sur la clé primaire : pour chercher par email il faut un select().where()
    result = db.session.execute(
        db.select(Utilisateur).where(Utilisateur.email == email)
    ).scalar_one_or_none() #email est unique : au plus un résultat, ou None
    return result

def create_utilisateur(data):
    new_utilisateur = Utilisateur(
        email = data["email"],
        mot_de_passe=data["mot_de_passe"],
        role=data["role"],
        eleve_id=data.get("eleve_id"), #FK nullables : .get renvoie None si absent (cas de l'admin)
        professeur_id=data.get("professeur_id")
    )
    db.session.add(new_utilisateur)
    db.session.commit()
    return new_utilisateur


def update_utilisateur(utilisateur_id, data):
    utilisateur_to_update = get_by_id(utilisateur_id)
    if utilisateur_to_update is None:
        return None
    #seuls email et mot_de_passe sont modifiables : role et les FK ne changent pas par un PATCH
    utilisateur_to_update.email = data.get("email", utilisateur_to_update.email)
    utilisateur_to_update.mot_de_passe = data.get("mot_de_passe", utilisateur_to_update.mot_de_passe)
    db.session.commit()
    return utilisateur_to_update

def delete_utilisateur(utilisateur_id):
    utilisateur_to_delete = get_by_id(utilisateur_id)
    if utilisateur_to_delete is None:
        return False
    db.session.delete(utilisateur_to_delete)
    db.session.commit()
    return True #les réponses True et False seront gérées dans le controller.
