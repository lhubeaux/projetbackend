from app.dal.models import Maison
from app.dal.database import db

def lister_maisons():
    liste_maisons = db.session.execute(db.select(Maison)).scalars().all()
    return liste_maisons

def get_by_id(maison_id):
    result = db.session.get(Maison, maison_id) #le .get renvoie None si l'élément est absent, pour éviter les plantages. Pas besoin de rajouter de if non plus.
    return result

def create_maison(data):
    new_maison = Maison(
        nom = data["nom"],
        couleur=data.get("couleur"),
        fondateur=data.get("fondateur"),
        valeurs=data.get("valeurs")
    )
    db.session.add(new_maison)
    db.session.commit()
    return new_maison


def update_maison(maison_id, data):
    maison_to_update = get_by_id(maison_id)
    if maison_to_update is None:
        return None
    maison_to_update.nom = data.get("nom", maison_to_update.nom)
    maison_to_update.couleur = data.get("couleur", maison_to_update.couleur)
    maison_to_update.fondateur = data.get("fondateur", maison_to_update.fondateur)
    maison_to_update.valeurs = data.get("valeurs", maison_to_update.valeurs)
    db.session.commit()
    return maison_to_update

def delete_maison(maison_id):
    maison_to_delete = get_by_id(maison_id)
    if maison_to_delete is None:
        return False
    db.session.delete(maison_to_delete)
    db.session.commit()
    return True #les réponses True et False seront gérées dans le controller.