"""Authentification simulée via le header X-User-Id.

Fournit la brique (décorateur ou hook before_request) qui lit X-User-Id,
identifie l'utilisateur courant et distingue espace élève / espace admin.
Un appel sans header sur un endpoint qui en a besoin doit renvoyer une erreur
explicite (401/400), pas un comportement silencieux.

Sécurité volontairement simulée à ce stade (cf. cahier des charges).
"""
