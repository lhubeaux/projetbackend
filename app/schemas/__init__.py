"""Schémas Pydantic (validation entrée / sérialisation sortie).

Séparés des modèles SQLAlchemy pour éviter le couplage persistance/validation.
Un fichier par domaine, avec typiquement un schéma de création, un schéma de
mise à jour et un schéma de sortie.

Rappel jour 4 : un payload invalide doit produire un 400 indiquant précisément
le champ fautif (glue Pydantic dans app/common/validation.py).
"""
