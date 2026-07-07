"""API — couche web.

Dossier « parapluie » regroupant tout ce qui expose l'application au monde HTTP :
    - routes/       : les blueprints (URL -> fonction du controller)
    - controllers/  : les fonctions de traitement (une par action)
    - schemas/      : les schémas Pydantic (validation entrée / sérialisation sortie)

Ne contient ni requête SQL directe, ni règle métier complexe (celle-ci vit dans services/).
"""
