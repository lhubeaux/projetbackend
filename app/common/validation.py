"""Glue entre Pydantic et Flask.

Point d'entrée unique qui parse le JSON de la requête vers un schéma Pydantic
et, en cas d'échec, renvoie un 400 indiquant précisément le champ fautif.
Conçu une fois, réutilisé sur tous les endpoints d'écriture (exigence jour 4).
"""
