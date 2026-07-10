# Explications

Ce fichier regroupe les concepts expliqués au fil du projet.

## Table des matières

1. [Pourquoi la relation N-N cours ↔ élèves est-elle « enrichie » ?](#sec1)
2. [L'architecture en couches : config, models, api, database, controllers](#sec2)
3. [Créer et utiliser l'environnement virtuel (venv, Windows / PowerShell)](#sec3)
4. [Le header `X-User-Id` : c'est quoi, à quoi ça sert, comment ça marche](#sec4)
5. [`database.py` : instance vs sous-classe, et où va `init_app`](#sec5)
6. [POO : classe vs instance (pourquoi `db.Model` n'existe que sur une instance)](#sec6)
7. [Le pattern « app factory » expliqué sans jargon](#sec7)
8. [Écrire une classe en Python (cas simple : les classes de config)](#sec8)
9. [Faut-il créer le fichier SQLite à la main ? Non](#sec9)
10. [À quoi sert `SECRET_KEY`](#sec10)
11. [Pourquoi `BaseConfig` n'a pas d'URI de base de données](#sec11)
12. [La factory `create_app` (app/__init__.py), étape par étape](#sec12)
13. [Erreur classique : `'function' object has no attribute 'run'`](#sec13)
14. [Que fait `app.run()` ?](#sec14)
15. [`app.run()` vs `flask run` : deux façons de démarrer le serveur](#sec15)
16. [`dal` vs `repositories` : même couche, ou deux niveaux ?](#sec16)
17. [Rôle de chaque dossier de la structure (où mettre quoi ?)](#sec17)
18. [`validation.py` vs `schemas/` : à quoi sert la glue de validation ?](#sec18)
19. [Le mixin d'horodatage (`base.py`) : created_at vs updated_at](#sec19)
20. [Qu'est-ce que `db.Model` ? (et `Base` abstraite vs mixin)](#sec20)
21. [SQLAlchemy pur vs Flask-SQLAlchemy (engine, Base, create_all)](#sec21)
22. [SQLAlchemy pur vs Flask-SQLAlchemy : les différences en détail](#sec22)
23. [Écrire un modèle SQLAlchemy : le gabarit `Maison`](#sec23)
24. [Pourquoi l'autocomplete manque (interpréteur + `db.` dynamique)](#sec24)
25. [Singulier ou pluriel ? (classe vs table vs fichier)](#sec25)
26. [Rendre les modèles visibles pour `create_all` (+ app_context)](#sec26)
27. [`ModuleNotFoundError: No module named 'app'` (lancer le bon fichier)](#sec27)
28. [Le dossier `instance/` : où atterrit la base SQLite](#sec28)
29. [Style `Column` vs `Mapped` / `mapped_column` (SQLAlchemy 2.0)](#sec29)
30. [`create_all()` ne modifie pas les tables existantes (≠ migration)](#sec30)
31. [`init-db` : une commande CLI Flask pour (re)créer la base](#sec31)
32. [Lancer un script depuis un sous-dossier (`python -m`)](#sec32)
33. [Anatomie d'une requête : `select` / `execute` / `scalars` / `all`](#sec33)
34. [Créer un objet : `add` vs `commit` (le caddie)](#sec34)
35. [Repository : `update` et `delete` (update partiel, cas introuvable)](#sec35)
36. [Héritage (IS-A) vs association (HAS-A) : Utilisateur ↔ Élève/Prof](#sec36)
37. [Modéliser l'ancienneté : valeur dérivée vs fait fixe (âge vs date de naissance)](#sec37)
38. [Où mettre les `default` ? (modèle vs schéma vs repository)](#sec38)
39. [Enregistrer plusieurs blueprints : le registre `routes/__init__.py`](#sec39)
40. [Les index en base de données (à quoi ça sert, ce que ça coûte)](#sec40)
41. [Les relations SQLAlchemy : `ForeignKey` + `relationship()`](#sec41)
42. [Les deux `relationship()` décortiqués morceau par morceau](#sec42)
43. [Intégrité référentielle : le cours fantôme (`professeur_id: 999`)](#sec43)
44. [Refuser la suppression d'un parent qui a des enfants (409 explicite)](#sec44)
45. [Qu'est-ce qu'une fonction « helper » ?](#sec45)
46. [Vérifier une FK dans le controller, morceau par morceau](#sec46)
47. [`Literal[]` de Pydantic : annotation de type, pas argument de `Field()`](#sec47)

---

<a id="sec1"></a>
## Pourquoi la relation N-N cours ↔ élèves est-elle « enrichie » ?

### Lien simple vs association enrichie

Une relation N-N **pure** ne fait que *relier* deux entités (ex. un article et ses
tags). La table intermédiaire ne contient que deux clés étrangères et rien d'autre.
SQLAlchemy peut la gérer de façon quasi invisible (paramètre `secondary`), sans en
faire une classe.

Une relation N-N **enrichie** porte des **attributs propres au lien lui-même**, qui
n'appartiennent ni à l'une ni à l'autre des deux entités reliées.

### Le cas de l'Inscription

Le cahier des charges définit Inscription avec : **date d'inscription** et **statut**
(inscrit / en cours / validé / abandonné).

À qui appartiennent ces attributs ?

- **Pas à l'Élève** : un même élève peut être « validé » en Potions et « abandonné »
  en Métamorphose. Le statut n'est pas une propriété de l'élève.
- **Pas au Cours** : le cours n'a pas un statut unique ; chaque élève inscrit a le sien.
- **Au couple (élève, cours)**, c'est-à-dire au **lien** entre les deux.

C'est la définition d'une association enrichie : le fait « l'élève X est inscrit au
cours Y » porte lui-même des données. La table intermédiaire devient une **entité
métier à part entière**, avec sa propre identité et ses propres colonnes.

### Conséquence concrète

Inscription (comme Résultat et Maîtrise) doit être un **modèle SQLAlchemy à part
entière**, pas un simple `secondary`. On manipule des objets `Inscription`, on les
liste, on change leur `statut` (c'est le sens de « clôturer un examen » au jour 2).

**Repère mental** : dès que le lien a besoin d'une date, d'un statut, d'une note ou
d'un score → c'est une association enrichie → c'est une entité.

---

<a id="sec2"></a>
## L'architecture en couches : config, models, api, database, controllers

### À quoi sert `config.py`

Fichier qui **centralise tous les réglages** de l'application au lieu de les mettre en
dur dans le code. Il contient des **classes de configuration**, une par environnement :

- `DevConfig` : base SQLite sur fichier, `SQLALCHEMY_ECHO = True` (affiche le SQL,
  indispensable pour la chasse au N+1 du jour 2).
- `TestConfig` : base **séparée** (souvent SQLite en mémoire), `TESTING = True`.
  Garantit que `pytest` ne touche jamais les données de dev.

Chaque classe déclare le chemin de la base (`SQLALCHEMY_DATABASE_URI`), une
`SECRET_KEY`, les seuils configurables, et lit les **variables d'environnement**.

**Lien avec l'app factory** : `create_app` reçoit *quelle* config utiliser. En dev elle
prend `DevConfig` ; dans `conftest.py`, les tests l'appellent avec `TestConfig`. C'est
tout l'intérêt du pattern factory : la même app montée avec des réglages différents.

### `models/` vs `api/` : deux couches, deux responsabilités

Ils peuvent porter le même nom de domaine (`eleve.py`) mais n'ont rien à voir :

| | `models/eleve.py` | `api/eleves.py` |
|---|---|---|
| **Question** | « Qu'est-ce qu'un élève ? » | « Que peut-on faire avec les élèves ? » |
| **Contenu** | Classe SQLAlchemy `Eleve` : colonnes, relations, contraintes | Routes du blueprint : `GET/POST/PUT/DELETE /eleves` |
| **Connaît** | La structure des données, la base | Le HTTP : requêtes, codes de statut, JSON |
| **Ignore** | Le HTTP, les routes | La structure interne de la table, le SQL |

`models/` = la **forme** des données (devient une table). `api/` = les **actions**
exposées (deviennent des URLs). L'un est le *quoi*, l'autre le *comment on y accède*.

### Où mettre `database.py`

C'est le fichier qui contient **l'instance SQLAlchemy partagée** (`db = SQLAlchemy()`),
sans app. Le placer dans `app/database.py`.

**Pourquoi un fichier dédié, pas dans la factory ?** Pour éviter les **imports
circulaires** : les `models/` ont besoin de `db`, la factory a besoin des `models/`.
Si `db` vivait dans la factory, les models importeraient la factory qui importe les
models → cycle → Python plante. En isolant `db` dans un fichier neutre qui ne dépend de
rien, tout le monde peut l'importer. La factory le relie ensuite à l'app via
`db.init_app(app)`.

### Où mettre les « controllers »

En MVC, un **controller** = le code qui reçoit une requête et décide quoi renvoyer.
Dans Flask, ce rôle est tenu par les **blueprints** et leurs fonctions de vue.

> **Les controllers = les fichiers de `api/`.** Un fichier par domaine = un blueprint =
> un controller. (`api/eleves.py`, `api/examens.py`...)

Un controller reste **fin** : il valide (via `schemas/`), délègue (à `services/` ou
`dal/`), met en forme la réponse. Ni requête SQL ni règle métier dedans.

---

<a id="sec3"></a>
## Créer et utiliser l'environnement virtuel (venv, Windows / PowerShell)

Un **venv** est un dossier isolé qui contient sa propre copie de Python et ses paquets,
pour ne pas polluer le Python global et rendre le projet reproductible.

1. **Créer** (à la racine du projet) :
   ```powershell
   python -m venv .venv
   ```
   `.venv` est la convention (déjà dans `.gitignore`). Si `python` échoue : `py -m venv .venv`.

2. **Activer** :
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   Le prompt se préfixe de `(.venv)`. Si PowerShell bloque (execution policy) :
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
   ```
   (`-Scope Process` = uniquement ce terminal, rien de permanent), puis réactiver.

3. **Installer les dépendances** :
   ```powershell
   pip install -r requirements.txt
   ```

4. **Vérifier** : `pip list` (doit montrer Flask, Flask-SQLAlchemy, pydantic, pytest).

5. **Sortir** : `deactivate`.

**À retenir** :
- Réactiver le venv à chaque nouveau terminal (l'activation ne persiste pas).
- `.venv/` ne se commite jamais ; ce qui se partage, c'est `requirements.txt`.
- Après ajout d'un paquet, figer les versions : `pip freeze > requirements.txt`.

---

<a id="sec4"></a>
## Le header `X-User-Id` : c'est quoi, à quoi ça sert, comment ça marche

### Un header HTTP, c'est quoi

Une requête HTTP a deux parties : le **corps** (les données JSON envoyées) et les
**headers** (en-têtes), des paires `clé: valeur` qui portent des **métadonnées** sur la
requête, pas les données elles-mêmes (ex. `Content-Type: application/json`).
`X-User-Id` est un header parmi d'autres, mais inventé pour ce projet.

### Le préfixe `X-`

Signalait historiquement un header **non standard / personnalisé**, propre à une
application. Convention aujourd'hui dépréciée mais toujours très répandue et lisible.
`X-User-Id` = « en-tête maison qui transporte l'identifiant de l'utilisateur ».

### À quoi ça sert

L'API doit savoir **qui** fait la requête pour se comporter différemment : un élève ne
voit que SES données (cours, notes, dossier), un admin voit et pilote tout. Le
`X-User-Id` transporte l'identité de l'appelant à chaque requête.

### Comment ça marche, étape par étape

1. `POST /login` (email + mot de passe) → renvoie utilisateur, rôle, eleve_id/professeur_id.
2. Le client mémorise cet id.
3. À chaque requête sur un endpoint protégé, le client ajoute `X-User-Id: 42`.
4. Côté serveur, une brique transverse (`app/common/auth.py`) :
   - lit le header ;
   - s'il est **absent** sur un endpoint qui en a besoin → **401/400 explicite**, pas de silence ;
   - sinon retrouve l'Utilisateur correspondant et l'expose comme « utilisateur courant ».
5. Le controller/service applique la règle : admin → accès complet ; élève → filtré sur ses données.

D'où le fichier `auth.py` dans `common/` : logique écrite une fois (décorateur ou hook
`before_request`), réutilisée sur toutes les routes protégées.

### Point crucial : auth *simulée*, pas *sécurisée*

N'importe qui peut écrire `X-User-Id: 1` et se faire passer pour l'utilisateur 1 : aucune
preuve d'identité, le serveur *fait comme si* c'était vérifié (note « sécurité hors scope,
mais pas absente » du cahier).

Dans une vraie API, on enverrait un **jeton signé** (session, JWT, OAuth) dans le header
`Authorization`, infalsifiable, et l'id serait **extrait** du jeton, pas envoyé en clair.
Ici on saute cette étape volontairement : `X-User-Id` permet de construire et tester toute
la logique d'**autorisation** (qui voit quoi) sans gérer l'**authentification** (prouver
qui on est). Le jour où on sécurise, on remplace juste la brique qui *fournit* l'id.

**En une phrase** : `X-User-Id` est un en-tête HTTP personnalisé qui transporte
l'identifiant de l'appelant, lu à chaque requête pour distinguer espace élève / admin —
un raccourci d'authentification simulée (donc falsifiable) qui laisse construire la vraie
logique d'autorisation.

---

<a id="sec5"></a>
## `database.py` : instance vs sous-classe, et où va `init_app`

### On veut une *instance*, pas une *sous-classe*

Le fichier `database.py` doit contenir :

```python
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
```

Piège rencontré : écrire `class db(SQLAlchemy): pass` crée une **nouvelle classe** qui
hérite de `SQLAlchemy` — un *plan*, pas un objet utilisable.

- `class db(SQLAlchemy)` = « je définis un nouveau *type* » → pas d'objet.
- `db = SQLAlchemy()` = « je *fabrique* un objet à partir du plan » → l'objet dont on a besoin.

Les parenthèses `()` après `SQLAlchemy` = « je l'appelle pour en fabriquer un exemplaire ».
C'est ce qui manquait. Concrètement, le code fera plus tard `db.Model`, `db.Column(...)`,
`db.init_app(app)` : ces attributs/méthodes n'existent que sur une **instance**, pas sur
une classe qui hérite sans être instanciée. Avec la sous-classe, `db.init_app(app)`
planterait.

### Où va `db.init_app(app)` : dans la factory, PAS dans run.py

| Fichier | Rôle | Contient `init_app` ? |
|---|---|---|
| `app/__init__.py` (`create_app`) | **Construit** l'app : config + `db.init_app(app)` + blueprints | ✅ oui |
| `run.py` | **Lance** une app déjà construite : `app = create_app()` puis `app.run()` | ❌ non |

Pourquoi : le branchement `db ↔ app` doit se faire **dans la factory**, car c'est elle qui
reçoit *quelle* config utiliser. Quand les tests appelleront `create_app(TestConfig)`, ils
veulent que `db.init_app` s'exécute sur *leur* app de test, automatiquement à chaque
construction. Dans `run.py`, l'app de test (qui ne passe jamais par `run.py`) n'aurait
jamais son `db` branché.

**Règle mentale** : `run.py` ne fait que *démarrer* ; toute la *construction* (dont
`init_app`) vit dans la factory.

---

<a id="sec6"></a>
## POO : classe vs instance (pourquoi `db.Model` n'existe que sur une instance)

### Classe = plan, instance = objet construit

- Une **classe** est un **plan de construction** (`SQLAlchemy` est un plan).
- Une **instance** est un **objet réellement bâti** à partir du plan (`SQLAlchemy()`
  construit un objet).

Analogie : le **plan d'architecte** (classe) vs la **maison bâtie** (instance). On ne peut
pas ouvrir un robinet sur un plan papier ; seulement dans une maison construite, où la
plomberie a été posée pendant la construction.

### Les parenthèses `()` déclenchent la construction

`SQLAlchemy()` exécute la méthode `__init__` (le constructeur). C'est **pendant** cette
construction que l'objet se remplit de ses attributs/outils (`.Model`, `.Column`, etc.).

```python
class Maison:
    def __init__(self):
        self.robinet = "installé"   # créé PENDANT la construction

m = Maison()
print(m.robinet)       # ✅ "installé" — construction faite
print(Maison.robinet)  # ❌ AttributeError — la classe brute n'a jamais construit robinet
```

`self.robinet` n'existe que parce que `__init__` s'est exécuté, et `__init__` ne s'exécute
que quand on appelle `Maison()`.

### Lien avec database.py

`db.Model`, `db.Column`, `db.init_app` sont comme `m.robinet` : Flask-SQLAlchemy les pose
dans le `__init__` de `SQLAlchemy`, donc au moment de `SQLAlchemy()`.

- `db = SQLAlchemy()` → construction → `__init__` s'exécute → `db.Model`, `db.init_app` existent. ✅
- `class db(SQLAlchemy): pass` → juste un **nouveau plan** dérivé, aucun objet construit →
  `__init__` ne s'exécute jamais → `db.Model` absent, `db.init_app(app)` planterait. ❌

Hériter (`class db(SQLAlchemy)`) donne un **deuxième plan**, pas une **maison habitable**.

### Précision sur les méthodes (`init_app`)

`init_app` est une **méthode d'instance** : elle travaille sur **un objet précis** (le
`self`). `db.init_app(app)` = « branche l'app sur cet objet `db` construit ». Sur une
classe jamais instanciée, il n'y a aucun objet à brancher — le `self` manque.

**À retenir** : les parenthèses transforment un plan en objet, et c'est l'objet (pas le
plan) qui possède les outils.

---

<a id="sec7"></a>
## Le pattern « app factory » expliqué sans jargon

### L'image : la recette plutôt que le plat déjà cuisiné

**Façon 1 — le plat déjà cuisiné, posé sur le comptoir.** Préparé une fois pour toutes ;
tout le monde mange ce plat précis ; il n'en existe qu'un, cuisiné d'une seule manière,
préparé dès qu'on entre dans la cuisine (même si personne n'a faim).

**Façon 2 — la recette écrite sur une fiche.** Rien de cuisiné d'avance : une **recette**
(« pour préparer le repas, fais ceci puis cela »). Tant que personne ne la suit, rien
n'est cuisiné. Quand quelqu'un a faim, il suit la recette et obtient un repas frais — et
il peut l'ajuster (« la même chose, sans sel, pour la cuisine d'essai »).

Le **factory = Façon 2** appliquée à l'application : au lieu de la construire tout de
suite, on écrit une **recette de construction** — une fonction `create_app` qui, quand on
l'appelle, assemble une application toute fraîche.

### Pourquoi c'est mieux — trois raisons concrètes

1. **La cuisine d'essai (tests)** : les tests ont besoin de leur propre application
   branchée sur une base jetable, pour ne pas abîmer les vraies données. Avec une recette,
   ils demandent « la version d'essai » (`TestConfig`) ; avec un plat unique, ils
   devraient manger le même que tout le monde.
2. **Le bon moment pour construire** : le plat déjà cuisiné est préparé trop tôt (dès
   l'entrée en cuisine), ce qui force un ordre rigide et crée le nœud « A a besoin de B qui
   a besoin de A » (imports circulaires). La recette dit « on construira plus tard, quand
   on me le demandera » — ce délai dénoue le problème.
3. **Une seule source de vérité** : un seul endroit sait assembler l'app (la recette). On
   en fabrique autant qu'on veut (vraie, test, démo), toutes cohérentes, sans copier-coller.

### Ce que fait la recette `create_app`, en clair

1. **Prendre les réglages** qu'on lui tend (vraie config ou config de test) → `config.py`.
2. **Brancher la plomberie** : relier la base à cette application précise → `db.init_app(app)`.
3. **Poser les portes d'entrée** : rattacher les zones de l'API → les blueprints de `routes/`.

Puis elle **rend l'application terminée**. `run.py` ne cuisine rien : il suit la recette
puis sert le plat (`app = create_app()` puis démarre).

### Le mot

« Factory » = « **usine** » : une machine à qui on demande « fabrique-moi une application »
et qui en sort une neuve à chaque appel, réglée selon ce qu'on précise. **On ne pose pas
l'application toute faite, on écrit le moyen d'en fabriquer une quand on veut.**

Déclic : **recette, pas plat déjà servi.**

---

<a id="sec8"></a>
## Écrire une classe en Python (cas simple : les classes de config)

Une classe de config est le type de classe le plus simple : pas de `__init__`, pas de
`self`, pas de méthode. **Juste une boîte étiquetée qui contient des variables.**

### Forme minimale

```python
class MaBoite:
    COULEUR = "bleu"
    TAILLE = 10
```

- `class` = mot-clé « je crée une boîte ».
- `MaBoite` = son nom (convention : première lettre majuscule).
- `:` = deux-points obligatoires en fin de ligne.
- Les lignes **indentées** (4 espaces) = le contenu, une variable par ligne (`NOM = valeur`).
  C'est l'indentation qui dit « ces variables appartiennent à la boîte ».

Lecture : « `MaBoite` contient `COULEUR = "bleu"` et `TAILLE = 10` ».

### L'héritage : partir d'une boîte existante

```python
class BoiteDeBase:
    COULEUR = "bleu"
    TAILLE = 10

class BoiteDev(BoiteDeBase):
    TAILLE = 99
```

Le `(BoiteDeBase)` = « `BoiteDev` **commence avec tout le contenu** de `BoiteDeBase` ».
- `BoiteDev` a `COULEUR = "bleu"` automatiquement (héritée, jamais réécrite).
- `BoiteDev` redéfinit `TAILLE = 99` → sa valeur **remplace** l'héritée.
- Résultat : `BoiteDev` = { COULEUR: "bleu", TAILLE: 99 }.

### Appliqué à config.py

```python
import os

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "valeur-de-secours")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROMOTION_THRESHOLD = 10          # seuil (nombre) du passage d'année

class DevConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///academie.db"
    SQLALCHEMY_ECHO = True

class TestConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
```

- `BaseConfig` n'a **pas** de parenthèses (boîte d'origine) ; `DevConfig(BaseConfig)` et
  `TestConfig(BaseConfig)` en ont → elles héritent de la base.
- Grâce à l'héritage, `DevConfig` et `TestConfig` possèdent aussi `SECRET_KEY`,
  `SQLALCHEMY_TRACK_MODIFICATIONS` et `PROMOTION_THRESHOLD`, sans les réécrire.
- Ces classes ne « se lancent » pas : ce sont des sacs de réglages, appliqués plus tard
  par la factory.

---

<a id="sec9"></a>
## Faut-il créer le fichier SQLite à la main ? Non

`SQLALCHEMY_DATABASE_URI = "sqlite:///academie.db"` ne crée pas le fichier : c'est une
**adresse** (« la base sera là »), pas un ordre de création. Le fichier `academie.db`
apparaît **automatiquement** à la première connexion — SQLite fabrique le fichier s'il
n'existe pas encore.

### Distinction essentielle : le fichier ≠ les tables

| | Quoi | Quand ça se crée |
|---|---|---|
| Le **fichier** `academie.db` | Le contenant vide | Automatiquement, 1ʳᵉ connexion |
| Les **tables** (Eleve, Maison…) | La structure | Via `db.create_all()`, **après** avoir écrit les modèles |

- Fichier : automatique, rien à faire.
- Tables : n'apparaissent pas seules → il faut explicitement `db.create_all()`, une fois
  les modèles écrits. Sans modèles, `create_all()` ne crée qu'un fichier vide.

### Ordre correct

1. `config.py` (adresse) → 2. factory + `db` (branchement) → 3. modèles (tables décrites)
→ 4. `db.create_all()` (le fichier `academie.db` se crée avec ses tables).

Créer le fichier à la main maintenant = un `.db` vide inutile, que SQLAlchemy referait de
toute façon.

### Nuance : `init_app` configure mais ne connecte pas

`db.init_app(app)` **prépare** le branchement (il enregistre l'adresse) mais **n'ouvre pas
la connexion**. SQLite ne crée le fichier qu'à la **première vraie connexion**. Donc une
app qui démarre avec `init_app` mais sans aucune requête ni `create_all()` **ne crée aucun
fichier** — c'est normal. Le fichier apparaît au premier `db.create_all()` (qui, lui, doit
tourner dans un app context et après import des modèles).

---

<a id="sec10"></a>
## À quoi sert `SECRET_KEY`

### Un sceau anti-falsification

Flask envoie parfois une petite donnée au **navigateur** du client (ex. un cookie de
session « cet utilisateur est connecté »), puis la récupère plus tard. Entre-temps la
donnée est chez le client, qui pourrait la modifier. Alors avant de l'envoyer, Flask y
appose un **sceau** calculé à partir du `SECRET_KEY`. Au retour, il recalcule le sceau
avec la même clé :
- sceaux identiques → donnée intacte, acceptée ;
- donnée bricolée → sceaux différents → rejetée.

**Analogie** : un cachet de cire portant ton empreinte. Si on falsifie la lettre, le
cachet est brisé. Le `SECRET_KEY` est ton empreinte : seul le serveur la connaît, donc
personne ne peut forger un faux cachet valide.

### Pourquoi c'est un secret

Toute la protection repose sur le fait que **seul le serveur connaît la clé**. Si elle
fuit, n'importe qui peut forger des sceaux valides. Donc :
- jamais en dur dans le code commité ;
- lue depuis une **variable d'environnement** → `os.getenv("SECRET_KEY", ...)`. La valeur
  de secours ne sert qu'en développement.

### Dans ce projet

L'authentification est **simulée** via `X-User-Id` → on n'utilise pas les sessions/cookies
signés de Flask, donc `SECRET_KEY` est peu sollicité. On le garde quand même :
1. bonne habitude standard de toute app Flask ;
2. filet de sécurité : Flask plante sans clé dès qu'on utilise flash/sessions/CSRF ;
3. cohérent avec « sécurité hors scope, mais pas absente ».

Chez nous : un **placeholder de bonne pratique**, inoffensif, à laisser tel quel.

---

<a id="sec11"></a>
## Pourquoi `BaseConfig` n'a pas d'URI de base de données

L'URI est **le réglage qui doit différer** selon l'environnement :
- dev → un vrai fichier persistant (`sqlite:///academie.db`) ;
- test → une base jetable en mémoire (`sqlite:///:memory:`).

C'est la raison d'être même de configs séparées. Si l'URI était dans `BaseConfig` :
- `DevConfig` et `TestConfig` **hériteraient de la même base** ;
- les tests tourneraient sur `academie.db` (les vraies données de dev), les polluant →
  l'isolation recherchée serait détruite.

On met donc l'URI **hors** de `BaseConfig`, dans chaque variante, pour **forcer** chaque
environnement à déclarer explicitement sa base.

**Bonus sécurité** : pas de valeur par défaut = pas d'oubli silencieux possible. Si une
URI « par défaut » vivait dans `BaseConfig` et qu'on oubliait de la redéfinir dans
`TestConfig`, les tests tourneraient sans erreur sur la base de dev — le pire des bugs.

### Règle mentale réutilisable

- Dans `BaseConfig` : ce qui est **identique** partout (`SECRET_KEY`,
  `PROMOTION_THRESHOLD`, `SQLALCHEMY_TRACK_MODIFICATIONS`).
- Laissé dehors + redéfini par variante : ce qui **doit** différer
  (`SQLALCHEMY_DATABASE_URI`, `SQLALCHEMY_ECHO`, `TESTING`).

### Au passage : `config.py` n'importe que `os`

`config.py` ne fait que déclarer des réglages (chaînes et nombres). Il ne touche jamais la
base → pas besoin de `from flask_sqlalchemy import SQLAlchemy` (import inutile à retirer).
Seul `import os` est nécessaire, pour `os.getenv`.

---

<a id="sec12"></a>
## La factory `create_app` (app/__init__.py), étape par étape

Ce fichier ne construit pas l'app tout de suite : il **définit une fonction** (la recette)
qui montera une app fraîche quand on l'appellera. Structure = quelques imports + une seule
fonction.

```python
from flask import Flask
from app.database import db
from config import DevConfig

def create_app(config_class=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    # TODO: db.create_all() + enregistrement des blueprints (plus tard)
    return app
```

Ligne par ligne :

1. **Imports** : `Flask` (l'outil qui fabrique l'app), `db` (l'objet base créé dans
   `database.py`, encore débranché), `DevConfig` (réglages par défaut).
2. **`def create_app(config_class=DevConfig):`** : la recette. `config_class=DevConfig` est
   une **valeur par défaut** → `create_app()` sans argument prend Dev ; les tests appellent
   `create_app(TestConfig)`. Tout le corps doit être **indenté** (dans la fonction).
3. **`app = Flask(__name__)`** : construit l'objet application (parenthèses = objet réel).
   `__name__` = variable spéciale remplie par Python avec le nom du module, qui aide Flask
   à savoir où il se trouve. Formule standard, toujours `Flask(__name__)`.
4. **`app.config.from_object(config_class)`** : recopie les réglages de la classe dans
   l'app. `from_object` ne lit **que les variables en MAJUSCULES** → c'est pour ça que les
   réglages de `config.py` sont en majuscules.
5. **`db.init_app(app)`** : branche la base sur *cette* app précise. Doit venir **après**
   le chargement de la config (étape 4), car `db` a besoin de connaître l'adresse de la base.
6. **`return app`** : rend l'app terminée (en dernier, indenté). Sans `return`, la fonction
   fabriquerait une app puis la jetterait.

À ajouter plus tard, entre l'étape 5 et le `return` : `db.create_all()` (une fois les
modèles écrits) et l'enregistrement des blueprints (une fois les routes écrites).

### run.py : suivre la recette et démarrer

```python
from app import create_app
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
```

- `from app import create_app` : Python lit `app/__init__.py` quand on importe `app`.
- `app = create_app()` : appelle la recette (parenthèses !) → une vraie app.
- `if __name__ == "__main__":` : « n'exécute ceci que si on lance CE fichier directement
  (`python run.py`), pas s'il est importé ailleurs ».
- `app.run(debug=True)` : lance le serveur de dev ; `debug=True` = erreurs détaillées.

Lancer `python run.py` doit afficher « Running on http://127.0.0.1:5000 » : la config, la
factory et la base sont correctement branchées, même sans aucune page.

---

<a id="sec13"></a>
## Erreur classique : `'function' object has no attribute 'run'`

Cause : avoir écrit `app = create_app` (sans parenthèses) au lieu de
`app = create_app()`. Sans `()`, on range **la fonction elle-même** dans `app`, pas le
résultat de son appel. Puis `app.run(...)` demande de démarrer… une fonction, qui n'a pas
de `.run` → `AttributeError: 'function' object has no attribute 'run'`.

Le message se lit : « l'objet est une **fonction**, pas une app ».

Correctif : `app = create_app()` (avec parenthèses = « suis la recette » → vraie app).

### Le fil rouge des parenthèses

| Sans `()` | Avec `()` |
|---|---|
| `SQLAlchemy` = le plan | `SQLAlchemy()` = l'objet construit |
| `create_app` = la recette | `create_app()` = l'app fabriquée |

**Les parenthèses = le geste « exécute / construis ». Sans elles, on tient l'outil, pas
son résultat.**

Réflexe : **lire le message d'erreur en entier** — il indique souvent directement la nature
du problème (ici, « function » au lieu d'une app).

---

<a id="sec14"></a>
## Que fait `app.run()` ?

`app.run()` ne fait pas que « lancer un script » : il **démarre un serveur web** et le
laisse allumé, en attente. Trois choses :

1. **Il ouvre une porte** pour recevoir des requêtes → message
   « Running on http://127.0.0.1:5000 » :
   - `127.0.0.1` = *localhost*, « cette machine-ci » (personne d'autre sur le réseau) ;
   - `5000` = le **port**, le numéro de porte sur lequel l'app écoute.
2. **Il attend en boucle des visiteurs.** À chaque requête reçue, le serveur cherche la
   **route** correspondante, exécute son code, renvoie la réponse, puis reprend l'attente.
   (Analogie : ouvrir la boutique et poster un réceptionniste à l'entrée.)
3. **Il bloque le programme** : le terminal reste figé sur « Running on… » car le serveur
   *tourne*. On l'arrête avec **Ctrl + C**.

### `debug=True`

- **Rechargement automatique** : sauvegarder un `.py` redémarre le serveur tout seul.
- **Pages d'erreur détaillées** : en cas de plantage pendant une requête, on voit où et
  pourquoi.

### Bon à savoir

Ce serveur est le **serveur de développement** de Flask : parfait pour coder/tester, mais
pas pour la production (on utiliserait gunicorn/waitress). Pour ce projet, le serveur de
dev suffit.

### État actuel

La boutique est ouverte mais vide (aucune route). Visiter `http://127.0.0.1:5000/`
renverrait un **404** — normal, et cela prouve même que le serveur répond. Prochaine
étape : lui donner des routes à servir.

---

<a id="sec15"></a>
## `app.run()` vs `flask run` : deux façons de démarrer le serveur

Le serveur de dev est le même ; la différence est **qui appelle `.run()`**.

**Chemin A — on le lance soi-même** (ce qu'on fait ici) :
```python
app.run(debug=True)   # dans run.py
```
puis `python run.py`. C'est notre code qui appelle `.run()`.

**Chemin B — la commande `flask run`** :
```powershell
flask run
```
On **n'écrit jamais `app.run()`** : l'outil `flask` trouve l'app et appelle `.run()` à
notre place. C'est souvent ce chemin qu'on utilise sans le savoir dans d'autres projets.

### Comment `flask run` trouve l'app tout seul

Par convention : la variable d'environnement `FLASK_APP`, ou un fichier standard
(`app.py`, `wsgi.py`), ou **une factory nommée `create_app` dans un package `app/`** —
c'est exactement notre structure. Donc `flask run` marcherait ici même **sans** `run.py`.

### Lequel choisir

Les deux sont valables. Pour ce projet on garde `run.py` + `app.run()` : explicite, point
d'entrée visible, aucune variable d'environnement à gérer. Mais `flask run` ferait le même
travail en repérant `create_app` automatiquement — ce n'était pas de la magie, juste une
convention.

---

<a id="sec16"></a>
## `dal` vs `repositories` : même couche, ou deux niveaux ?

`DAL` (Data Access Layer) est le **concept** (la couche qui isole l'accès aux données) ;
`repository` est le **patron concret** le plus courant pour l'implémenter. Donc un dossier
`repositories/` **est** une façon de matérialiser un DAL.

### Pourquoi certains projets ont les DEUX en même temps

Deux raisons possibles :

**Raison 1 (la plus courante) — imbrication de dossiers.** `dal/` est un dossier
« parapluie » qui regroupe tout l'accès aux données, et `repositories/` est un
**sous-dossier** à l'intérieur :

```
dal/
├── database.py
├── models/
└── repositories/
```

Ici `dal/` n'est pas une couche technique différente : c'est juste une **organisation**
(tout le « data » au même endroit). C'est le cas rencontré dans les projets précédents.

**Raison 2 (plus rare) — accès aux données à deux niveaux.** Là, chacun joue un rôle
distinct :

| Couche | Nom fréquent | Rôle | Exemple |
|---|---|---|---|
| Basse | `dao/` | Mécanique, une par table, CRUD brut | `get_by_id`, `insert`, `update` |
| Haute | `repositories/` | Métier, exprime l'intention, combine plusieurs DAO | `trouver_eleves_actifs_d_une_maison` |

Analogie (niveau 2) : le **DAO** = le magasinier (« va chercher la boîte 42 ») ; le
**repository** = le vendeur qui comprend la demande client et l'envoie chercher les bonnes
boîtes.

### Pour ce projet (4 jours, solo) : une seule couche

La séparation à deux niveaux est utile sur un gros projet, mais ici c'est de la
**sur-ingénierie**. On garde **un seul** dossier `repositories/`, un repository par entité
qui fait directement ses requêtes SQLAlchemy sur les modèles. La logique métier lourde
(passage d'année…) va de toute façon dans `services/`, qui joue déjà un peu le rôle du
« repository haut niveau ». Donc pas besoin des deux dossiers.

---

<a id="sec17"></a>
## Rôle de chaque dossier de la structure (où mettre quoi ?)

Structure retenue : « données » regroupées sous `dal/`, « web » sous `api/`.

### Le trajet d'une requête

```
Requête HTTP
   ▼
api/routes ──▶ api/controllers ──▶ services ──▶ dal/repositories ──▶ dal/models ──▶ SQLite
   (URL)         (orchestration)     (métier)      (requêtes SQL)       (tables)
                      └── api/schemas (valide l'entrée / met en forme la sortie)

common/ = briques transverses (auth, validation, erreurs)
```

### `dal/` — accès aux données (parapluie)

- **`dal/database.py`** : l'instance `db = SQLAlchemy()`. Rien d'autre (aucune table, aucune requête).
- **`dal/models/`** : *ce que sont* les données → une classe SQLAlchemy par entité (colonnes,
  relations, contraintes) + `base.py` (horodatage). Pas de requête, pas de HTTP, pas de métier.
- **`dal/repositories/`** : la **seule** couche qui exécute des requêtes SQLAlchemy. Un
  repository par entité (`get`, `list`, `create`, `update`, `delete`, requêtes anti-N+1).
  Sait chercher/écrire, pas décider.

### `api/` — couche web (parapluie)

- **`api/routes/`** : associe une URL à une fonction de controller (blueprints). Très fin,
  aucune logique.
- **`api/controllers/`** : orchestre **un** endpoint HTTP (lit la requête, valide via
  `schemas/`, appelle un service ou un repository, met en forme la réponse + code HTTP).
  Pas de SQL direct, pas de métier complexe.
- **`api/schemas/`** : le **contrat** d'entrée/sortie (schémas Pydantic : création, update,
  sortie ; rejet d'un payload invalide avec message par champ). ⚠️ à ne pas confondre avec
  `dal/models/` : model = table (persistance), schema = validation/forme échangée.

### `services/` — logique métier

Les **décisions** et opérations complexes, indépendantes du HTTP, **testables seules** :
clôture d'examen, déblocage idempotent des compétences, clôture de tournoi, passage
d'année. Pas de `request` ni de codes HTTP ; délègue les requêtes aux repositories.
Repère : « je veux tester ça sans HTTP ? » → oui → service.

### `common/` — briques transverses

Partagé par toutes les couches : `auth.py` (middleware `X-User-Id`), `validation.py` (glue
Pydantic → 400 champ fautif), `errors.py` (réponses d'erreur JSON cohérentes). Rien de
spécifique à un seul domaine.

### Racine

- `app/__init__.py` : la factory `create_app`.
- `config.py` : réglages par environnement.
- `run.py` : point d'entrée.
- `seed.py` : peuplement idempotent.
- `tests/` : pytest (`conftest.py` + un scénario métier par jour).

### Règle d'or (dans l'ordre)

1. Ça parle **HTTP** (URL, requête, code) ? → `api/`
2. Ça prend une **décision métier** ? → `services/`
3. Ça **lit/écrit en base** ? → `dal/` (models = structure, repositories = requêtes)

Si une fonction fait les trois → la **découper** en trois, une par couche. But : chaque
bout de code a **une seule raison de changer**.

---

<a id="sec18"></a>
## `validation.py` vs `schemas/` : à quoi sert la glue de validation ?

Les deux ne font pas le même travail :

- **`schemas/` = les règles** (le *quoi*). Un schéma Pydantic *décrit* une donnée valide
  (champs, types, bornes). C'est une description, une loi. Il n'agit pas seul.
- **`validation.py` = le mécanisme qui applique ces règles dans Flask** (le *comment*).

### Le problème résolu

1. Une requête arrive avec du JSON.
2. On tente de construire le schéma Pydantic à partir de ce JSON.
3. Si les données sont mauvaises, **Pydantic lève une exception Python** (`ValidationError`).

Or une exception Python **n'est pas** une réponse HTTP : sans traitement, le serveur
renverrait un 500 moche. Il faut donc **attraper** l'exception et la **traduire** en `400`
avec le champ fautif. Cette traduction est **identique pour tous les endpoints** → on
l'écrit une fois dans `validation.py` au lieu de la copier-coller partout.

### Analogie

Le **schéma** = la liste des règles d'entrée affichée à la porte d'un club. `validation.py`
= le **videur** qui confronte chaque arrivant aux règles et délivre un motif de refus clair.
Le videur *utilise* les règles mais c'est un rôle séparé : les règles sans videur ne
filtrent personne, le videur sans règles ne sait pas quoi vérifier.

### Concrètement

Un décorateur, écrit une fois, posé sur les controllers :

```
@validate_body(EleveCreateSchema)
def creer_eleve(...):
    ...
```

Il : (1) lit `request.json`, (2) tente `EleveCreateSchema(**data)`, (3) si échec → `400` +
champ fautif (le controller n'est même pas appelé), (4) si succès → transmet l'objet validé.
Le controller reçoit des données déjà propres, sans `try/except` répété.

**En une phrase** : `schemas/` déclare les règles ; `validation.py` les applique
uniformément et traduit les erreurs Pydantic en `400` — écrit une fois, réutilisé partout.

---

<a id="sec19"></a>
## Le mixin d'horodatage (`base.py`) : created_at vs updated_at

Choix retenu : **pattern mixin** (classe ordinaire), pour que le nom colle au concept et
éviter toute confusion avec la declarative base `db.Model`.

### Le fichier `dal/models/base.py`

```python
from datetime import datetime, timezone
from app.dal.database import db


class TimestampMixin:                      # classe ordinaire — PAS de (db.Model), PAS de __abstract__
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
```

Les modèles s'écrivent alors avec un **double héritage** :
`class Maison(TimestampMixin, db.Model):` — le mixin *prête* ses colonnes, `db.Model`
*apporte* le statut de table. Pas de `__abstract__` (le mixin n'est pas un `db.Model`).

À éviter : `class Mixin(db.Model): __abstract__ = True` = nom « Mixin » sur un pattern
« Base abstraite », contradictoire. Choisir franchement : nom `Mixin` → pattern mixin
(classe simple).

- `db.Column(...)` déclare une colonne ; `db.DateTime` en est le type.
- `default=lambda: ...` : valeur **à la création** de la ligne. Le `lambda:` fait calculer
  l'heure *au moment de l'insertion* (sans lui, l'heure serait figée au démarrage du programme).
- `onupdate=...` (sur `updated_at` seulement) : valeur **recalculée à chaque modification**.
- Différence clé : `created_at` = posé une fois à la naissance ; `updated_at` = rafraîchi à
  chaque `UPDATE`.
- `datetime.now(timezone.utc)` (UTC) plutôt que `datetime.utcnow()` déprécié.

Voir la section suivante pour `db.Model` et le rôle de `__abstract__`.

---

<a id="sec20"></a>
## Qu'est-ce que `db.Model` ? (et `Base` abstraite vs mixin)

### `db.Model`

`db` est l'instance SQLAlchemy (de `database.py`) ; `db.Model` est un outil qu'elle
fournit (comme `db.Column`). Rôle :

- Une classe Python **normale** ne connaît rien aux bases de données.
- **Hériter de `db.Model`** transforme la classe en classe **reliée à une table** (l'ORM
  l'adopte) : chaque **instance** = une **ligne**, chaque `db.Column` = une **colonne**, et
  SQLAlchemy sait la sauvegarder/charger/interroger.

Analogie : `db.Model` est un **contrat d'adoption**. Sans lui, `class Maison` n'est qu'un
objet Python banal sans lien avec SQLite ; avec lui, c'est une **table** gérée par l'ORM.

### Deux façons de partager les colonnes d'horodatage

**Mixin** : classe ordinaire (pas `db.Model`), mélangée à côté →
`class Maison(TimestampMixin, db.Model)`. Pas besoin de `__abstract__` car le mixin n'est
pas un `db.Model`, donc SQLAlchemy ne cherche jamais à lui créer une table.

**Base abstraite** (retenue ici) : `class Base(db.Model)` + `__abstract__ = True`, puis
`class Maison(Base)` (héritage simple, plus lisible). `Base` transmet colonnes **et**
machinerie de table.

### Pourquoi `__abstract__ = True` sur `Base` mais pas sur le mixin

Parce que `Base` **hérite de `db.Model`**. Sans `__abstract__`, SQLAlchemy essaierait de
créer une table pour `Base` elle-même (indésirable, ce n'est qu'un parent commun).
`__abstract__ = True` dit : « parent abstrait — pas de table pour `Base`, mais les enfants
héritent de ses colonnes ». Le mixin, lui, n'étant pas un `db.Model`, n'a jamais ce
problème.

---

<a id="sec21"></a>
## SQLAlchemy pur vs Flask-SQLAlchemy (engine, Base, create_all)

Deux façons d'utiliser SQLAlchemy — même travail, mais l'une montre ce que l'autre cache.

**SQLAlchemy pur** (assemblage manuel) : on crée soi-même un `engine` (`create_engine`),
un `Base = declarative_base()` (racine dont tous les modèles héritent), et on appelle
`Base.metadata.create_all(bind=engine)`.

**Flask-SQLAlchemy** (ici) : l'objet `db = SQLAlchemy()` emballe les trois : l'engine est
créé par Flask au `db.init_app(app)`, `db.Model` joue le rôle de `declarative_base()`, et
`db.metadata` est le catalogue.

### Correspondance

| SQLAlchemy pur | Flask-SQLAlchemy |
|---|---|
| `Base = declarative_base()` | `db.Model` |
| `create_engine(...)` | géré par `db.init_app(app)` |
| `Base.metadata.create_all(bind=engine)` | `db.create_all()` |
| `Base.metadata.drop_all(bind=engine)` | `db.drop_all()` |

Un `init_db(delete=False)` habituel devient :

```python
def init_db(delete=False):
    if delete:
        db.drop_all()
    db.create_all()
```

### Le `bind=engine` devient le contexte d'app

On ne passe plus `bind=engine` : Flask-SQLAlchemy gère plusieurs apps (dev/test) avec des
bases différentes, donc il faut lui dire *laquelle* utiliser via le **contexte
d'application** :

```python
with app.app_context():
    db.create_all()
```

Le `with app.app_context():` remplace le `bind=engine`.

### Piège de nommage : deux `Base`

- Ancien projet : `Base` = la **racine déclarative** → ici c'est **`db.Model`**.
- Ce projet : la classe `Base` écrite dans `base.py` est juste un **intermédiaire abstrait**
  d'horodatage qui hérite de `db.Model` — ce n'est **pas** la racine déclarative.

### Deux conditions pour que `create_all` fonctionne

1. Tourner dans un `with app.app_context():`.
2. Les **modèles doivent être importés** avant l'appel : `db.create_all()` ne crée que les
   tables dont la classe a été exécutée par Python. Sinon `db.metadata` est vide.

---

<a id="sec22"></a>
## SQLAlchemy pur vs Flask-SQLAlchemy : les différences en détail

### Ce que chacun est

- **SQLAlchemy** = la bibliothèque complète (moteur, ORM, sessions). Fonctionne partout,
  sans Flask.
- **Flask-SQLAlchemy** = une fine extension qui **emballe** SQLAlchemy pour l'intégrer à
  Flask. Elle n'invente rien côté requêtes : sous le capot, **c'est SQLAlchemy**. Elle
  ajoute la colle (config + cycle de vie Flask) et des raccourcis.

Analogie : SQLAlchemy pur = moteur + pièces à monter soi-même ; Flask-SQLAlchemy = le même
moteur déjà installé et câblé dans la voiture (Flask).

### Différences concrètes

| Aspect | SQLAlchemy pur | Flask-SQLAlchemy |
|---|---|---|
| Moteur (engine) | `create_engine(url)` à la main | créé depuis `SQLALCHEMY_DATABASE_URI` au `db.init_app(app)` |
| Classe racine | `Base = declarative_base()` | `db.Model` |
| Session | `sessionmaker(bind=engine)`, gérée à la main | `db.session`, prête et gérée automatiquement |
| Cycle de vie | ouverture/fermeture par requête à ta charge | Flask ouvre/nettoie la session à chaque requête |
| Configuration | dans le code | lue depuis `app.config` |
| Requête | `session.execute(select(...))` | identique (`db.session.execute(select(...))`) |

### La différence la plus sensible : la session

Une **session** = la zone de travail temporaire avec la base (on y `add`/modifie, puis
`commit` pour écrire ; rien n'est écrit avant le commit).

- Pur : tu gères tout son cycle de vie (créer, partager, fermer par requête). Boilerplate
  délicat ; une session mal fermée = fuites de connexions.
- Flask-SQLAlchemy : `db.session` est branchée sur le cycle de vie de Flask → session
  propre par requête, **nettoyée automatiquement** en fin de requête. On écrit juste
  `db.session.add(...)` / `db.session.commit()`.

C'est la raison principale d'utiliser Flask-SQLAlchemy dans une app web.

### Ce qui NE change PAS

Le cœur ORM est identique : déclaration des modèles (`db.Column`, types, relations), clés
étrangères, relations 1-N / N-N, langage de requête (`select`, filtres, jointures), `add`,
`commit`, `rollback`. Seule la plomberie (engine, base, session, config) est prise en
charge par l'extension. D'où la traduction quasi identique de `init_db`.

### Compromis

- **Flask-SQLAlchemy** : moins de boilerplate, intégration Flask, factory/tests faciles ;
  mais couplé à Flask.
- **SQLAlchemy pur** : plus de contrôle, indépendant de tout framework ; mais tout à câbler.

Pour ce projet (API Flask), Flask-SQLAlchemy est imposé et idéal.

---

<a id="sec23"></a>
## Écrire un modèle SQLAlchemy : le gabarit `Maison`

```python
"""Modèle Maison — une maison de l'Académie (possède plusieurs élèves, 1-N)."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.dal.database import db
from app.dal.models.timestamps import TimestampMixin


class Maison(TimestampMixin, db.Model):
    __tablename__ = "maisons"         # minuscules, pluriel (convention projet)

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(50), unique=True)
    couleur: Mapped[str | None] = mapped_column(String(50))
    fondateur: Mapped[str | None] = mapped_column(String(50))
    valeurs: Mapped[str | None] = mapped_column(String(255))
    reputation: Mapped[int] = mapped_column(default=0)

    def __repr__(self):
        return f"<Maison {self.id} {self.nom}>"
```

Style **`Mapped` / `mapped_column`** (SQLAlchemy 2.0) — voir sections 24 et 29.
`db.Model` reste la base.

### Ligne par ligne

- **imports** : `Mapped, mapped_column` depuis `sqlalchemy.orm` ; `String` depuis
  `sqlalchemy` (pour la longueur) ; `db` (pour `db.Model`) ; `TimestampMixin`.
- **`class Maison(TimestampMixin, db.Model)`** : double héritage — le mixin prête
  `created_at`/`updated_at`, `db.Model` fait la table. Mixin en premier, `db.Model` en dernier.
- **`__tablename__ = "maisons"`** : minuscules, pluriel (convention projet), identique sur
  toutes les tables.
- **`id: Mapped[int] = mapped_column(primary_key=True)`** : `int`→`Integer` déduit ;
  identifiant unique auto-incrémenté (jamais fourni à la main).
- **`Mapped[str]`** = NOT NULL (obligatoire) ; **`Mapped[str | None]`** = nullable
  (facultatif) → `couleur`/`fondateur`/`valeurs` sont facultatifs, `nom` obligatoire.
- **`String(50)`** dans `mapped_column` : fixe la longueur max (le type `str` seul ne peut
  pas la deviner).
- **`unique=True`** : pas de doublon.
- **`default=0`** (sur `reputation`) : valeur si non fournie à la création.
- **`__repr__`** : affichage lisible en debug (`<Maison 1 Gryffondor>`). Optionnel.

### Gabarit réutilisable pour les autres entités

```
1. docstring
2. imports (db + TimestampMixin)
3. class XXX(TimestampMixin, db.Model):
4.     __tablename__ = "xxx"
5.     id = clé primaire
6.     ... colonnes propres ...
7.     def __repr__(self): ...
```

Ne changent d'un modèle à l'autre : le nom, `__tablename__`, la liste des colonnes (et plus
tard les **relations** entre tables).

---

<a id="sec24"></a>
## Pourquoi l'autocomplete manque (interpréteur + `db.` dynamique)

Deux causes possibles.

### Cause 1 — le bon interpréteur n'est pas sélectionné

Si VS Code ne pointe pas vers le **venv**, Pylance ne voit pas les paquets installés → aucun
autocomplete (même sur `datetime`, `Flask`…). Fix : `Ctrl+Shift+P` → « Python: Select
Interpreter » → choisir `.venv\Scripts\python.exe`. Vérifier aussi les extensions Python +
Pylance. Test : l'autocomplete apparaît-il sur `datetime.` ? Si non → c'est l'interpréteur.

### Cause 2 — `db.` complète mal (normal)

`db.Column`, `db.Integer`, `db.Model` ne sont pas écrits en dur : `db` se les fabrique **à
l'exécution** (dans son `__init__`). Pylance analyse **sans exécuter** (analyse statique),
donc il ne « voit » pas toujours ces attributs dynamiques → autocomplete pauvre sur `db.`.
Limite connue, pas une erreur.

### Solution : importer depuis `sqlalchemy`

`db.Column` **est** `sqlalchemy.Column`, `db.Integer` **est** `sqlalchemy.Integer`… mêmes
objets. On peut les importer directement → Pylance les voit :

```python
from sqlalchemy import Column, Integer, String
from app.dal.database import db

class Maison(TimestampMixin, db.Model):     # db.Model reste la base
    id = Column(Integer, primary_key=True)
    nom = Column(String(80), unique=True, nullable=False)
```

| Style | Autocomplete | Imports |
|---|---|---|
| `db.Column`, `db.Integer` | pauvre (dynamique) | aucun |
| `Column`, `Integer` importés | complet | quelques lignes en plus |

Résultat en base **identique** ; pur confort d'écriture. (Style « SQLAlchemy 2.0 » avec
`Mapped[int]` / `mapped_column(...)` : encore mieux typé, mais syntaxe supplémentaire.)

---

<a id="sec25"></a>
## Singulier ou pluriel ? (classe vs table vs fichier)

### La classe est au singulier

Une classe décrit **UN objet** ; l'instancier crée **une** chose :

```python
maison = Maison()      # ✅ « maison est une Maison »
maison = Maisons()     # ❌ « maison est une Maisons » (faux)
```

Une instance est toujours une unité → son type (la classe) est au singulier. Idem pour les
relations : `eleve.maison` (un élève → une maison) se lit bien ; `Maisons` sèmerait le
doute. Convention quasi universelle ; `class Maisons` fait tiquer un relecteur.

### Piège : « la classe représente la table » → NON, elle représente une ligne

La classe **ne représente pas la table** (le contenant de plusieurs lignes) : elle
représente **UNE ligne / une entité**. Trois concepts distincts :

| Concept | Quoi | Nombre |
|---|---|---|
| Classe `Maison` | le moule d'**une** maison | une → singulier |
| Table `"maisons"` | le contenant de **toutes** | plusieurs → pluriel |
| Instance `Maison(...)` | **une** maison (une ligne) | une |

Le pluriel « contient des maisons » est déjà porté par le nom de **table**. Preuve par
l'usage : `Maison(...)` crée UNE maison, `db.session.get(Maison, 1)` en renvoie UNE, et
`Maison.query.all()` renvoie une **liste** d'objets `Maison`, chacun étant UNE maison. On
n'a jamais un objet `Maison` = « toutes les maisons ».

Analogie : la classe = l'**emporte-pièce** (façonne une unité) ; la table = le **bocal**
qui contient toutes les unités découpées.

### La table peut être au pluriel

Une table contient **plusieurs lignes** → `maisons` (pluriel) est défendable (défaut de
Rails, par ex.). Singulier marche aussi. Choix libre, **indépendant** du nom de classe.

### Règle : cohérence par catégorie, pas entre catégories

| Élément | Convention | Exemple |
|---|---|---|
| Classe | singulier (une instance = une chose) | `class Maison` |
| Fichier | suit la classe → singulier | `maison.py` |
| Table | choix libre, mais identique sur **toutes** les tables | `"maisons"` (ou `"maison"`) |

`class Maison` (singulier) mappée sur `"maisons"` (pluriel) n'est **pas** une incohérence :
c'est le cas normal. « Pareil partout » = toutes les classes au singulier, toutes les tables
dans le même style.

**Choix du projet** : classes au **singulier**, tables au **pluriel** (minuscules).

---

<a id="sec26"></a>
## Rendre les modèles visibles pour `create_all` (+ app_context)

`db.create_all()` ne crée que les tables **enregistrées** dans `db.metadata`, c'est-à-dire
celles dont la classe a été **exécutée par Python** (donc importée). Deux étapes.

### Étape 1 — `dal/models/__init__.py` = le registre des modèles

```python
from app.dal.models.maison import Maison
# (une ligne par nouveau modèle)
```

Endroit unique qui « connaît » tous les modèles. Importer ce package chargera tous les
modèles d'un coup.

### Étape 2 — Import + `create_all` dans la factory

```python
    db.init_app(app)                 # 1. brancher db

    from app.dal import models       # noqa: F401  -> 2. enregistrer les modèles

    with app.app_context():          # 3. créer les tables
        db.create_all()
```

- `from app.dal import models` : exécute `models/__init__.py` → importe `Maison` → le corps
  de la classe s'exécute → SQLAlchemy enregistre la table dans `db.metadata`. Sans cet
  import, le catalogue est vide et `create_all` ne crée rien.
- `# noqa: F401` : dit au linter que l'import « inutilisé » est **voulu** (on l'importe pour
  son **effet de bord** — l'enregistrement — pas pour utiliser le nom).
- `with app.app_context()` : remplaçant du `bind=engine` — indique à Flask-SQLAlchemy quelle
  app/base utiliser.
- `db.create_all()` : crée les tables → `academie.db` naît avec ses tables.

Ordre : après `db.init_app(app)`, avant `return app`.

---

<a id="sec27"></a>
## `ModuleNotFoundError: No module named 'app'` (lancer le bon fichier)

L'erreur ne vient pas du code mais de **la façon de lancer**. Quand on lance
`python monfichier.py`, Python ajoute à sa recherche **le dossier de ce fichier**, et
cherche les imports à partir de là.

**Cause typique** : avoir lancé `app/__init__.py` directement (bouton ▶ de VS Code sur le
fichier ouvert). Python part alors du dossier `app/` → depuis l'intérieur de `app/`, le
package `app` n'est pas visible (il faudrait être à la racine, au-dessus) →
`No module named 'app'`. (Comme chercher le dossier « app » en étant déjà dedans.)

**Fix** : lancer le point d'entrée `run.py`, qui est à la **racine** du projet (à côté de
`app/`). Python part de la racine → voit `app/` → les `from app...` marchent.

```powershell
python run.py     # depuis la racine, PAS python app/__init__.py
```

**Piège VS Code** : le bouton ▶ lance le **fichier actif**. Toujours lancer `run.py` (via
le terminal, ou en ouvrant `run.py` avant de cliquer ▶).

---

<a id="sec28"></a>
## Le dossier `instance/` : où atterrit la base SQLite

Flask a une notion d'**instance folder** : un dossier pour les fichiers propres à une
installation locale, non versionnés (base SQLite, secrets, config locale). Par défaut
`<projet>/instance/`.

Depuis **Flask-SQLAlchemy 3.x**, un chemin SQLite **relatif** (`sqlite:///academie.db`) est
résolu **par rapport à `instance/`** → `instance/academie.db`. (Changement vs 2.x qui
utilisait le dossier courant.)

C'est voulu et sain : la base de dev est séparée du code source, dans un dossier prévu pour
ça. `*.db` étant déjà dans `.gitignore`, `instance/academie.db` n'est pas versionné.

Rien à changer. Pour forcer un autre emplacement : utiliser un chemin **absolu** dans l'URI.

### Gitignore : ignorer tout le dossier `instance/`

Mieux que `*.db` seul : ajouter `instance/` au `.gitignore`. Le dossier peut accueillir non
seulement la base mais aussi une config locale ou des secrets (non couverts par `*.db`).
Ignorer le dossier entier exprime l'intention « local à ma machine, jamais versionné »
(convention Flask). Garder `*.db` en plus = double sécurité.

---

<a id="sec29"></a>
## Style `Column` vs `Mapped` / `mapped_column` (SQLAlchemy 2.0)

Deux façons de déclarer les colonnes.

**Style `Column` (legacy, supporté)**
```python
from sqlalchemy import Column, Integer, String
id = Column(Integer, primary_key=True)
nom = Column(String(50), unique=True, nullable=False)
couleur = Column(String(50))
```

**Style `Mapped` (recommandé 2.0+)**
```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
id: Mapped[int] = mapped_column(primary_key=True)
nom: Mapped[str] = mapped_column(String(50), unique=True)
couleur: Mapped[str | None] = mapped_column(String(50))
```

### Ce que `Mapped` apporte

1. **Types réels → autocomplete sur les instances** : `maison.nom` est connu comme `str`
   (`maison.nom.upper()` autocomplété), `maison.reputation` comme `int`. Va plus loin que
   l'autocomplete sur les colonnes : partout où on utilise un objet.
2. **Nullabilité déduite du type** : `Mapped[str]` = NOT NULL ; `Mapped[str | None]` =
   nullable. Plus de `nullable=False` à répéter.
3. **Type SQL déduit** : `Mapped[int]` → colonne entière (plus besoin d'`Integer`). On ne
   précise `String(50)` que pour fixer une longueur.

| | `Column` | `Mapped` |
|---|---|---|
| Autocomplete colonnes | ✅ | ✅ |
| Autocomplete instances (`maison.nom`) | ❌ | ✅ |
| Nullabilité | `nullable=False` | déduite (`str` vs `str \| None`) |
| Type SQL | explicite (`Integer`) | déduit de `Mapped[int]` |
| Statut | legacy (supporté) | recommandé 2.0+ |

Coût : 2 notions (`Mapped[...]`, `mapped_column(...)`) + import `sqlalchemy.orm`.

**Choix du projet** : style `Mapped` (meilleur autocomplete, standard moderne).

### Détail : comment le type Python déduit le type SQL

SQLAlchemy 2.0 garde une table de correspondance Python → SQL. En lisant `Mapped[X]`, il y
cherche `X` et choisit le type de colonne :

| `Mapped[...]` | SQL |
|---|---|
| `int` | `Integer` |
| `str` | `String` |
| `bool` | `Boolean` |
| `float` | `Float` |
| `datetime` | `DateTime` |
| `date` | `Date` |
| `Decimal` | `Numeric` |

Donc `id: Mapped[int]` → `Integer` automatiquement (plus besoin de l'écrire).

**Quand préciser un type dans `mapped_column` :**
1. Fixer une longueur/param que le type Python ne peut pas deviner : `Mapped[str] =
   mapped_column(String(50))` (SQLite ignore la longueur, MySQL l'exige, PostgreSQL la
   valide → portabilité).
2. Forcer un type différent du défaut : `description: Mapped[str] = mapped_column(Text)`.

**Raccourci annotation seule** : sans option ni type paramétré, l'annotation suffit —
`description: Mapped[str]` (pas de `= mapped_column(...)`). On ajoute `mapped_column(...)`
seulement pour les options (`primary_key`, `unique`, `default`, `index`) ou un type
paramétré (`String(50)`, `Numeric`, `Text`).

Règle : **le type Python donne le type SQL par défaut ; `mapped_column` ne sert qu'aux
options et aux types paramétrés.**

---

<a id="sec30"></a>
## `create_all()` ne modifie pas les tables existantes (≠ migration)

`db.create_all()` crée seulement les tables **qui n'existent pas encore**. Si une table
existe déjà, il la **laisse intacte**, même si le modèle a changé (colonnes ajoutées,
nullabilité modifiée…). Ce n'est **pas** un outil de migration.

Conséquence : après avoir modifié un modèle (ex. ajout de `created_at`/`updated_at`, passage
en `Mapped`), relancer l'app ne met **pas** à jour la table existante.

### Fix en dev : recréer la base

- **Option A (rapide)** : supprimer `instance/academie.db`, relancer `python run.py` →
  `create_all` recrée tout avec le nouveau schéma.
- **Option B (réutilisable)** : `init_db(delete=True)` → `db.drop_all()` puis
  `db.create_all()`. Pratique quand le schéma change souvent (ajout de modèles).

### En production

On ne supprime pas la base : on utilise des **migrations** (Alembic / Flask-Migrate) qui
modifient les tables sans perdre les données. Hors scope ici, mais bon à connaître.

---

<a id="sec31"></a>
## `init-db` : une commande CLI Flask pour (re)créer la base

Plutôt que `db.create_all()` au démarrage (effet de bord), on rend la création **explicite**
via une commande. On **retire** donc le bloc `with app.app_context(): db.create_all()` de la
factory.

### La commande (dans `create_app`, après l'import des modèles)

```python
import click   # en haut du fichier

    @app.cli.command("init-db")
    @click.option("--delete", is_flag=True, help="Supprime les tables avant de les recréer.")
    def init_db(delete):
        if delete:
            db.drop_all()
            click.echo("❌ Tables supprimées.")
        db.create_all()
        click.echo("✅ Tables créées.")
```

- `import click` : la CLI de Flask est bâtie sur `click` (déjà installé avec Flask).
- `@app.cli.command("init-db")` : crée la commande `flask init-db`.
- `@click.option("--delete", is_flag=True)` : option interrupteur ; `--delete` présent →
  `delete=True`.
- `click.echo(...)` : affichage propre en CLI.
- **Pas de `with app.app_context()`** : les commandes `@app.cli.command()` s'exécutent déjà
  dans un contexte d'app.

### Utilisation

```powershell
flask init-db            # crée les tables
flask init-db --delete   # supprime puis recrée (appliquer un changement de schéma)
```

Si « Could not locate a Flask application » : `$env:FLASK_APP = "app"` puis relancer.

### Tests

Les tests n'utilisent pas cette commande : `conftest.py` crée les tables via `db.create_all()`
dans une fixture (base en mémoire jetable). `init-db` sert au développement.

### Alternative sans CLI : un script `init_db.py`

Plus simple, proche d'un `init_db` classique, lancé avec `python init_db.py [--delete]` :

```python
"""python init_db.py [--delete]"""
import sys
from app import create_app
from app.dal.database import db

app = create_app()

with app.app_context():
    if "--delete" in sys.argv:
        db.drop_all()
        print("❌ Tables supprimées.")
    db.create_all()
    print("✅ Tables créées.")
```

- `with app.app_context()` : à ouvrir soi-même ici (un script normal n'a pas le contexte
  auto d'une commande `flask`).
- `"--delete" in sys.argv` : version manuelle de l'option `--delete`.

| | Script `python init_db.py` | Commande `flask init-db` |
|---|---|---|
| Simplicité | familier | click + `FLASK_APP` |
| `app_context` | manuel (`with`) | automatique |
| Style | proche des projets classiques | idiomatique Flask |

Les deux font la même chose ; n'en garder qu'un. Dans **tous les cas**, retirer
`db.create_all()` de la factory pour que la création soit explicite.

---

<a id="sec32"></a>
## Lancer un script depuis un sous-dossier (`python -m`)

Déplacer `run.py`/`seed.py`/`init_db.py` dans un dossier `scripts/` **casse** leurs
`from app import ...` si on les lance par `python scripts/run.py` : Python met alors
`scripts/` sur le chemin (pas la racine) → `No module named 'app'` (même cause que la
section 27).

### Solution : lancer en module depuis la racine

```powershell
python -m scripts.run
python -m scripts.init_db --delete
python -m scripts.seed
```

- Ajouter un `scripts/__init__.py` (vide) → `scripts` devient un *package*.
- Toujours lancer **depuis la racine**.
- Pourquoi `-m` marche : il met la **racine** (dossier courant) sur le chemin, pas
  `scripts/` → `app` redevient visible. Les args (`--delete`) sont bien transmis à `sys.argv`.

### Ce qui ne change pas

`instance/academie.db` reste à la racine : son emplacement dépend du package `app`, pas du
dossier courant.

### Convention

Souvent : `run.py` reste à la racine (point d'entrée) et seuls les utilitaires (`seed.py`,
`init_db.py`) vont dans `scripts/`. Sinon, tout dans `scripts/` avec `python -m scripts.xxx`.

---

<a id="sec33"></a>
## Anatomie d'une requête : `select` / `execute` / `scalars` / `all`

Décomposition de `db.session.execute(db.select(Maison)).scalars().all()`, de l'intérieur
vers l'extérieur.

1. **`db.select(Maison)`** — **construit** la requête (un plan « SELECT … FROM maisons »).
   Rien n'est envoyé à la base. Équivalent moderne de `session.query(...)`.
2. **`db.session.execute(...)`** — **exécute** : envoie le SQL, la base répond. Renvoie un
   objet `Result` (des lignes).
3. **`.scalars()`** — **déballe**. Par défaut chaque ligne est un `Row` (tuple) ; comme on a
   sélectionné une seule entité, chaque ligne est `(Maison,)`. `.scalars()` prend le premier
   élément de chaque ligne → objets `Maison` directs.
   - sans : `[(Maison,), (Maison,)]` (tuples)
   - avec : `[Maison, Maison]`
4. **`.all()`** — **collecte** en liste Python. Autres terminateurs : `.first()` (premier ou
   `None`).

```
db.select(Maison)            → PLAN (rien d'exécuté)
db.session.execute(...)      → EXÉCUTE, renvoie des lignes (Row/tuples)
              .scalars()      → DÉBALLE : objets Maison au lieu de tuples
                    .all()     → COLLECTE en liste [Maison, ...]
```

En une phrase : on **décrit** (`select`), on **exécute** (`execute`), on **déballe**
(`scalars`), on **collecte** (`all`). (L'ancien `Maison.query.all()` faisait tout d'un coup
en cachant ces étapes.)

### Équivalent SQL

`db.select(Maison)` correspond à `SELECT * FROM maisons` (en SQL : `SELECT` d'abord, `FROM`
ensuite). Nuance : l'ORM n'écrit pas `*`, il **énumère les colonnes**
(`SELECT maisons.id, maisons.nom, ... FROM maisons`) — même résultat, plus explicite.
Pour voir le SQL réel généré : `SQLALCHEMY_ECHO = True` (déjà dans `DevConfig`) l'affiche
dans la console (utile pour la chasse au N+1 du jour 2).

---

<a id="sec34"></a>
## Créer un objet : `add` vs `commit` (le caddie)

```python
maison = Maison(nom="Gryffondor", couleur="rouge")   # 1. fabriquer l'objet (en mémoire)
db.session.add(maison)                               # 2. mettre dans la session (pending)
db.session.commit()                                  # 3. écrire réellement en base
```

1. **`Maison(...)`** : objet Python en **mémoire** seulement. La base ne le connaît pas, pas
   encore d'`id`.
2. **`db.session.add(maison)`** : **n'écrit rien**. Dit à la session « prends en charge cet
   objet », il passe en attente (pending).
3. **`db.session.commit()`** : envoie l'`INSERT`, l'objet est écrit, la base lui attribue son
   **`id`** (`maison.id` devient disponible).

**Analogie caddie** : `Maison(...)` = prendre l'article ; `.add()` = le mettre dans le
caddie (rien payé) ; `.commit()` = passer en caisse. Avant commit, rien n'est en base ;
`db.session.rollback()` « vide le caddie ».

### Points utiles

- `add` sert aux objets **nouveaux**. Pour **modifier** un objet déjà chargé (via `get`),
  pas besoin de `add` : la session le suit déjà → changer les attributs + `commit`.
- On peut `add` plusieurs objets puis un seul `commit` (utile pour le seed).
- `data["nom"]` plante si absent (bien pour un champ obligatoire) ; `data.get("couleur")`
  renvoie `None` si absent (bien pour un facultatif).

Après `commit`, `maison.id` est rempli → renvoyer `maison` donne l'id créé au controller.

---

<a id="sec35"></a>
## Repository : `update` et `delete` (update partiel, cas introuvable)

```python
def update_maison(maison_id, data):
    maison = get_by_id(maison_id)
    if maison is None:
        return None
    maison.nom = data.get("nom", maison.nom)
    maison.couleur = data.get("couleur", maison.couleur)
    maison.fondateur = data.get("fondateur", maison.fondateur)
    maison.valeurs = data.get("valeurs", maison.valeurs)
    db.session.commit()
    return maison


def delete_maison(maison_id):
    maison = get_by_id(maison_id)
    if maison is None:
        return False
    db.session.delete(maison)
    db.session.commit()
    return True
```

- **`get_by_id` réutilisé** ; cas introuvable géré (`None` / `False`), le controller décidera
  du 404.
- **`update` : pas de `add`** (l'objet est déjà suivi par la session → modifier + `commit`).
- **`data.get("nom", maison.nom)`** : update **partiel** — nouvelle valeur si fournie, sinon
  on garde l'ancienne (évite d'écraser avec `None`).
- **`delete` renvoie `True`/`False`** : pas d'objet à retourner après suppression ; juste
  « supprimé » ou « introuvable ». (`update` renvoie l'objet car le controller doit le
  sérialiser.)
- **Éviter `id` comme nom de paramètre** : masque la fonction intégrée `id()`. Utiliser
  `maison_id`.
- `reputation` non modifiée ici : gérée par la logique de tournoi (jour 3).

---

<a id="sec36"></a>
## Héritage (IS-A) vs association (HAS-A) : Utilisateur ↔ Élève/Prof

Faut-il faire de `Utilisateur` la classe parente (abstraite) d'`Élève`/`Prof`/`Admin` ?
**Non** — ici la bonne relation est l'**association**, pas l'héritage.

### La question à se poser

- **Héritage** = « **est un** » (IS-A) : *un Chien est un Animal*. Pour de vraies
  spécialisations.
- **Association** = « **a un** » (HAS-A) : *une Personne a une Adresse*. Pour référencer/posséder.

Un Élève « est un » Utilisateur ? Non : un élève est une **entité académique** (maison,
année, familier) ; un Utilisateur est un **compte** (email, mot de passe, rôle). L'élève
**a un** compte → HAS-A → association.

### Pourquoi l'association ici

1. Le cahier le demande : « lien optionnel vers un Élève ou un Professeur », « admin lié à
   personne ».
2. L'admin ne référence personne → avec l'héritage il serait un sous-type vide ; avec
   l'association c'est juste `role="admin"` sans lien.
3. Séparation des préoccupations : données académiques ≠ authentification. Ne pas mélanger
   email/mot de passe avec maison/année.

### Design retenu

```
Utilisateur(id, email, mot_de_passe [clair, temporaire], role,
            eleve_id FK null, professeur_id FK null)
```
Contrainte **applicative** : role="eleve" → eleve_id ; role="professeur" → professeur_id ;
admin → aucun.

### Quand l'héritage aurait été pertinent

Pour de vraies variantes d'un même concept (ex. `SortOffensif`/`SortDéfensif` héritant de
`Sort`). SQLAlchemy le gère (héritage polymorphe) mais c'est plus complexe et inutile ici.

### Juste mutualiser une colonne (ex. `nom`) ?

Utiliser un **mixin** (comme `TimestampMixin`), pas une entité parente. Pour une seule
colonne, ça ne vaut pas la peine — garder `nom` dans chaque entité.

---

<a id="sec37"></a>
## Modéliser l'ancienneté : valeur dérivée vs fait fixe

Deux façons de stocker « ancienneté » :

**Option A — un nombre d'années (`int`)**
```python
anciennete: Mapped[int] = mapped_column(default=0)
```
Simple, mais **se périme** : « 5 ans » aujourd'hui = 6 l'an prochain, sauf mise à jour manuelle.

**Option B — une date d'entrée, et on calcule**
```python
from datetime import date
date_embauche: Mapped[date] = mapped_column()
# ancienneté = aujourd'hui − date_embauche (calculée à la demande)
```
Toujours juste, sans maintenance.

### Principe : « âge vs date de naissance »

Ne pas stocker une valeur qui **dérive du temps** (âge, ancienneté) → stocker le **fait
fixe** dont elle découle (date de naissance, date d'embauche) et **calculer** le reste.

### Reco projet

L'ancienneté n'est utilisée dans **aucune règle métier** (jours 2-4), juste affichée. Donc
**Option A (`int`)** est pragmatique et suffisante ici. Option B = modélisation plus
soignée (bon pour un projet évalué) mais nécessite un petit calcul.

---

<a id="sec38"></a>
## Où mettre les `default` ? (modèle vs schéma vs repository)

Ce ne sont **pas des doublons** : chaque `default` protège une **porte d'entrée** différente.

| Couche | Répond à | Protège |
|---|---|---|
| **Modèle** (`mapped_column(default=0)`) | « que met-on en base si aucun code n'a fourni la valeur ? » | **toutes** les créations (API, seed, tests, services) |
| **Schema Create** (`Field(default=0)`) | « le **client** peut-il omettre ce champ ? » | le **contrat de l'API** |
| **Repository** (`data.get("x", 0)`) | « et si le dict passé n'a pas la clé ? » | les appelants du repo |

### Le défaut du schéma n'est pas une redondance

```python
anciennete: int                      # OBLIGATOIRE : le client DOIT l'envoyer
anciennete: int = Field(default=0)   # OPTIONNEL : s'il l'omet → 0
```

Le `default` du schéma **rend le champ facultatif dans le payload** (décision d'API). Sans
lui, un POST sans `anciennete` → **400 champ manquant**. Le `default` du **modèle**, lui,
agit quand du **code Python** crée l'objet sans le champ (ex. `seed.py`) — Pydantic
n'intervient alors pas du tout.

### Exemple parlant

- **`reputation`** (Maison) : `default=0` dans le **modèle**, **absente de `MaisonCreate`** →
  le client ne peut pas la définir (gérée par la logique de tournoi). Seul le modèle agit.
- **`anciennete`** (Professeur) : `default=0` dans le modèle **et** dans `ProfesseurCreate` →
  le client **peut** la fournir, et s'il l'omet → 0.

### Que garder

- **Modèle** : indispensable (filet de sécurité pour tous les chemins de création).
- **Schema Create** : à garder si on veut que le client puisse omettre le champ.
- **Repository** (`.get(..., 0)`) : redondant dans le flux API (Pydantic remplit toujours la
  clé) mais utile si un autre appelant (seed) passe un dict incomplet. Ceinture-bretelles
  inoffensive.

### Règle

> `default` dans le **schéma** = « le client peut l'omettre ».
> `default` dans le **modèle** = « la base a une valeur même si le code l'oublie ».
> Deux protections différentes, à deux portes différentes.

---

<a id="sec39"></a>
## Enregistrer plusieurs blueprints : le registre `routes/__init__.py`

`app.register_blueprint()` prend **un seul blueprint par appel** :

```python
app.register_blueprint(maison_bp, professeur_bp)   # ❌ impossible
app.register_blueprint(maison_bp)                  # ✅
app.register_blueprint(professeur_bp)              # ✅
```

### Boucle

```python
for bp in (maison_bp, professeur_bp):
    app.register_blueprint(bp)
```

### Mieux : un registre (comme `dal/models/__init__.py`)

**`app/api/routes/__init__.py`**
```python
"""Registre des blueprints de l'API."""
from app.api.routes.maison_route import maison_bp
from app.api.routes.professeur_route import professeur_bp

ALL_BLUEPRINTS = (
    maison_bp,
    professeur_bp,
)
```

**`app/__init__.py`**
```python
from app.api.routes import ALL_BLUEPRINTS
...
    for bp in ALL_BLUEPRINTS:
        app.register_blueprint(bp)
```

**Avantage** : à chaque nouvelle entité, une **seule ligne** à ajouter dans
`routes/__init__.py` ; la factory ne change jamais. Sur 13 entités, ça évite d'empiler 26
lignes dans la factory. Même logique de **registre** que `models/__init__.py` → cohérence.

---

<a id="sec40"></a>
## Les index en base de données (à quoi ça sert, ce que ça coûte)

### L'analogie de l'index d'un livre

Chercher « photosynthèse » dans un livre de 900 pages : **sans index**, lire les 900 pages ;
**avec l'index** (trié alphabétiquement, en fin d'ouvrage), aller à P → « page 412 » →
sauter directement.

Un **index de base** = une structure **supplémentaire, triée**, qui associe chaque **valeur**
d'une colonne à **l'emplacement des lignes** correspondantes.

### Ce que ça change

```sql
SELECT * FROM cours WHERE annee_academique = '2025-2026';
```
- **Sans index** : *full table scan* — la base lit **chaque ligne** et compare.
- **Avec index** : recherche dichotomique dans la structure triée → quelques sauts suffisent,
  même sur des millions de lignes.

### ⚠️ Un index n'est pas gratuit

1. **Espace disque** : structure stockée en plus de la table.
2. **Écritures plus lentes** : chaque `INSERT`/`UPDATE`/`DELETE` doit aussi mettre à jour
   l'index. Plus d'index = écritures plus lentes.

→ On n'indexe **pas tout**. On indexe les colonnes souvent utilisées dans un `WHERE`
(filtres), pour **joindre** des tables, ou pour **trier** (`ORDER BY`). C'est un **compromis
lecture/écriture**.

### Déjà indexé automatiquement

- **Clé primaire** (`id`) : toujours (d'où la rapidité de `db.session.get(Maison, 1)`).
- **Colonne `unique=True`** : index unique créé pour vérifier l'unicité → `Maison.nom`,
  `Utilisateur.email` déjà indexés (login rapide).
- **Clés étrangères** : ⚠️ **pas** indexées automatiquement (SQLite, PostgreSQL). À indexer
  si on filtre souvent dessus.

### Dans ce projet

| Colonne | Pourquoi |
|---|---|
| `Cours.annee_academique` | filtré à la clôture d'année (J4) et au listing |
| `Eleve.maison_id` (FK) | « les élèves de telle maison » |
| `Examen.cours_id` (FK) | « les examens de tel cours » |
| `Utilisateur.email` | déjà indexé (unique) |

### Point d'honnêteté

Avec **150 élèves**, aucun gain perceptible : les index comptent à partir de dizaines de
milliers de lignes. On les met par **bonne habitude**, sans coût à cette échelle.

⚠️ Ne pas se tromper d'ennemi : le vrai problème de perf du projet, c'est le **N+1** (jour 2)
— *300 requêtes au lieu de 2*. Un index accélère **une** requête ; aucun index ne corrige un
N+1. Deux problèmes distincts.

---

<a id="sec41"></a>
## Les relations SQLAlchemy : `ForeignKey` + `relationship()`

### Le point de départ : deux mondes à relier

Il y a **deux couches** qui parlent de la même relation, et il faut bien les distinguer.

| | Ce que c'est | Où ça vit | Ce que ça produit |
|---|---|---|---|
| `ForeignKey` | Une **vraie colonne** dans la table | En base (SQLite) | `professeur_id INTEGER REFERENCES professeurs(id)` |
| `relationship()` | Un **attribut Python** | En mémoire, dans l'objet | `cours.professeur` te rend un objet `Professeur` |

`relationship()` **ne crée aucune colonne**. C'est du confort Python par-dessus la
colonne FK. Si tu n'écris que le `ForeignKey`, ta base est correcte — tu devras juste
écrire les jointures à la main. Si tu n'écris que le `relationship()` sans FK,
SQLAlchemy **plante** : il n'a aucun moyen de savoir sur quelle colonne joindre.

> Règle : `ForeignKey` = obligatoire. `relationship()` = très fortement recommandé.

### Où poser la clé étrangère ? Du côté « N »

Un professeur donne **plusieurs** cours ; un cours a **un seul** professeur → relation **1-N**.

```
professeurs (le « 1 »)          cours (le « N »)
+----+----------+               +----+-----------+---------------+
| id | nom      |               | id | intitule  | professeur_id |
+----+----------+               +----+-----------+---------------+
| 1  | Rogue    | <------------ | 1  | Potions   | 1             |
| 2  | Chourave |         \---- | 2  | Potions 2 | 1             |
+----+----------+               | 3  | Botanique | 2             |
                                +----+-----------+---------------+
```

La FK va **toujours du côté « plusieurs »**. Pourquoi ? Parce qu'une colonne ne peut
contenir **qu'une seule** valeur. Mettre `cours_id` dans `professeurs` obligerait Rogue à
choisir un seul de ses deux cours. Alors que `professeur_id` dans `cours` marche : chaque
cours n'a qu'un prof, et rien n'empêche deux lignes de `cours` de pointer vers le même prof.

**Mnémotechnique** : *l'enfant porte le nom de son parent.* Le « N » porte l'id du « 1 ».

### Écrire la FK

```python
from sqlalchemy import ForeignKey

professeur_id: Mapped[int] = mapped_column(ForeignKey("professeurs.id"))
```

Trois détails qui coûtent une heure de debug si on les rate :

1. **`"professeurs.id"` est le nom de la TABLE**, pas de la classe. Donc `professeurs`
   (le `__tablename__`, au pluriel), pas `Professeur`. C'est une chaîne de caractères
   parce que SQLAlchemy la résout au moment de construire le schéma, pas à l'import.
2. **La nullabilité vient du type**, comme d'habitude (cf. [sec29](#sec29)) :
   - `Mapped[int]` → NOT NULL → un cours **doit** avoir un prof.
   - `Mapped[int | None]` → nullable → un cours **peut** être orphelin.
3. **Pas de `default=0`.** Un `default=0` sur une FK signifie « pointe vers le professeur
   n°0 », qui n'existe pas. Une FK n'a pas de valeur par défaut : soit on la fournit,
   soit elle est nullable.

### Nommer la colonne

Convention quasi universelle : **`<entite_au_singulier>_id`**, donc `professeur_id`.
Pas `prof_responsable`, pas `id_professeur`. Deux raisons :

- On lit `cours.professeur_id` et on sait immédiatement que c'est une FK vers `professeurs`.
- Le nom `professeur` (sans `_id`) reste **libre** pour le `relationship()`, qui rendra
  l'objet complet. On aura donc, très naturellement :
  - `cours.professeur_id` → `1` (un entier)
  - `cours.professeur` → `<ID: 1 - Professeur : Rogue>` (l'objet)

### Écrire le `relationship()` des deux côtés

```python
from sqlalchemy.orm import relationship

# Dans Cours (côté N) — un cours pointe vers UN professeur
professeur: Mapped["Professeur"] = relationship(back_populates="cours")

# Dans Professeur (côté 1) — un professeur possède UNE LISTE de cours
cours: Mapped[list["Cours"]] = relationship(back_populates="professeur")
```

Décortiquons.

**Le type dit la cardinalité.** `Mapped["Professeur"]` = un seul objet.
`Mapped[list["Cours"]]` = une liste. SQLAlchemy lit l'annotation pour savoir s'il doit te
rendre un objet ou une collection. C'est le même mécanisme que pour les colonnes : le type
Python porte l'information.

**Les guillemets autour du nom de classe.** `"Professeur"` plutôt que `Professeur`. C'est
une *forward reference* : au moment où Python lit `cours.py`, la classe `Professeur` n'est
peut-être pas encore importée — et si tu l'importais, `professeur.py` devrait importer
`Cours` en retour → **import circulaire**. La chaîne de caractères casse le cycle :
SQLAlchemy la résout plus tard, une fois toutes les classes enregistrées (c'est d'ailleurs
à ça que sert le registre `models/__init__.py`).

**`back_populates`** dit à SQLAlchemy que les deux attributs sont **les deux faces d'une
même relation**. La valeur passée est le nom de l'attribut *d'en face*. Donc, dans `Cours`,
`back_populates="cours"` désigne l'attribut `cours` de `Professeur`, et réciproquement.
C'est croisé, et c'est là qu'on se trompe.

Concrètement, ça synchronise la mémoire dans les deux sens :

```python
c = Cours(intitule="Potions", ...)
rogue.cours.append(c)      # j'ajoute d'un côté...
c.professeur               # -> <Professeur Rogue>  (l'autre côté est déjà à jour)
```

Sans `back_populates`, tu aurais deux relations indépendantes qui ignorent l'existence de
l'autre, et `c.professeur` resterait `None` jusqu'au prochain `commit` + rechargement.

*(Tu croiseras `backref="cours"` dans de vieux tutos : c'est l'ancêtre, il crée
l'attribut d'en face automatiquement — donc invisible quand on lit `Professeur`. On préfère
`back_populates`, explicite des deux côtés.)*

### Ce que ça te donne à l'usage

```python
cours = repo.get_by_id(1)
cours.professeur.nom              # "Rogue"  — SQLAlchemy fait le SELECT pour toi
cours.professeur_id               # 1        — pas de requête, la colonne est déjà là

prof = prof_repo.get_by_id(1)
len(prof.cours)                   # 2
[c.intitule for c in prof.cours]  # ["Potions", "Potions 2"]
```

Et à la création, deux styles équivalents :

```python
Cours(intitule="Potions", professeur_id=1)     # par l'id   (ce que fera ton repo)
Cours(intitule="Potions", professeur=rogue)    # par l'objet
```

Ton repository utilisera le **premier** : le client HTTP t'envoie
`{"intitule": "Potions", "professeur_id": 1}`, tu passes l'entier tel quel.

### Le piège qui arrive : le N+1

`cours.professeur` déclenche **une requête SQL** au moment où tu y accèdes (comportement
`lazy="select"`, le défaut). Sur un objet, c'est invisible. Sur une liste de 100 cours dont
tu sérialises le nom du prof, ça fait **1 requête pour la liste + 100 requêtes pour les
profs** = 101 requêtes. C'est le fameux **N+1**, et c'est exactement ce que le jour 2
demande de traquer et documenter dans `PERFORMANCE.md`.

La parade, quand on en sera là : `selectinload()` / `joinedload()`, qui vont chercher tous
les profs en **une seule** requête supplémentaire. On ne s'en occupe pas maintenant — mais
sache que ce `relationship()` est la source du problème *et* de sa solution.

### Récapitulatif

| Question | Réponse |
|---|---|
| Où va la FK ? | Côté **N** (dans `cours`) |
| Comment on la nomme ? | `professeur_id` |
| Vers quoi elle pointe ? | `ForeignKey("professeurs.id")` → nom de **table** |
| Obligatoire ? | `Mapped[int]` oui / `Mapped[int \| None]` non |
| `relationship()` crée une colonne ? | **Non**, c'est un attribut Python |
| Combien de `relationship()` ? | Un de chaque côté, liés par `back_populates` |
| Nom de classe dans `relationship` ? | Entre **guillemets** (import circulaire) |
| `default=0` sur une FK ? | **Jamais** |

---

<a id="sec42"></a>
## Les deux `relationship()` décortiqués morceau par morceau

Suite de [sec41](#sec41), en zoomant sur les deux lignes elles-mêmes.

### La ligne dans `Cours` (côté N)

```python
professeur: Mapped["Professeur"] = relationship(back_populates="cours")
```

| Morceau | Ce que c'est | Qui le choisit |
|---|---|---|
| `professeur` | le **nom de l'attribut** qu'on écrira : `mon_cours.professeur` | **toi**, librement |
| `:` | annotation de type Python (pas un `=`) | la syntaxe |
| `Mapped[...]` | marqueur qui dit à SQLAlchemy « occupe-toi de ça » | imposé |
| `"Professeur"` | la **classe cible**, celle qu'on récupère au bout | ta classe `Professeur` |
| *pas de* `list[...]` | ⇒ **un seul objet** au bout | la cardinalité |
| `relationship(...)` | dit « ceci n'est **pas** une colonne, c'est un lien » | imposé |
| `back_populates="cours"` | le nom de l'attribut **d'en face**, dans `Professeur` | doit matcher exactement |

Traduction : *« Sur un objet `Cours`, l'attribut `professeur` donnera **un** objet
`Professeur`. L'attribut correspondant, de l'autre côté, s'appelle `cours`. »*

### La ligne dans `Professeur` (côté 1)

```python
cours: Mapped[list["Cours"]] = relationship(back_populates="professeur")
```

| Morceau | Ce que c'est |
|---|---|
| `cours` | nom de l'attribut : `rogue.cours` |
| `list["Cours"]` | ⇒ une **liste** d'objets `Cours` (c'est le `list[...]` qui fait toute la différence) |
| `back_populates="professeur"` | le nom de l'attribut d'en face, dans `Cours` |

Traduction : *« Sur un objet `Professeur`, l'attribut `cours` donnera **une liste** d'objets
`Cours`. L'attribut correspondant, de l'autre côté, s'appelle `professeur`. »*

### Le croisement — LA source d'erreur

```
Cours       professeur: Mapped["Professeur"] = relationship(back_populates="cours")
                ^                                                            |
                |                                                            |
                +--------------------------+            +--------------------+
                                           |            v
Professeur  cours: Mapped[list["Cours"]] = relationship(back_populates="professeur")
```

**`back_populates` ne nomme jamais l'attribut sur lequel il est posé.** Il nomme toujours
celui d'en face. Donc dans `Cours` on écrit `back_populates="cours"` — ce qui a l'air
absurde jusqu'à comprendre que `"cours"` désigne l'*attribut* de `Professeur`, pas la
*classe* `Cours`.

Le test qui sauve : **le mot entre guillemets de `back_populates` doit exister comme nom
d'attribut dans l'autre fichier.** `"cours"` existe dans `professeur.py` ✅ ;
`"professeur"` existe dans `cours.py` ✅.

### Pourquoi deux lignes et pas une ?

Parce qu'une relation a **deux points de vue**, et chaque classe ne connaît que le sien.
Un couloir entre deux pièces : chaque pièce déclare sa propre porte. `back_populates` est
le message « ma porte débouche sur la tienne ».

Un seul côté déclaré ⇒ ça marche **dans un seul sens** : on aurait `cours.professeur` mais
pas `rogue.cours`.

Les deux côtés **sans** `back_populates` :

```python
professeur: Mapped["Professeur"] = relationship()   # ❌
cours: Mapped[list["Cours"]] = relationship()       # ❌
```

SQLAlchemy crée **deux relations indépendantes** qui s'ignorent :

```python
rogue.cours.append(potions)   # j'ajoute d'un côté
potions.professeur            # -> None   l'autre côté n'a rien vu
```

Il faudrait un `commit()` + un rechargement depuis la base pour resynchroniser. Avec
`back_populates`, c'est immédiat en mémoire :

```python
rogue.cours.append(potions)
potions.professeur            # -> <Professeur Rogue>   ✅
```

### « Mais où est la clé étrangère là-dedans ? »

Nulle part, et c'est normal : `relationship()` ne mentionne jamais `professeur_id`.
SQLAlchemy la **trouve tout seul**, parce qu'il n'existe qu'une seule `ForeignKey` entre
`cours` et `professeurs` — aucune ambiguïté à lever.

⚠️ Le jour où une table aura **deux** FK vers la même table cible (typiquement `Duel` avec
`eleve1_id` et `eleve2_id`, au jour 3), il faudra désambiguïser avec `foreign_keys=[...]`.

### Ce qu'on obtient concrètement

```python
potions.professeur          # <Professeur Rogue>   <- 1 requête SQL déclenchée ICI
potions.professeur.nom      # "Rogue"
potions.professeur_id       # 1                    <- aucune requête, la colonne est là

rogue.cours                 # [<Cours Potions>, <Cours Potions 2>]
len(rogue.cours)            # 2
```

Bien noter la différence : `professeur_id` est **une colonne**, déjà chargée.
`professeur` est **une relation** : SQLAlchemy va chercher la ligne en base au moment où on
y touche. C'est précisément ce mécanisme qui produit le **N+1** du jour 2 (cf. [sec41](#sec41)).

---

<a id="sec43"></a>
## Intégrité référentielle : le cours fantôme (`professeur_id: 999`)

### Le problème, démontré

```python
payload = {"intitule": "Magie noire", ..., "professeur_id": 999}
```

Résultat réel, sur une base ne contenant **aucun** professeur :

```
Pydantic : accepté
INSERT   : accepté, id du cours = 1
c.professeur_id  ->  999
c.professeur     ->  None      # cours orphelin
```

Un cours est en base, il pointe vers un professeur inexistant, et aucun des deux gardiens
n'a bronché.

### Pourquoi Pydantic laisse passer

Pydantic ne connaît pas la base. C'est un validateur de **forme**, pas de **cohérence
métier**. Il vérifie « est-ce un entier ≥ 1 ? » — et `999` en est un. Il ne peut pas (et ne
doit pas) interroger la table `professeurs`.

### Pourquoi SQLite laisse passer

Le `CREATE TABLE cours` contient pourtant bien
`FOREIGN KEY(professeur_id) REFERENCES professeurs (id)`. La contrainte est **écrite**,
mais SQLite ne l'**applique pas par défaut** : depuis la 3.6.19 il sait le faire, mais
c'est resté désactivé pour compatibilité. Il faut le demander sur **chaque connexion** :

```sql
PRAGMA foreign_keys = ON;
```

PostgreSQL ou MySQL/InnoDB, eux, auraient refusé l'`INSERT`. ⚠️ C'est donc un bug qui
n'apparaît **qu'en dev sous SQLite**… ou qu'en prod sous PostgreSQL, selon le sens où on
le prend.

### Ce que ça casse

- `cours.professeur` vaut `None` → plus tard, `cours.professeur.nom` lève
  `AttributeError: 'NoneType' object has no attribute 'nom'`, très loin de la vraie cause.
- `seed.py` peut fabriquer des données incohérentes en silence.
- Le problème existe **dans l'autre sens** : `DELETE /professeurs/3` alors que 3 cours le
  référencent → trois orphelins d'un coup, sans avertissement.

### Deux parades complémentaires

**A. `PRAGMA foreign_keys = ON`** — un event listener SQLAlchemy qui exécute le PRAGMA à
chaque connexion. L'`INSERT` fautif lève alors une `IntegrityError`, que `errors.py`
transforme déjà en **409**. Protection **globale**, sur toutes les FK présentes et futures
(Inscription, Résultat, Duel…), impossible à contourner.
*Limite* : message technique (`FOREIGN KEY constraint failed`), ne dit pas quel champ.

**B. Vérification dans le controller** — `professeur_repository.get_by_id(...)` puis
`abort(...)` si `None`. On contrôle le code HTTP **et** le message
(`"Professeur 999 introuvable"`).
*Limite* : il faut **penser** à l'écrire, à chaque endroit, pour chaque FK.

👉 **Faire les deux.** A = la ceinture (intégrité garantie), B = les bretelles (bonne API).

### 404 ou 400 ?

- **404 Not Found** = *la ressource désignée par l'URL n'existe pas*. Or l'URL est
  `POST /cours`, et cet endpoint existe. Ce qui est introuvable est mentionné dans le
  **corps**. Répondre 404 laisserait croire que `/cours` n'existe pas.
- **400 Bad Request** (ou 422) = *requête mal formée ou incohérente*. C'est exactement le
  cas, et c'est cohérent avec `validate_body` qui renvoie déjà 400.

👉 **Choix retenu : 400**, avec `{"error": "Professeur 999 introuvable"}`. Le 404 reste
réservé à son vrai sens : `GET /cours/999`.

Les deux se défendent ; l'essentiel est de savoir **pourquoi** on a choisi, et de
l'écrire dans le README.

### Pourquoi dans le controller, pas dans le repository ?

Le repository ne décide **jamais** d'un code HTTP (cf. `delete_cours` qui renvoie
`True`/`False`). Il parle base de données. Le controller est la couche qui traduit
« le prof n'existe pas » en « 400 + ce message ».

Si la règle se complique un jour (« un cours ne peut être rattaché qu'à un prof enseignant
cette matière »), ça migrera dans `services/`. Pour une simple vérification d'existence, le
controller suffit.

### Le cas particulier du PATCH

Avec `exclude_unset=True`, `professeur_id` peut être **absent** du dict :

- `PATCH {"niveau": "2"}` → pas de `professeur_id`, rien à vérifier.
- `PATCH {"professeur_id": 999}` → il faut vérifier.

La vérification doit donc être **conditionnelle** (seulement si la clé est présente),
sinon on appelle `get_by_id(None)` sur un PATCH qui ne touche pas au prof.

### TOCTOU (pour la culture)

Même avec la vérification applicative, il reste une fenêtre théorique entre le
`get_by_id()` (le prof existe) et le `commit()` (le prof vient d'être supprimé par une
autre requête) : c'est un **TOCTOU**, *Time Of Check To Time Of Use*.

Sur un projet solo, ça n'arrivera jamais. Mais c'est **l'argument décisif** pour la parade
A : seule la base, qui verrouille au moment de l'écriture, garantit l'intégrité sans faille.
La vérification applicative est là pour le confort du client, pas pour la sûreté.

---

<a id="sec44"></a>
## Refuser la suppression d'un parent qui a des enfants (409 explicite)

### Le contexte

Supprimer un `Professeur` qui a des `Cours` échoue **déjà** : SQLAlchemy tente de mettre
`cours.professeur_id` à `NULL` (cascade « nullify » par défaut), la colonne est `NOT NULL`,
SQLite lève une `IntegrityError`, et `errors.py` la traduit en 409.

Mais le message est générique : *« Conflit : violation d'une contrainte d'unicité ou
d'intégrité »*. Le client ne sait ni **quoi** a échoué, ni **quoi faire**.

⚠️ Décision métier prise : **on refuse**, on ne cascade pas. Un prof qui part ne doit pas
emporter ses cours (et, plus tard, les inscriptions / examens / résultats qui en dépendent
— la cascade est **transitive**).

### Le problème structurel de l'ancienne version

```python
def supprimer(professeur_id):
    supprime = repo.delete_professeur(professeur_id)   # supprime D'ABORD
    if not supprime:                                   # pose les questions ENSUITE
        abort(... 404 ...)
    return "", 204
```

Tant qu'il n'y avait **qu'une** raison d'échouer (le prof n'existe pas), un `True`/`False`
suffisait. Il y en a maintenant **deux** (n'existe pas → 404 ; a des cours → 409), et un
booléen ne peut pas porter deux causes distinctes.

👉 Il faut **inverser l'ordre** : récupérer, inspecter, décider, supprimer en dernier.

### Étape 1 — Récupérer au lieu de supprimer

`repo.get_by_id(professeur_id)` rend l'**objet complet**, pas un booléen. Et un objet
`Professeur` porte l'attribut `cours` grâce au `relationship()` (cf. [sec41](#sec41)).
Sans cet objet en main, aucune inspection n'est possible. À ce stade, **rien n'est encore
supprimé**.

### Étape 2 — Le 404 se déplace

`if professeur is None:` → même `abort` 404 qu'avant. Le comportement ne change pas, la
**source de l'information** change : on ne déduit plus l'inexistence de l'échec de la
suppression, on la constate.

`abort()` **interrompt la fonction** (Flask lève une exception qui remonte au handler).
Donc après ce `if`, on sait avec certitude que `professeur` n'est pas `None`.

### Étape 3 — Le garde-fou (la vraie nouveauté)

`if professeur.cours:` — trois choses s'y passent :

1. SQLAlchemy déclenche une requête cachée : `SELECT * FROM cours WHERE professeur_id = 1`
   (*lazy loading*).
2. Elle rend une liste (`InstrumentedList`, utilisable comme une liste normale).
3. En Python une **liste vide est falsy** → pas besoin de `len(...) > 0`.

Si non vide : `abort` avec **409** (pas 400 : la requête est bien formée ; pas 404 : le prof
existe) et un message utilisant `len(professeur.cours)`.

Le message doit répondre à *pourquoi ça a échoué et que puis-je faire* :
> « Impossible de supprimer : ce professeur est responsable de 3 cours »

### Étape 4 — Supprimer, enfin

`repo.delete_professeur(professeur_id)`. Existence vérifiée, cours vérifiés : ça ne peut
plus échouer. Garder le `if not supprime:` en filet est gratuit (protège du TOCTOU,
cf. [sec43](#sec43)).

### Étape 5 — La sortie

`return "", 204` inchangé. On ne renvoie un message qu'en cas d'échec, et ceux-là passent
par `abort()`. (Un **204 n'a pas de corps** : Flask jetterait silencieusement un `jsonify`
renvoyé avec ce code.)

### Le squelette

```
def supprimer(professeur_id):
    professeur = <récupérer>
    if <n'existe pas>:
        abort(... 404 ...)
    if <a des cours>:
        abort(... 409 avec le compte ...)
    <supprimer>
    return "", 204
```

Motif général : **valider, valider, valider, agir.** Chaque `abort()` est une sortie
anticipée ; le code qui suit peut supposer vrai tout ce qui précède.

### Les deux couches restent

Le handler `IntegrityError → 409` ne devient pas inutile : il reste le **filet** si un autre
chemin d'écriture (script, `seed.py`, futur endpoint admin) oublie la vérification. Le
message sera juste moins beau.

- vérification applicative → **confort** du client (message clair)
- contrainte en base → **sûreté** (impossible à contourner)

Ici, pas besoin du `PRAGMA foreign_keys` : c'est le `NOT NULL` de `professeur_id` qui fait
le travail.

### Aucun nouvel import

`abort`, `make_response`, `jsonify` sont déjà importés ; `repo.get_by_id` existe déjà.
La seule chose « nouvelle » est `professeur.cours` — et c'est précisément ce pour quoi le
`relationship()` a été écrit.

---

<a id="sec45"></a>
## Qu'est-ce qu'une fonction « helper » ?

Rien de technique. Un **helper**, c'est une fonction ordinaire écrite pour soi-même, parce
qu'elle rend service à plusieurs endroits du même fichier. Le mot n'existe pas dans Python :
c'est du **vocabulaire de développeur**, pas un mécanisme du langage.

### On en a déjà un

```python
def _serialize(cours):
    return CoursOut.model_validate(cours).model_dump(mode="json")
```

`_serialize` n'est appelée par **aucune route**. Flask ne la connaît pas. C'est *nous* qui
l'appelons, depuis `lister()`, `recuperer()`, `creer()` et `modifier()`. Elle existe parce
qu'on allait taper la même ligne quatre fois.

### Les deux conventions

**1. L'underscore devant le nom.** `_serialize`, pas `serialize`. Ça ne change **rien** au
fonctionnement : c'est un signal au lecteur — *« fonction privée à ce module, ne l'appelle
pas depuis l'extérieur »*. Les routes appellent `lister()` et `creer()`, jamais
`_serialize()`.

**2. La place dans le fichier.** Après les imports, avant les fonctions publiques.
Les helpers sont les outils ; les fonctions publiques sont le travail.

### Le helper à écrire pour Cours

```python
def _verifier_professeur(professeur_id):
    ...   # get_by_id, puis abort(400) si None
```

Une fonction, deux appels : un dans `creer()`, un dans `modifier()` (conditionnel,
cf. [sec43](#sec43)). Sans elle, le même `get_by_id` + `if` + `abort` serait écrit deux
fois — et le jour où on change le message ou le code HTTP, il faut se souvenir des deux
endroits.

### La règle empirique

**Dès qu'on écrit deux fois la même chose, on l'extrait.** Pas parce que c'est plus court,
mais parce que le duplicata finit toujours par **diverger** : on corrige un endroit et pas
l'autre.

⚠️ Vécu sur ce projet : `lister_courss` renommé au `return` mais pas à l'assignation
→ `NameError: name 'liste_courss' is not defined`. Deux endroits, un seul corrigé.
C'est aussi la source du piège du copier-coller entre verticales.

---

<a id="sec46"></a>
## Vérifier une FK dans le controller, morceau par morceau

Mise en œuvre concrète de [sec43](#sec43) (le cours fantôme), avec le helper de
[sec45](#sec45). Choix retenu : **pas de `PRAGMA foreign_keys`**, vérification applicative.

### Morceau 1 — l'import

```python
from app.dal.repositories import professeur_repository as prof_repo
```

Le `as prof_repo` est **obligatoire** ici : la ligne du dessus fait déjà
`import cours_repository as repo`. Sans alias, deux modules se disputeraient le même nom.
Avec, on lit `repo.` = « cours » et `prof_repo.` = « professeurs », sans ambiguïté.

### Morceau 2 — le helper

À placer juste après `_serialize`, avant `lister()`.

```python
def _verifier_professeur(professeur_id):
    """Interrompt la requête (400) si le professeur référencé n'existe pas."""
    if prof_repo.get_by_id(professeur_id) is None:
        abort(make_response(jsonify({"error": f"Professeur {professeur_id} introuvable"}), 400))
```

- **`prof_repo.get_by_id(...)`** → `SELECT * FROM professeurs WHERE id = ?`. Rend l'objet,
  ou `None`.
- **`is None`** — pas besoin de stocker le résultat : on veut seulement savoir s'il existe.
  (Écrire `professeur = prof_repo.get_by_id(...)` puis `if professeur is None:` est
  équivalent, et plus lisible pour certains.)
- **`abort(make_response(jsonify(...), 400))`** — `abort()` lève une exception : la fonction
  s'arrête **et la fonction appelante aussi**. C'est le point clé : `creer()` n'a rien à
  tester après l'appel, si le prof n'existe pas on n'y arrive jamais.
- **`400`** et pas 404 : la requête est mal formée (elle référence une entité inexistante),
  mais l'endpoint `/cours` existe bel et bien.
- **f-string** → `"Professeur 999 introuvable"`. Le client sait quoi corriger.
- **Pas de `return`** : c'est une *garde*, pas un calcul. Soit elle laisse passer en
  silence, soit elle fait tout exploser.

### Morceau 3 — `creer()`

```python
def creer():
    donnees = validate_body(CoursCreate)
    _verifier_professeur(donnees.professeur_id)
    cours = repo.create_cours(donnees.model_dump())
    return jsonify(_serialize(cours)), 201
```

Une seule ligne ajoutée, au bon endroit : **après** la validation de forme, **avant**
l'écriture. `donnees` est un objet Pydantic → on accède au champ **avec un point**.

### Morceau 4 — `modifier()`

```python
def modifier(cours_id):
    donnees = validate_body(CoursUpdate)
    champs = donnees.model_dump(exclude_unset=True)
    if "professeur_id" in champs:
        _verifier_professeur(champs["professeur_id"])
    cours = repo.update_cours(cours_id, champs)
    if cours is None:
        abort(make_response(jsonify({"error": "Cours introuvable"}), 404))
    return jsonify(_serialize(cours)), 200
```

- **`champs = donnees.model_dump(exclude_unset=True)`** — seul vrai changement structurel :
  le dict est rangé dans une variable pour pouvoir être **inspecté** avant usage.
- **`if "professeur_id" in champs:`** — sur un dict, `in` teste la présence d'une **clé**.
  Sur `PATCH {"niveau": "2"}`, `champs` vaut `{"niveau": "2"}` → pas de vérification.
  ⚠️ Sans ce `if`, on appellerait `_verifier_professeur(None)` sur tous les PATCH qui ne
  touchent pas au prof → `"Professeur None introuvable"`, absurde.
- **`champs["professeur_id"]`** — crochets + guillemets (dict), alors que `creer()` écrit
  `donnees.professeur_id` (objet Pydantic). **Même donnée, deux syntaxes** selon l'endroit
  du flux : piège classique.
- **L'ordre** : vérification **avant** `update_cours()`. Sinon on écrit une valeur invalide
  en base, puis il faut un rollback.
- **`if cours is None`** reste, et ne fait pas double emploi : le **400** dit « le
  professeur référencé n'existe pas », le **404** dit « le cours à modifier n'existe pas ».
  Deux entités, deux erreurs.

### Le motif général

```
valider la forme  →  valider les références  →  agir  →  répondre
```

Chaque garde fait gagner une certitude pour la suite. Même structure que
`controller_professeur.supprimer()` ([sec44](#sec44)).

---

<a id="sec47"></a>
## `Literal[]` de Pydantic : annotation de type, pas argument de `Field()`

### D'où il vient

`Literal` n'appartient pas à Pydantic : c'est un outil du module standard `typing`.

```python
from typing import Literal
```

### Une annotation de type, au même endroit que `str` ou `int`

Contrairement à `min_length`, `max_length` ou `pattern` (qui sont des **arguments** de
`Field()`), `Literal` **remplace le type** lui-même :

```python
statut: Literal["inscrit", "diplome", "renvoye"]
```

Lecture : « `statut` n'est pas n'importe quelle chaîne, c'est **exactement une** de ces
trois valeurs ». Toute autre valeur est rejetée automatiquement (400 via
`validate_body`, [sec18](#sec18)), sans avoir besoin d'un `pattern` regex à la main.

### Avec une valeur par défaut

`Field()` reste utile pour le `default`, mais en argument **nommé**, pas en position :

```python
statut: Literal["inscrit", "diplome", "renvoye"] = Field(default="inscrit")
# raccourci équivalent :
statut: Literal["inscrit", "diplome", "renvoye"] = "inscrit"
```

### Champ optionnel (schéma `Update`)

Même recette que les autres champs optionnels du projet, avec `| None` :

```python
statut: Literal["inscrit", "diplome", "renvoye"] | None = Field(default=None)
```

### Erreur rencontrée

```python
familier: str = Field(Literal["inscrit", "diplome", "renvoye"])
```

Deux fautes cumulées :
1. `Literal[...]` passé **en position** à `Field()` — qui attend un `default` à cette
   place, pas un type. Ne valide rien.
2. Le `Literal` visait en réalité `statut` (les 3 valeurs du modèle `Eleve`,
   [sec23](#sec23)), pas `familier` (qui doit rester un `str` libre, ex. "Hedwige").
   C'est `statut` qui portait à la place un `pattern` de date copié depuis
   `annee_academique` de `Cours` — encore le piège du copier-coller entre verticales
   (déjà vu en [sec45](#sec45)).

### Repère mental

`Field(...)` = **comment** contraindre une valeur (bornes, regex, défaut).
`Literal[...]` = **quelles** valeurs sont même autorisées, au niveau du type. Les deux se
combinent (`Literal[...] = Field(default=...)`), mais `Literal` n'est jamais un argument
*dans* `Field()`.
