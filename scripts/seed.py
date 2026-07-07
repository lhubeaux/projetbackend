"""Script de seed idempotent.

Peuple la base sans dupliquer ni casser les données quand on le relance
(get-or-create plutôt que create aveugle).

Volume attendu :
    - jour 1 : >= 4 maisons, ~30 élèves sur les 7 années, quelques profs/cours,
      un utilisateur par élève/professeur + un compte admin.
    - jour 4 : montée à >= 150 élèves, plusieurs examens, plusieurs tournois,
      un historique de compétences déjà débloquées.

Lancé via une commande documentée dans le README.
"""
