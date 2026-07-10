# Documentation technique — L'Académie de Sorcellerie

Référence du code : rôle de chaque module, de chaque fonction, et description des
modèles de données. Pour le *pourquoi* des concepts, voir [explications.md](explications.md).
Pour le plan de travail restant, voir [plan.md](plan.md).

---

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Le trajet d'une requête](#le-trajet-dune-requête)
3. [Arborescence](#arborescence)
4. [Racine du projet](#racine-du-projet)
5. [Couche `dal/` — accès aux données](#couche-dal--accès-aux-données)
6. [Les modèles en détail](#les-modèles-en-détail)
7. [Les repositories](#les-repositories)
8. [Couche `api/` — la couche web](#couche-api--la-couche-web)
9. [Les schémas Pydantic](#les-schémas-pydantic)
10. [Les controllers](#les-controllers)
11. [Les routes](#les-routes)
12. [Couche `common/` — briques transverses](#couche-common--briques-transverses)
13. [Couche `services/` — logique métier](#couche-services--logique-métier)
14. [Tests et scripts](#tests-et-scripts)
15. [Référence des endpoints](#référence-des-endpoints)
16. [Conventions du projet](#conventions-du-projet)
17. [État d'avancement](#état-davancement)

---

## Vue d'ensemble

API REST Flask + SQLAlchemy gérant la vie académique d'une école de sorcellerie.
L'architecture est **en couches**, chaque couche ayant une seule responsabilité :

| Couche | Question à laquelle elle répond | Ce qu'elle ignore |
|---|---|---|
| `api/routes/` | À quelle URL répond-on ? | Tout le reste |
| `api/controllers/` | Que fait-on de cette requête HTTP ? | Le SQL |
| `api/schemas/` | Cette donnée est-elle valide ? Quelle forme renvoyer ? | La base, le HTTP |
| `services/` | Quelle décision métier prendre ? | Le HTTP |
| `dal/repositories/` | Comment lire/écrire en base ? | Le HTTP, les décisions |
| `dal/models/` | Qu'est-ce qu'une entité ? | Tout le reste |
| `common/` | Briques partagées (auth, validation, erreurs) | — |

**Règle d'or** : ça parle HTTP → `api/` ; ça décide → `services/` ; ça lit/écrit → `dal/`.

---

## Le trajet d'une requête

```
Requête HTTP
   ▼
api/routes ──▶ api/controllers ──▶ services ──▶ dal/repositories ──▶ dal/models ──▶ SQLite
   (URL)         (orchestration)     (métier)      (requêtes SQL)       (tables)
                      └── api/schemas (valide l'entrée / met en forme la sortie)

common/ = briques transverses (auth, validation, erreurs)
```

Un endpoint d'écriture suit toujours le même motif :

```
valider la forme  →  valider les références  →  agir  →  répondre
   (Pydantic)          (_verifier_xxx)         (repo)    (jsonify + code)
```

---

## Arborescence

```
projetbackend/
├── config.py                 # Réglages par environnement
├── run.py                    # Point d'entrée (démarrage du serveur)
├── documentation.md          # Ce fichier
├── explications.md           # Concepts expliqués au fil du projet
├── plan.md                   # Plan de travail des 4 jours
├── readme.md                 # Choix techniques + démarrage
├── PERFORMANCE.md            # Chasse au N+1 (jour 2)
├── requirements.txt
├── instance/                 # Base SQLite générée (non versionnée)
├── scripts/
│   └── seed.py               # Peuplement idempotent  [à écrire]
├── tests/
│   └── conftest.py           # Fixtures pytest        [à écrire]
└── app/
    ├── __init__.py           # App factory create_app()
    ├── common/
    │   ├── auth.py           # Middleware X-User-Id    [à écrire]
    │   ├── errors.py         # Handlers d'erreur JSON
    │   └── validation.py     # Glue Pydantic ↔ Flask
    ├── services/             # Logique métier          [vide, jours 2-4]
    ├── dal/
    │   ├── database.py       # Instance db = SQLAlchemy()
    │   ├── models/
    │   │   ├── timestamps.py # TimestampMixin (created_at / updated_at)
    │   │   ├── maison.py
    │   │   ├── professeur.py
    │   │   ├── cours.py
    │   │   ├── eleve.py
    │   │   └── utilisateur.py
    │   └── repositories/
    │       ├── maison_repository.py
    │       ├── professeur_repository.py
    │       ├── cours_repository.py
    │       └── eleve_repository.py
    └── api/
        ├── schemas/          # maison_schema.py, professeur_schema.py, ...
        ├── controllers/      # controller_maison.py, ...
        └── routes/           # maison_route.py, ... + __init__.py (registre)
```

---

## Racine du projet

### `config.py`

Centralise les réglages, **une classe par environnement**. `from_object()` ne lit que les
variables en MAJUSCULES.

| Classe | Contenu | Usage |
|---|---|---|
| `BaseConfig` | `SECRET_KEY`, `SQLALCHEMY_TRACK_MODIFICATIONS = False`, `PROMOTION_THRESHOLD = 10` | Parent commun |
| `DevConfig` | `SQLALCHEMY_DATABASE_URI = "sqlite:///academie.db"`, `SQLALCHEMY_ECHO = True` | Développement |
| `TestConfig` | `SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"`, `TESTING = True` | Tests (base isolée) |

L'URI est **volontairement absente** de `BaseConfig` : chaque environnement doit déclarer
explicitement sa base, pour qu'un oubli ne fasse jamais tourner les tests sur les données
de dev. `PROMOTION_THRESHOLD` est le seuil configurable du passage d'année (jour 4).
`SQLALCHEMY_ECHO` affiche le SQL généré — indispensable à la chasse au N+1 (jour 2).

### `run.py`

Point d'entrée. Ne construit rien : appelle la factory puis démarre le serveur de
développement.

```python
app = create_app()
if __name__ == "__main__":
    app.run(debug=True)
```

### `app/__init__.py` — la factory

**`create_app(config_class=DevConfig)`** → assemble une application Flask neuve et la renvoie :

1. `Flask(__name__)` — crée l'objet application.
2. `app.config.from_object(config_class)` — charge les réglages.
3. `db.init_app(app)` — branche SQLAlchemy sur *cette* application.
4. Enregistre chaque blueprint de `ALL_BLUEPRINTS`.
5. `register_error_handlers(app)` — réponses d'erreur JSON homogènes.

Le paramètre `config_class` est ce qui permet aux tests de monter la même application sur
une base jetable (`create_app(TestConfig)`).

---

## Couche `dal/` — accès aux données

### `dal/database.py`

Contient **uniquement** l'instance partagée :

```python
db = SQLAlchemy()
```

Isolé dans un fichier neutre qui ne dépend de rien, pour briser le cycle d'imports : les
modèles importent `db` d'ici, la factory les importe tous ensuite.

### `dal/models/__init__.py`

Registre des modèles. **Importer une classe ici est obligatoire** : sans cet import, Python
n'exécute jamais la classe, `db.create_all()` ne crée pas sa table, et SQLAlchemy ne peut
pas résoudre les références par chaîne (`Mapped["Eleve"]`).

### `dal/models/timestamps.py`

**`TimestampMixin`** — classe ordinaire (pas un `db.Model`) prêtant deux colonnes à tous
les modèles principaux :

| Colonne | Comportement |
|---|---|
| `created_at` | Posée une fois, à l'insertion (`default=lambda: datetime.now(timezone.utc)`) |
| `updated_at` | Posée à l'insertion **et recalculée à chaque `UPDATE`** (`onupdate=...`) |

Le `lambda:` est essentiel : sans lui, l'heure serait figée au démarrage du serveur au lieu
d'être calculée à l'insertion.

Tous les modèles s'écrivent donc `class X(TimestampMixin, db.Model)` — le mixin prête ses
colonnes, `db.Model` apporte le statut de table.

---

## Les modèles en détail

### `Maison` — une maison de l'Académie

Table `maisons`. Possède plusieurs élèves (1-N).

| Attribut | Type | Contraintes | Rôle |
|---|---|---|---|
| `id` | `int` | clé primaire | Identifiant |
| `nom` | `str(50)` | **unique** | Nom de la maison (Gryffondor…) |
| `couleur` | `str(50)` | — | Couleur emblématique |
| `reputation` | `int` | `default=0` | Score de réputation, **modifié par la clôture d'un tournoi** (jour 3) |
| `fondateur` | `str(50)` | — | Nom du fondateur |
| `valeurs` | `Text` | — | Valeurs de la maison (texte libre, sans limite) |
| `eleves` | relation | `list["Eleve"]` | Ses élèves (1-N, `back_populates="maison"`) |

`reputation` n'est **pas exposée en écriture** dans `MaisonCreate`/`MaisonUpdate` : elle ne
doit évoluer que via la logique métier des tournois, jamais par appel direct du client.

### `Professeur` — un enseignant

Table `professeurs`. Responsable de plusieurs cours (1-N), possède au plus un compte (1-1).

| Attribut | Type | Contraintes | Rôle |
|---|---|---|---|
| `id` | `int` | clé primaire | |
| `nom` | `str(50)` | — | |
| `prenom` | `str(50)` | — | |
| `matiere` | `str(50)` | — | Matière enseignée |
| `anciennete` | `int` | `default=0` | Années d'ancienneté (jamais négative, garanti par le schéma) |
| `cours` | relation | `list["Cours"]` | Ses cours (1-N) |
| `utilisateur` | relation | `"Utilisateur \| None"` | Son compte (1-1, optionnel) |

### `Cours` — un cours

Table `cours`. Appartient à un professeur (N-1).

| Attribut | Type | Contraintes | Rôle |
|---|---|---|---|
| `id` | `int` | clé primaire | |
| `intitule` | `str(50)` | — | Nom du cours |
| `niveau` | `str(50)` | — | Niveau requis |
| `capacite_max` | `int` | — | Nombre max d'inscrits — **fera respecter le refus d'inscription** (jour 2) |
| `professeur_id` | `int` | FK → `professeurs.id` | Professeur responsable |
| `annee_academique` | `str(9)` | **indexée** | Format `"YYYY-YYYY"`, imposé par le schéma |
| `professeur` | relation | `"Professeur"` | Son professeur (N-1) |

L'index sur `annee_academique` anticipe les filtrages fréquents par année (clôture d'année,
jour 4).

### `Eleve` — un élève

Table `eleves`. Appartient à une maison (N-1), possède au plus un compte (1-1).

| Attribut | Type | Contraintes | Rôle |
|---|---|---|---|
| `id` | `int` | clé primaire | |
| `nom` | `str(50)` | — | |
| `prenom` | `str(50)` | — | |
| `annee` | `int` | — | Année d'études (1 à 7) |
| `familier` | `str(50)` | — | Animal de compagnie |
| `statut` | `str(20)` | `default="inscrit"` | `inscrit` / `diplome` / `renvoye` |
| `maison_id` | `int` | FK → `maisons.id` | Maison d'appartenance |
| `maison` | relation | `"Maison"` | Sa maison (N-1) |
| `utilisateur` | relation | `"Utilisateur \| None"` | Son compte (1-1, optionnel) |

Le statut évoluera vers `diplome` lors du passage de fin d'année (jour 4). Les valeurs
autorisées sont garanties par un `Literal[...]` côté schéma.

### `Utilisateur` — un compte de connexion

Table `utilisateurs`. Lié à **au plus un** Élève **ou** un Professeur (1-1), ou à personne
(admin).

| Attribut | Type | Contraintes | Rôle |
|---|---|---|---|
| `id` | `int` | clé primaire | Valeur attendue dans le header `X-User-Id` |
| `email` | `str(120)` | **unique** | Identifiant de connexion, clé naturelle du seed |
| `mot_de_passe` | `str(255)` | — | ⚠️ **En clair, temporaire** (cf. cahier des charges) |
| `role` | `str(20)` | — | `eleve` / `professeur` / `admin` |
| `eleve_id` | `int \| None` | FK, **unique**, nullable | Rempli si `role="eleve"` |
| `professeur_id` | `int \| None` | FK, **unique**, nullable | Rempli si `role="professeur"` |
| `eleve` | relation | `"Eleve \| None"` | L'élève lié (1-1) |
| `professeur` | relation | `"Professeur \| None"` | Le professeur lié (1-1) |

Trois subtilités :

- **`unique=True` sur les deux FK** traduit le « lié à exactement un » : deux comptes ne
  peuvent pas viser le même élève. Comme SQL autorise **plusieurs `NULL`** dans une colonne
  unique, plusieurs admins coexistent sans problème.
- **La cohérence rôle ↔ lien** (`admin` ⇒ aucune FK, etc.) est une **contrainte applicative**,
  vérifiée dans le schéma Pydantic, pas en base.
- **Le 1-1 est déduit de l'annotation** : `Mapped["Utilisateur | None"]` est scalaire, donc
  `eleve.utilisateur` renvoie un objet, pas une liste. Aucun `uselist=False` nécessaire en
  style SQLAlchemy 2.0. (Contraste : `Maison.eleves` est `Mapped[list["Eleve"]]` → 1-N.)

`__repr__` n'expose **jamais** le mot de passe.

### Schéma relationnel

```
Maison  1 ──── N  Eleve  1 ──── 1  Utilisateur  1 ──── 1  Professeur  1 ──── N  Cours
                                    (role: eleve / professeur / admin)
```

---

## Les repositories

**Seule couche autorisée à exécuter des requêtes SQLAlchemy.** Sait chercher et écrire,
ne décide jamais. Aucun `abort()`, aucun code HTTP.

Les quatre repositories exposent la même interface, au nom de l'entité près :

| Fonction | Retour | Comportement |
|---|---|---|
| `lister_xxx()` | `list[Model]` | Tous les enregistrements |
| `get_by_id(id)` | `Model \| None` | `db.session.get()` renvoie `None` si absent — pas de plantage |
| `create_xxx(data)` | `Model` | Construit depuis un `dict`, `add` + `commit`, renvoie l'objet créé |
| `update_xxx(id, data)` | `Model \| None` | `None` si introuvable ; sinon met à jour champ par champ via `data.get(champ, valeur_actuelle)` puis `commit` |
| `delete_xxx(id)` | `bool` | `False` si introuvable, `True` si supprimé |

Le motif `data.get("champ", objet.champ)` réalise la **mise à jour partielle** : un champ
absent du dict conserve sa valeur actuelle. C'est ce qui fait fonctionner le `PATCH`.

Les valeurs `None` / `False` renvoyées sont **traduites en codes HTTP par le controller**,
jamais par le repository.

| Fichier | Entité |
|---|---|
| `maison_repository.py` | `lister_maisons`, `get_by_id`, `create_maison`, `update_maison`, `delete_maison` |
| `professeur_repository.py` | `lister_professeurs`, `get_by_id`, `create_professeur`, `update_professeur`, `delete_professeur` |
| `cours_repository.py` | `lister_cours`, `get_by_id`, `create_cours`, `update_cours`, `delete_cours` |
| `eleve_repository.py` | `lister_eleve`, `get_by_id`, `create_eleve`, `update_eleve`, `delete_eleve` |

---

## Couche `api/` — la couche web

## Les schémas Pydantic

Le **contrat** d'entrée/sortie. À ne pas confondre avec les modèles SQLAlchemy : le modèle
décrit une **table**, le schéma décrit une **donnée échangée**.

Chaque ressource a trois schémas :

| Schéma | `model_config` | Rôle |
|---|---|---|
| `XxxCreate` | `extra="forbid"` | Payload du `POST`. Tous les champs requis. Un champ inconnu → **400** |
| `XxxUpdate` | `extra="forbid"` | Payload du `PATCH`. **Tous les champs optionnels** (`default=None`) |
| `XxxOut` | `from_attributes=True` | Forme renvoyée. Lit directement les attributs de l'objet SQLAlchemy |

⚠️ Dans un schéma `Update`, `str | None` **ne suffit pas** à rendre un champ optionnel :
`| None` autorise la valeur `None`, mais c'est `Field(default=None)` qui rend le champ
facultatif. Sans lui, Pydantic l'exige à chaque PATCH.

### Contraintes déclarées par ressource

| Ressource | Contraintes notables |
|---|---|
| **Maison** | `nom`, `couleur`, `fondateur` : 1-50 car. ; `valeurs` : ≥ 1 car. `reputation` absente en écriture |
| **Professeur** | `anciennete` : `ge=0` (jamais négative) |
| **Cours** | `capacite_max` : `ge=1` ; `professeur_id` : `ge=1` ; `annee_academique` : `pattern=r"^\d{4}-\d{4}$"` |
| **Élève** | `annee` : `ge=1` ; `statut` : `Literal["inscrit", "diplome", "renvoye"]` ; `maison_id` : `ge=1` |

`Literal[...]` est une **annotation de type** (venue de `typing`), pas un argument de
`Field()` : il restreint l'ensemble des valeurs acceptées, là où `Field()` contraint une
valeur (bornes, longueur, regex).

---

## Les controllers

Orchestrent **un** endpoint HTTP : valident, délèguent, répondent. Aucune requête SQL.

Chaque controller expose cinq fonctions publiques et un ou deux helpers privés.

### Helpers privés (préfixés `_`)

**`_serialize(objet)`** — présent dans les quatre controllers.

```python
def _serialize(maison):
    return MaisonOut.model_validate(maison).model_dump(mode="json")
```

Convertit un objet SQLAlchemy en `dict` JSON-compatible. Extrait parce qu'il serait sinon
répété dans `lister`, `recuperer`, `creer` et `modifier`. `mode="json"` sérialise les
`datetime` en chaînes ISO.

**`_verifier_professeur(id)` / `_verifier_maison(id)`** — présents uniquement dans les
controllers dont la ressource porte une **clé étrangère** (Cours et Élève).

```python
def _verifier_maison(maison_id):
    """Interrompt la requête (400) si la maison référencée n'existe pas."""
    if maison_repo.get_by_id(maison_id) is None:
        abort(make_response(jsonify({"error": f"Maison {maison_id} introuvable"}), 400))
```

C'est une **garde**, pas un calcul : elle ne renvoie rien, elle laisse passer ou fait tout
exploser (`abort()` lève une exception qui interrompt aussi la fonction appelante). Sans
elle, un `POST /cours` avec `professeur_id: 999` créerait un **cours fantôme**, car SQLite
n'applique pas les clés étrangères par défaut dans ce projet — la vérification est donc
**applicative**.

Le **400** (et non 404) signifie « votre requête est mal formée : elle référence une entité
inexistante », alors que l'endpoint, lui, existe bien.

### Fonctions publiques

| Fonction | Méthode | Comportement | Codes |
|---|---|---|---|
| `lister()` | GET | Liste sérialisée (`[]` si vide) | 200 |
| `recuperer(id)` | GET | L'objet, ou `abort` si introuvable | 200 / 404 |
| `creer()` | POST | `validate_body` → gardes FK → `repo.create` | 201 / 400 / 409 |
| `modifier(id)` | PATCH | `validate_body` → `model_dump(exclude_unset=True)` → gardes FK conditionnelles → `repo.update` | 200 / 400 / 404 |
| `supprimer(id)` | DELETE | Garde d'intégrité éventuelle → `repo.delete` | 204 / 404 / 409 |

**`exclude_unset=True`** est la clé du PATCH : seuls les champs **réellement envoyés** par
le client se retrouvent dans le dict. C'est pourquoi `modifier()` teste
`if "professeur_id" in champs:` avant d'appeler la garde — sans ce test, un PATCH ne
touchant pas à la FK appellerait `_verifier_professeur(None)`.

Noter la différence de syntaxe entre les deux fonctions d'écriture, piège classique :
`creer()` lit `donnees.professeur_id` (objet Pydantic, avec un point), `modifier()` lit
`champs["professeur_id"]` (dict, avec des crochets).

### Gardes d'intégrité avant suppression

Deux controllers refusent de supprimer un parent encore référencé, en **409 Conflict** :

| Controller | Refuse si | Message |
|---|---|---|
| `controller_professeur.supprimer()` | le professeur a des cours | `"…responsable de N cours"` |
| `controller_maison.supprimer()` | la maison a des élèves | `"…compte N élèves"` |

L'ordre est déterminant : **récupérer → vérifier → `abort` si besoin → supprimer**. Appeler
`repo.delete()` avant la garde supprimerait la ligne avant même de pouvoir la protéger.

`controller_cours` et `controller_eleve` n'ont pas de garde : rien ne dépend d'eux
aujourd'hui.

---

## Les routes

Fichiers très fins : ils associent une URL à une fonction de controller, rien d'autre.

```python
maison_bp = Blueprint("maisons", __name__, url_prefix="/maisons")
maison_bp.add_url_rule("", view_func=controller.lister, methods=["GET"])
maison_bp.add_url_rule("/<int:maison_id>", view_func=controller.recuperer, methods=["GET"])
...
```

`<int:maison_id>` capture un segment d'URL, le convertit en entier et le passe en argument
à la fonction du controller. Un id non numérique ne matche aucune route → 404 automatique.

### `api/routes/__init__.py` — le registre

Expose le tuple **`ALL_BLUEPRINTS`**, parcouru par la factory. **Y ajouter un blueprint est
obligatoire** : un blueprint défini mais absent de ce tuple n'est jamais enregistré, et tous
ses endpoints répondent 404.

---

## Couche `common/` — briques transverses

### `common/validation.py`

**`validate_body(schema)`** — la glue entre Pydantic et Flask, écrite une fois, utilisée par
tous les endpoints d'écriture.

1. Lit `request.get_json(silent=True)`. Corps absent ou illisible → **400**
   (`"Corps JSON manquant ou invalide"`).
2. Tente `schema.model_validate(data)`.
3. En cas d'échec, traduit la `ValidationError` Python en réponse **400** listant
   précisément les champs fautifs :

```json
{
  "error": "Validation échouée",
  "details": [{"champ": "statut", "message": "Input should be 'inscrit', 'diplome' or 'renvoye'"}]
}
```

4. En cas de succès, renvoie l'objet Pydantic validé.

Une exception Python n'est pas une réponse HTTP : sans cette traduction, un payload invalide
provoquerait un 500. C'est le rôle exact de ce module.

### `common/errors.py`

**`register_error_handlers(app)`** — appelée par la factory, enregistre deux handlers :

| Handler | Déclenché par | Réponse |
|---|---|---|
| `handle_integrity_error` | `IntegrityError` SQLAlchemy | `rollback()` puis **409** `"Conflit : violation d'une contrainte d'unicité ou d'intégrité"` |
| `handle_http_exception` | toute `HTTPException` Werkzeug | JSON `{"error": description}` + le code d'origine |

Le premier attrape par exemple la création de deux maisons de même nom (`unique=True`). Le
`rollback()` est indispensable : sans lui, la session reste polluée.

Le second garantit que **même les erreurs générées par Flask** (404 sur une URL inconnue,
405 sur une méthode non prévue) sortent en JSON, jamais en page HTML.

### `common/auth.py` — *à écrire (jour 1)*

Doit fournir la brique lisant le header **`X-User-Id`** : identifier l'utilisateur courant,
distinguer espace élève / espace admin, et renvoyer une **erreur explicite (401)** si le
header manque sur un endpoint qui en a besoin — jamais un comportement silencieux.

Authentification volontairement **simulée** : rien n'empêche aujourd'hui d'usurper un id.
Elle permet de construire toute la logique d'**autorisation** (qui voit quoi) sans gérer
l'**authentification** (prouver qui on est).

---

## Couche `services/` — logique métier

**Actuellement vide.** Accueillera les décisions métier des jours 2 à 4, testables sans HTTP :

- refus d'inscription à un cours complet (jour 2) ;
- clôture d'un examen : mise à jour des statuts d'inscription + moyenne du cours (jour 2) ;
- déblocage **idempotent** des compétences après un examen (jour 3) ;
- clôture d'un tournoi : vainqueur + réputation de sa maison (jour 3) ;
- passage de fin d'année : promotion / redoublement / diplomation (jour 4).

Repère : « puis-je tester ça sans HTTP ? » → oui → c'est un service.

---

## Tests et scripts

### `scripts/seed.py` — *à écrire*

Peuplement **idempotent** (get-or-create, jamais create aveugle) : le relancer ne doit ni
dupliquer ni casser les données. Volume attendu : ≥ 4 maisons, ~30 élèves sur 7 années,
quelques professeurs et cours, un utilisateur par élève/professeur, un admin. Monte à ≥ 150
élèves au jour 4.

### `tests/conftest.py` — *à écrire*

Fixtures pytest : application montée via `create_app(TestConfig)` (base en mémoire, isolée),
schéma créé, client de test, session propre par test.

---

## Référence des endpoints

| Méthode | URL | Description | Codes |
|---|---|---|---|
| GET | `/maisons` | Liste des maisons | 200 |
| GET | `/maisons/<id>` | Une maison | 200, 404 |
| POST | `/maisons` | Créer | 201, 400, 409 |
| PATCH | `/maisons/<id>` | Modifier partiellement | 200, 400, 404 |
| DELETE | `/maisons/<id>` | Supprimer | 204, 404, **409** si elle a des élèves |
| GET | `/professeurs` | Liste des professeurs | 200 |
| GET | `/professeurs/<id>` | Un professeur | 200, 404 |
| POST | `/professeurs` | Créer | 201, 400 |
| PATCH | `/professeurs/<id>` | Modifier partiellement | 200, 400, 404 |
| DELETE | `/professeurs/<id>` | Supprimer | 204, 404, **409** s'il a des cours |
| GET | `/cours` | Liste des cours | 200 |
| GET | `/cours/<id>` | Un cours | 200, 404 |
| POST | `/cours` | Créer | 201, **400** si `professeur_id` inexistant |
| PATCH | `/cours/<id>` | Modifier partiellement | 200, 400, 404 |
| DELETE | `/cours/<id>` | Supprimer | 204, 404 |
| GET | `/eleves` | Liste des élèves | 200 |
| GET | `/eleves/<id>` | Un élève | 200, 404 |
| POST | `/eleves` | Créer | 201, **400** si `maison_id` inexistant |
| PATCH | `/eleves/<id>` | Modifier partiellement | 200, 400, 404 |
| DELETE | `/eleves/<id>` | Supprimer | 204, 404 |
| GET | `/utilisateurs` | Liste des utilisateurs | 200 |
| GET | `/utilisateurs/<id>` | Un utilisateur | 200, 404 |
| POST | `/utilisateurs` | Créer | 201, 400, **409** si l'email est déjà pris |
| PATCH | `/utilisateurs/<id>` | Modifier `email` / `mot_de_passe` | 200, 400, 404, 409 |
| DELETE | `/utilisateurs/<id>` | Supprimer | 204, 404 |

> Le préfixe `/cours` reste invariable (singulier = pluriel en français).

---

## Conventions du projet

### Codes HTTP

| Code | Signification dans ce projet |
|---|---|
| **200** | Lecture ou modification réussie |
| **201** | Création réussie (l'objet créé est renvoyé) |
| **204** | Suppression réussie (corps vide) |
| **400** | Payload invalide, **ou** référence vers une entité inexistante |
| **404** | La ressource ciblée par l'URL n'existe pas |
| **405** | Méthode non prévue sur cette URL (JSON, via le handler) |
| **409** | Conflit : doublon (`unique`) ou suppression d'un parent référencé |

Distinction importante entre 400 et 404 : un `PATCH /cours/5` avec `professeur_id: 999`
renvoie **400** (le professeur référencé n'existe pas) ; un `PATCH /cours/999` renvoie
**404** (le cours à modifier n'existe pas). Deux entités, deux erreurs.

### Nommage

- Classes de modèle : **singulier** (`Maison`), tables : **pluriel minuscule** (`maisons`).
- Fichiers modèles : singulier (`maison.py`) ; repositories : `xxx_repository.py` ;
  controllers : `controller_xxx.py` ; routes : `xxx_route.py`.
- Fonctions publiques des controllers en français (`lister`, `recuperer`, `creer`,
  `modifier`, `supprimer`) ; helpers privés préfixés `_`.

### Piège récurrent : le copier-coller entre verticales

Chaque nouvelle ressource est écrite en dupliquant la précédente. **Systématiquement**,
relire ligne par ligne : nom du champ FK, nom du repository importé, nom de l'entité dans
les messages d'erreur, type des champs. Erreurs déjà rencontrées sur ce projet : `maison`
au lieu de `maison_id`, `familier: int` au lieu de `str`, `_verifier_professeur` dans le
controller Élève, `self.nom` dans le `__repr__` d'`Utilisateur`.

---

## État d'avancement

| Élément | Statut |
|---|---|
| Architecture en couches, factory, config | ✅ |
| Handlers d'erreur JSON | ✅ |
| Glue de validation Pydantic | ✅ |
| Timestamps `created_at` / `updated_at` | ✅ *(exigence jour 4, faite en avance)* |
| Validation stricte des payloads | ✅ *(exigence jour 4, faite en avance)* |
| Verticale **Maison** (modèle → routes) | ✅ |
| Verticale **Professeur** | ✅ |
| Verticale **Cours** | ✅ |
| Verticale **Élève** | ✅ |
| Modèle **Utilisateur** | ✅ |
| Repository / schéma / controller / routes Utilisateur | ⬜ |
| `POST /login` | ⬜ |
| Middleware `X-User-Id` (`common/auth.py`) | ⬜ |
| Script de seed idempotent | ⬜ |
| Tests (`conftest.py` + scénarios) | ⬜ |
| Jours 2, 3, 4 | ⬜ |

### Bizarreries connues, non bloquantes

- **`EleveUpdate.statut`** a `default="inscrit"` au lieu de `default=None`. Inoffensif tant
  que le controller utilise `exclude_unset=True` (le champ non envoyé n'apparaît pas dans le
  dict), mais incohérent avec les autres champs optionnels.
- **Message d'erreur non accordé** : `"cette maison compte 1 élèves"`.
- **Fuseaux horaires** : les `datetime` sont stockés en UTC, mais SQLite perd l'information
  de fuseau ; l'API renvoie donc des dates sans suffixe `Z`.
