"""Data Access Layer : la seule couche qui exécute des requêtes SQLAlchemy.

Un repository par domaine (eleve_repository.py, cours_repository.py, ...).
Contient les opérations de lecture/écriture (get, list, create, update,
delete) et les requêtes optimisées (joinedload/selectinload pour la chasse
au N+1 du jour 2). Ne connaît ni le HTTP ni les règles métier.
"""
