"""DAL — Data Access Layer.

Dossier « parapluie » regroupant tout ce qui touche à l'accès aux données :
    - database.py    : l'instance SQLAlchemy partagée (db)
    - models/        : les classes SQLAlchemy (les tables)
    - repositories/  : les requêtes SQLAlchemy, un repository par entité

Aucune logique HTTP ni métier ici.
"""
