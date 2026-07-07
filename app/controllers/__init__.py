"""Controllers : fonctions de traitement, une par action, un fichier par domaine.

Chaque fonction orchestre UN endpoint HTTP : valide le payload (schemas/),
délègue à un service (services/) ou directement au dal/ pour le CRUD simple,
puis met en forme la réponse JSON avec le bon code HTTP.

Reste fin : aucune requête SQL directe, aucune règle métier complexe ici.
"""
