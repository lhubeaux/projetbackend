"""Repositories : la seule couche qui exécute des requêtes SQLAlchemy.

Un repository par domaine (app/dal/repositories/eleve_repository.py, ...).
Contient les opérations de lecture/écriture (get, list, create, update,
delete) et les requêtes optimisées (joinedload/selectinload pour la chasse
au N+1 du jour 2). Ne connaît ni le HTTP ni les règles métier.
"""
