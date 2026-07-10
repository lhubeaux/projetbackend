# Plan de continuation — Académie de Sorcellerie

État des lieux au 10/07 (fin d'après-midi) : les **cinq** verticales — **Maison**, **Professeur**,
**Cours**, **Élève** et **Utilisateur** — sont complètes (modèle → repository → schémas Pydantic →
controller → routes), vérifiées en exécution de bout en bout, et les préfixes d'URL sont
uniformisés au pluriel (`/maisons`, `/professeurs`, `/cours`, `/eleves`, `/utilisateurs`).
La validation Pydantic et les timestamps `created_at`/`updated_at` sont en place (exigences du
jour 4 prises en avance ✅). Restent pour le jour 1 : le login (1.3), le seed (1.4) et les
premiers tests (1.5). `seed.py`, `auth.py`, `conftest.py` et `services/` sont des squelettes vides.

---

## Étape 1 — Finir le Jour 1 : Élève, Utilisateur, login, seed

### 1.1 Verticale Élève ✅ (commit `ef7d1df`)
- [x] `eleve_repository.py` : lister / get_by_id / create / update / delete.
- [x] `eleve_schema.py` : `EleveCreate`, `EleveUpdate`, `EleveOut`.
      `statut` restreint via `Literal[...]` ✅. ⚠️ `annee` n'a que `ge=1` : le `le=7`
      prévu n'a pas été posé — à ajouter avant le passage d'année du jour 4.
- [x] `controller_eleve.py` : vérifie que `maison_id` existe (→ 400).
- [x] `eleve_route.py` + ajout dans `ALL_BLUEPRINTS` (préfixe passé au pluriel `/eleves`).
- [x] Garde-fou : suppression d'une **Maison** qui a des élèves → 409.

### 1.2 Entité Utilisateur ✅ (10/07 après-midi, vérifiée de bout en bout)
- [x] Modèle `Utilisateur` : `email` (unique), `mot_de_passe` en clair avec commentaire
      TEMPORAIRE, `role`, FK **nullables** et `unique=True` (1 compte max par élève/prof),
      relations 1-1 `eleve`/`professeur` posées des deux côtés.
- [x] Contrainte applicative rôle ⇒ lien : `model_validator(mode="after")` dans
      `UtilisateurCreate` (cf. explications.md sec48–52).
- [x] CRUD **complet** (pas seulement minimal) : les 5 endpoints sous `/utilisateurs`.
      En plus du plan : 409 si email déjà pris (`_verifier_email_libre`, qui exclut
      l'utilisateur lui-même en PATCH), `UtilisateurUpdate` limité à email/mot_de_passe,
      `mot_de_passe` jamais sérialisé dans `UtilisateurOut`.
- ⚠️ Point connu (découvert en vérification) : `DELETE /eleves/<id>` sur un élève
      référencé par un compte réussit et laisse un utilisateur `role="eleve"` avec
      `eleve_id = NULL` (SQLite n'applique pas les FK par défaut). À trancher :
      cascade, 409 comme Maison, ou statu quo documenté.

### 1.3 Connexion simulée
- [ ] `POST /login` : email + mot de passe → renvoie l'utilisateur, son rôle,
      et `eleve_id` ou `professeur_id`. Mauvais identifiants → 401.
- [ ] Dans `app/common/auth.py` : un décorateur (ou helper) qui lit le header
      `X-User-Id`, charge l'utilisateur et le rend accessible au controller.
      Header absent → 401 explicite. Prévoir deux variantes : "utilisateur requis"
      et "admin requis" — elles serviront tous les jours suivants.

### 1.4 Script de seed (idempotent dès le départ)
- [ ] `scripts/seed.py` : pattern **get-or-create** (chercher par clé naturelle —
      nom de maison, email d'utilisateur — avant d'insérer). Relançable sans doublon.
- [ ] Volume jour 1 : 4 maisons, ~30 élèves répartis sur les 7 années, quelques
      professeurs et cours, un utilisateur par élève/professeur + un admin.
- [ ] Documenter la commande de lancement dans le README.

### 1.5 Premiers tests
- [ ] Remplir `tests/conftest.py` : fixture app avec `TestConfig`, `db.create_all()`,
      client de test, session propre par test.
- [ ] Un test de login + un test CRUD simple pour valider le socle.

**✔ Critère de fin :** une personne extérieure peut faire le CRUD sur les 4 ressources,
se connecter avec un compte du seed et obtenir rôle + id.
**Commit de fin de jour.**

---

## Étape 2 — Jour 2 : inscriptions, examens, résultats, premier endpoint métier

C'est ici que le dossier `services/` prend son sens : la logique métier
(clôture d'examen, contrôle de capacité) y va, les controllers restent minces.

### 2.1 Nouvelles entités
- [ ] `Inscription` (association enrichie Élève ↔ Cours) : `date_inscription`, `statut`
      (`inscrit / en_cours / valide / abandonne`) + **contrainte d'unicité (eleve_id, cours_id)**
      pour éviter la double inscription.
- [ ] `Examen` : rattaché à un Cours (1-N), titre, date, `seuil_reussite`.
- [ ] `Resultat` (association enrichie Élève ↔ Examen) : `note` + unicité (eleve_id, examen_id).

### 2.2 Endpoints
- [ ] `POST /cours/<id>/inscriptions` : refuse proprement (409 ou 400) si le cours est
      complet — compter les inscriptions actives vs `capacite_max`, **dans un service**.
- [ ] Saisie **en masse** des résultats d'un examen : un payload avec la liste
      `[{eleve_id, note}, ...]` — valider chaque note (bornes min/max) via Pydantic.
- [ ] `POST /examens/<id>/cloture` : met à jour le statut des inscriptions selon le
      seuil et renvoie un vrai bilan (moyenne du cours, nb validés/échoués) — pas un 200 vide.

### 2.3 Espace élève / espace admin (utilise auth.py de l'étape 1)
- [ ] Élève via `X-User-Id` : `GET /me/cours`, `GET /me/notes`, `GET /me/dossier` —
      uniquement ses propres données.
- [ ] Admin : résultats filtrables par cours/examen, moyenne par cours.

### 2.4 Chasse au N+1 (obligatoire)
- [ ] `SQLALCHEMY_ECHO = True` est déjà actif : compter les requêtes sur un listing
      (ex. élèves d'un cours avec `eleve.maison.nom`).
- [ ] Corriger avec `selectinload()` / `joinedload()`, **optionnel via un paramètre de
      requête** (ex. `?include=maison`), pas systématique.
- [ ] Consigner le chiffre avant/après dans `PERFORMANCE.md`.

### 2.5 Tests métier
- [ ] La clôture d'examen met à jour les statuts selon le seuil.
- [ ] L'inscription à un cours complet est refusée.

**Commit de fin de jour.**

---

## Étape 3 — Jour 3 : compétences, tournois, duels

### 3.1 Entités
- [ ] `Competence` : nom, catégorie, description, condition de déblocage
      (soit `examen_id` + `note_minimale`, soit "victoire en tournoi").
- [ ] `Maitrise` (Élève ↔ Compétence) : date d'obtention, source (`examen` / `tournoi`),
      référence vers la source + **unicité (eleve_id, competence_id)** — c'est cette
      contrainte qui garantit l'idempotence en dernier recours.
- [ ] `Tournoi` : nom, année, maison organisatrice (nullable).
- [ ] `Duel` : tournoi, deux élèves, vainqueur (valider que le vainqueur est bien
      l'un des deux participants).

### 3.2 Endpoints métier (dans services/)
- [ ] Évaluation des compétences après clôture d'examen : créer les Maîtrises
      manquantes uniquement. **Idempotent** : relancer 2× ne crée aucun doublon
      (vérifier l'existence avant insertion, l'unicité en base en filet de sécurité).
- [ ] `POST /tournois/<id>/cloture` : vainqueur = le plus de victoires en duel
      (décider la règle en cas d'égalité et la documenter), déblocage des compétences
      liées, `reputation += X` sur la maison du vainqueur.

### 3.3 Espace élève / admin
- [ ] Élève : mes compétences, mon historique tournois/duels.
- [ ] Admin : CRUD catalogue de compétences, création tournoi, saisie des duels.

### 3.4 Pagination et filtres
- [ ] Compétences filtrables par catégorie, tournois par année ; pagination sur les
      deux (`?page=&per_page=`) — factoriser un helper réutilisable dans `common/`.

### 3.5 Seed et tests
- [ ] Seed : 15–20 compétences au catalogue.
- [ ] Test idempotence du déblocage ; test clôture de tournoi
      (compétence obtenue + réputation qui monte).

**Commit de fin de jour.**

---

## Étape 4 — Jour 4 : passage de fin d'année et fiabilisation

### 4.1 Clôture de l'année académique (le gros morceau — dans services/)
- [ ] Entité `ClotureAnnee` (année académique clôturée + date) : c'est elle qui
      permet de **refuser explicitement un rejeu** (409 si l'année est déjà clôturée).
- [ ] Pour chaque élève actif : moyenne générale sur ses inscriptions validées de
      l'année ; puis :
      - moyenne ≥ seuil (`PROMOTION_THRESHOLD`, déjà dans config.py ✅) et année < 7 → **promotion**,
      - moyenne < seuil → **redoublement**,
      - année 7 et moyenne ≥ seuil → **diplomation** (statut `diplome`, dossier conservé).
- [ ] Renvoyer le **détail des décisions** (qui est promu/redoublant/diplômé et pourquoi).

### 4.2 Fiabilisation
- [ ] Vérifier que **tous** les endpoints d'écriture de la semaine passent par
      `validate_body` (c'est déjà le cas pour les 3 verticales existantes).
- [ ] Rejouer la chasse au N+1 sur les nouveaux listings avec le gros volume.

### 4.3 Seed final
- [ ] ≥ 150 élèves, plusieurs examens, tournois, maîtrises déjà débloquées —
      toujours idempotent.

### 4.4 Documentation et livraison
- [ ] README complet : installation, variables d'environnement, seed, lancement,
      tests, **exemples curl pour tous les endpoints** (login, X-User-Id, cas d'erreur).
- [ ] `PERFORMANCE.md` finalisé avec les chiffres avant/après.

### 4.5 Tests finaux
- [ ] Les trois issues du passage d'année (promotion / redoublement / diplomation).
- [ ] Refus de la double clôture d'une même année.

**Commit final.**

---

## Rappels transverses (à garder en tête à chaque étape)

- **Un commit par jour minimum**, message clair — l'historique est évalué.
- Toute nouvelle logique de décision (capacité, clôtures, déblocage) va dans
  `services/`, pas dans les controllers ni les repositories.
- Chaque nouvelle association N-N reçoit une **contrainte d'unicité** en base :
  c'est le filet de sécurité de l'idempotence et de la non-duplication exigées.
- Réutiliser les patterns déjà en place : `validate_body`, handler `IntegrityError`
  → 409, garde-fou 409 avant suppression d'un parent référencé, `TimestampMixin`.
- Attention au piège du copier-coller entre verticales : relire chaque nom de
  champ/ressource après duplication d'un fichier.
