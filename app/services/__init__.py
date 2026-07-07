"""Couche métier : logique complexe, indépendante du HTTP et testable seule.

C'est ici que vivent les endpoints métier du projet :
    - clôture d'un examen (mise à jour des statuts d'inscription, moyenne)
    - déblocage idempotent des compétences après un examen
    - clôture d'un tournoi (vainqueur global, réputation de maison)
    - passage de fin d'année (promotion / redoublement / diplomation, anti-rejeu)

Ces fonctions sont appelées par les controllers et directement par les tests.
Elles orchestrent les règles métier et délèguent les requêtes au dal/.
"""
