"""Modèles SQLAlchemy (couche persistance).

Un fichier par domaine : maison.py, professeur.py, cours.py, eleve.py,
utilisateur.py, inscription.py, examen.py, resultat.py, competence.py,
maitrise.py, tournoi.py, duel.py, cloture_annee.py.

Chaque fichier définit une classe = une table (colonnes, relations,
contraintes d'unicité). Aucune logique HTTP ni métier ici.
"""
from app.dal.models.maison import Maison