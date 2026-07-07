# Exercice final Flask + SQLAlchemy — L'Académie de Sorcellerie

API REST gérant la vie académique d'une académie de sorcellerie : élèves, maisons,
cours, examens, compétences, tournois et passage de fin d'année.

Projet réalisé en solo sur 4 jours.

## Choix techniques et justifications

| Choix | Décision | Raisonnement |
|---|---|---|
| **Langage / framework** | Python 3 + Flask | Imposé par le cahier des charges. |
| **Accès aux données** | Flask-SQLAlchemy | Imposé par le cahier des charges. |
| **Architecture** | App factory + blueprints | Le projet grandit sur 4 jours et doit être testé. L'app factory permet une configuration de test isolée (base séparée, pas d'effets de bord), et les blueprints découpent le code par domaine métier (maisons, élèves, cours, examens, compétences, tournois...) plutôt qu'un monolithe qui devient vite illisible. |
| **Base de données** | SQLite | Zéro installation, fichier unique versionnable/reproductible. Rend le critère « cloner le repo et suivre le README sans aide » trivial à satisfaire. SQLAlchemy permet de basculer vers une autre base plus tard si besoin. |
| **Validation des payloads** | Pydantic (v2) | Bibliothèque de validation moderne et typée. Séparation nette entre les modèles SQLAlchemy (persistance) et les schémas Pydantic (validation d'entrée / sérialisation de sortie), ce qui évite le couplage. Messages d'erreur précis par champ, exigés au jour 4. |

### Points de vigilance liés à ces choix

- **Pydantic n'a pas d'intégration native Flask** : une brique de glue maison parse le JSON
  de la requête vers un modèle Pydantic et renvoie un `400` avec le champ fautif en cas
  d'échec. Conçue une seule fois, réutilisée sur tous les endpoints d'écriture.
- **created_at / updated_at** (exigés au jour 4) sont posés dès le début via une classe de
  base commune, pour éviter d'avoir à les ajouter rétroactivement à toutes les tables.
- **Middleware `X-User-Id`** : brique réutilisable (hook/décorateur) posée dès le jour 1,
  utilisée toute la semaine pour distinguer espace élève / espace admin.

## Démarrage

> À compléter au fil du projet : installation, variables d'environnement, commande de seed,
> commande de lancement, commande de tests.
