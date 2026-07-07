"""Fixtures pytest communes.

Monte une application de test via create_app(TestConfig) avec une base isolée,
crée le schéma, fournit un client de test et une session propre par test.
Sert de socle aux tests métier (au moins un scénario réel par jour) :

    - jour 2 : clôture d'examen (statuts), inscription à un cours complet refusée
    - jour 3 : déblocage idempotent d'une compétence ; vainqueur de tournoi + réputation
    - jour 4 : passage d'année (promotion / redoublement / diplomation) ; anti double clôture
"""
