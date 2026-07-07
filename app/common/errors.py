"""Handlers d'erreur pour des réponses JSON cohérentes.

Centralise la mise en forme des erreurs (400, 401, 404, 409, ...) afin que
tous les endpoints renvoient un corps JSON homogène avec le bon code HTTP.
Enregistrés dans l'app factory.
"""
