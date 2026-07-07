# Performance — chasse au N+1

> À documenter au jour 2, puis à réappliquer au jour 4 si un nouvel endpoint de
> listing en a besoin.

## Contexte

Lister les élèves d'un cours (ou les cours d'un élève) et accéder à une relation
(`eleve.maison.nom`) dans une boucle déclenche, en chargement paresseux, une
requête SQL par élément → problème N+1.

## Mesure avant / après

Activer `SQLALCHEMY_ECHO = True`, compter les requêtes sur un endpoint de listing.

| Endpoint | Requêtes AVANT | Requêtes APRÈS | Correctif |
|----------|----------------|----------------|-----------|
| _(à remplir)_ | | | joinedload / selectinload |

Le chargement optimisé est rendu **optionnel** via un paramètre de requête plutôt
que systématique.
