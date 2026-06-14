# learnEnglish — Besoin & Attendu Client

> **Document source de vérité** — Si le résultat final n'est pas aligné avec ce document, le projet est un échec.
> À lire avant toute décision technique. À relire avant chaque phase de développement.

---

## 1. Le problème

### 1.1 Constat

J'apprends l'anglais depuis des années. Je lis, j'écoute, je comprends de mieux en mieux. Mais il y a un trou noir : **les phrasal verbs**.

- `get over`, `run out of`, `put up with`, `bring about` — je les reconnais, je ne les utilise pas.
- Les listes de vocabulaire traditionnelles ne marchent pas : je les apprends, je les oublie.
- Les applis existantes (Duolingo, Memrise) sont généralistes — elles ne ciblent pas spécifiquement les phrasal verbs.
- Les cartes mémoire papier / Anki sont statiques — pas d'adaptation à ma progression.

### 1.2 Pourquoi c'est dur

| Problème | Exemple |
|----------|---------|
| Sens non littéral | `give up` ≠ "donner en haut" mais "abandonner" |
| Multiples sens | `take off` = décoller / enlever / imiter / décoller (carrière) |
| Pas d'image mentale | `run out of` = ? Un réservoir qui se vide ? |
| Ouubli rapide | Sans répétition espacée, 70% oublié en 48h |

### 1.3 Ce que j'ai essayé (et pourquoi ça n'a pas marché)

| Méthode | Résultat |
|---------|----------|
| Listes papier | Appris → oublié en 1 semaine |
| Anki (cards brutes) | Pas de contexte, pas d'image, pas adaptatif |
| Duolingo | Trop général, pas focus phrasal verbs |
| Regarder des séries en VO | Je les entends, je ne les retiens pas |
| Cahier de vocabulaire | Tenir à jour est trop lourd |

---

## 2. Le besoin

### 2.1 En une phrase

> Une application personnelle, accessible sur mon téléphone et mon PC en local, qui me fait **apprendre et retenir les phrasal verbs anglais** grâce à des **images mentales fortes** et un **système de répétition espacée** qui s'adapte automatiquement à ma mémoire.

### 2.2 Décomposition du besoin

| Besoin | Pourquoi |
|--------|----------|
| **Apprentissage visuel** | Je retiens mieux avec une image mentale forte qu'avec du texte |
| **Pas de texte dans l'image** | L'image doit être universelle, pas dépendante de la langue |
| **Répétition espacée** | Revoir au bon moment pour ancrer durablement |
| **Adaptatif** | L'appli apprend de mes erreurs et ajuste le programme |
| **Mobile + desktop** | Je veux réviser sur mon téléphone (LAN) et sur mon PC |
| **Focus phrasal verbs** | Pas 5000 mots génériques — ~240 phrasal verbs essentiels |
| **Progression visible** | Voir mon streak, ma maîtrise, mes points faibles |
| **Une carte à la fois** | Je ne veux qu'un seul élément d'attention par écran — apprendre ou être testé, pas les deux en même temps |
| **Je choisis mon rythme** | Je décide combien de mots apprendre, combien réviser, et quels types d'exercices faire |

---

## 3. Ce que le client verra (expérience utilisateur)

### 3.1 Connexion

Écran simple. Email + mot de passe. Pas de Google, pas de magic link, pas de OAuth.

Première connexion : création de compte → redirection vers le dashboard.

### 3.2 Dashboard (page d'accueil)

```ascii
┌──────────────────────────────────────────────────┐
│  🔥 12 jours de streak              [Paramètres] │
│                                                  │
│  Aujourd'hui                                     │
│  ┌──────────────────────────────────────┐        │
│  │  À réviser :  23 expressions         │        │
│  │  Fait aujourd'hui : 15  (78%)        │        │
│  │  Nouveaux mots : 3/5                 │        │
│  │                                      │        │
│  │  [📚 Commencer la révision]          │        │
│  │  [✨ Apprendre de nouveaux mots]     │        │
│  └──────────────────────────────────────┘        │
│                                                  │
│  Progression globale                             │
│  ┌──────────────────────────────────────┐        │
│  │  🟢 Maîtrisé :  34   ████████░░ 40%  │        │
│  │  🟡 En cours :  42   ██████████░ 49%  │        │
│  │  ⚪ Nouveaux :  11   ██░░░░░░░░ 12%  │        │
│  └──────────────────────────────────────┘        │
└──────────────────────────────────────────────────┘
```

Le dashboard me donne envie de continuer. Voir mon streak me motive à ne pas casser la chaîne.

### 3.3 Session d'apprentissage (LEARN)

Je clique sur "Apprendre de nouveaux mots" :

#### Étape 0 — Je choisis combien de mots

```
┌──────────────────────────────────────┐
│  ✨ Apprendre de nouveaux mots       │
│                                      │
│  Combien de mots aujourd'hui ?       │
│                                      │
│     ┌──────────────────────────┐     │
│     │         [ 5 ]            │     │
│     └──────────────────────────┘     │
│     (par défaut : 5, je peux         │
│      mettre 3, 7, 10...)             │
│                                      │
│  Disponibles : 12 nouveaux mots      │
│                                      │
│  [✅ Commencer l'apprentissage]      │
└──────────────────────────────────────┘
```

Je décide. Pas imposé.

#### Étape 1 — Découverte + mini-test optionnel (une par une)

**Un seul mot par écran. Si l'option "mini-test après chaque carte" est activée dans les paramètres, une mini-question suit chaque carte découverte.**

```
Mode 1 — mini-test désactivé (paramètre OFF) :

Carte 1/5
┌──────────────────────────────────────┐
│                                      │
│  ┌────────────────────────────┐      │
│  │                            │      │
│  │      🖼️ IMAGE              │      │
│  │      (obstacle /           │      │
│  │       mur franchi)         │      │
│  │                            │      │
│  └────────────────────────────┘      │
│                                      │
│  get over                            │
│  = surmonter                         │
│                                      │
│  "It took her months to              │
│   get over the breakup."             │
│                                      │
│        [⏭ Suivant →]                │
└──────────────────────────────────────┘

→ Je clique Suivant → Carte 2/5
```

```
Mode 2 — mini-test activé (paramètre ON) :

Carte 1/5
┌──────────────────────────────────────┐
│                                      │
│  ┌────────────────────────────┐      │
│  │                            │      │
│  │      🖼️ IMAGE              │      │
│  │                            │      │
│  └────────────────────────────┘      │
│                                      │
│  get over                            │
│  = surmonter                         │
│                                      │
│  "It took her months to              │
│   get over the breakup."             │
│                                      │
│        [⏭ Suivant →]                │
└──────────────────────────────────────┘

    ↓ Après avoir cliqué Suivant ↓

┌──────────────────────────────────────┐
│  Mini-test : que signifie "get over" ?│
│                                      │
│  ○ a) monter sur                     │
│  ○ b) surmonter                      │  ← bonne réponse
│  ○ c) descendre                      │
│  ○ d) contourner                     │
│                                      │
│         [Valider]                    │
└──────────────────────────────────────┘

    ↓ Feedback ↓

┌──────────────────────────────────────┐
│  ✅ Correct !                        │
│                                      │
│         [⏭ Carte suivante →]        │
└──────────────────────────────────────┘

→ Carte 2/5
```

**Résumé :** Découverte pure quand le paramètre est OFF. Découverte + quiz immédiat quand le paramètre est ON. L'utilisateur choisit dans les paramètres, pas de forcing.

```
Résultat final (identique dans les deux modes)
┌──────────────────────────────────────┐
│  🎉 Session terminée !               │
│                                      │
│  5 mots appris                       │
│  Score : 4/5 (80%)                   │
│  Temps moyen : 4.2s                  │
│                                      │
│  🔥 Streak : 12 jours                │
│                                      │
│        [🏠 Retour au Dashboard]       │
└──────────────────────────────────────┘
```

**Résumé du flux LEARN :**
1. Je choisis **combien de mots** → 2. Je découvre **une carte à la fois** → 3. **Mini-test après chaque carte** (si paramètre activé) → 4. Résultat final

### 3.4 Session de révision (REVIEW)

Je clique sur "Commencer la révision" :

#### Étape 0 — Je configure ma session

```
┌──────────────────────────────────────┐
│  📚 Révision                         │
│                                      │
│  Combien de mots réviser ?           │
│     ┌──────────────────────────┐     │
│     │         [ 20 ]           │     │
│     └──────────────────────────┘     │
│     (défaut : 20, max dispo : 35)    │
│                                      │
│  Types d'exercices :                 │
│  ☑ QCM (choix multiple)              │
│  ☑ Phrase à trou (fill the blank)    │
│  ☐ Traduction FR → EN               │
│  ☐ Traduction EN → FR               │
│  ☐ Association (match)              │
│                                      │
│  [✅ Commencer la révision]          │
└──────────────────────────────────────┘
```

- Je choisis **combien de mots** réviser cette session
- Je choisis **quels types d'exercices** je veux faire
- Par défaut : QCM + phrase à trou (les plus efficaces)

#### Étape 1 — Questions une par une

**Les mots les plus fragiles passent en premier (SRS). Un seul mot par question.**

```
Question 1/20 (QCM)
┌──────────────────────────────────────┐
│  Que signifie "run out" ?            │
│                                      │
│                                      │
│  ○ a) courir dehors                  │
│  ○ b) être à court de                │  ← bonne réponse
│  ○ c) déborder                       │
│  ○ d) s'enfuir                       │
│                                      │
│         [Valider]                    │
└──────────────────────────────────────┘

    ↓ Feedback ↓

┌──────────────────────────────────────┐
│  ✅ Correct !                        │
│  "run out = être à court de"         │
│  "We ran out of time"                │
│                                      │
│  Temps : 3.1s                        │
│  Confiance : [Facile] [Moyen] [Dur]  │
│                                      │
│         [⏭ Question suivante]        │
└──────────────────────────────────────┘
```

Les types d'exercices alternent aléatoirement selon ce que j'ai coché :

```
Question 7/20 (Phrase à trou)
┌──────────────────────────────────────┐
│  Complète la phrase :                │
│                                      │
│  "She needs to ______ her fear       │
│   of public speaking."               │
│                                      │
│  Indice : elle doit surmonter        │
│                                      │
│  Réponse : [____________________]    │
│                                      │
│         [Valider]                    │
└──────────────────────────────────────┘
```

```
Question 14/20 (Traduction FR → EN)
┌──────────────────────────────────────┐
│  Comment dit-on "être à court de"    │
│  en anglais ?                        │
│                                      │
│  Réponse : [____________________]    │
│                                      │
│         [Valider]                    │
└──────────────────────────────────────┘
```

#### Fin de session

```
┌──────────────────────────────────────┐
│  🎉 Révision terminée !              │
│                                      │
│  20 cartes révisées                  │
│  Score : 16/20 (80%)                 │
│  Temps moyen : 3.5s                  │
│                                      │
│  📈 Progression du jour              │
│  Avant :  3 mots fragiles            │
│  Après :  1 mot fragile              │
│                                      │
│        [🏠 Retour au Dashboard]       │
└──────────────────────────────────────┘
```

**Résumé du flux REVIEW :**
1. Je choisis **combien de mots** + **quels types d'exercices**
2. Questions **une par une**, les plus fragiles en priorité
3. Feedback après chaque réponse
4. Résultat final avec progression

### 3.5 Progression

Je peux voir :

- **Mon streak** : nombre de jours consécutifs
- **Ma courbe de maîtrise** : quels mots je maîtrise, lesquels je révise encore
- **Mes points faibles** : quels types d'erreurs je fais (confusion de sens, orthographe, etc.)
- **Mon historique** : sessions passées, scores, progression dans le temps

```ascii
┌──────────────────────────────────────┐
│  Mes points faibles                  │
│                                      │
│  🟥 Confusion de sens     ██████░ 70%│
│  🟨 Orthographe           ██░░░░░ 25%│
│  🟩 Temps de réponse      █░░░░░░  5%│
│                                      │
│  Les mots les + fragiles :           │
│  • get away with    ██░░░░  20%      │
│  • put up with      ███░░░  35%      │
│  • bring about      ████░░  45%      │
└──────────────────────────────────────┘
```

### 3.6 Bibliothèque

Je peux parcourir toutes les expressions, filtrer par tier (1/2/3), par tag, rechercher :

```
┌──────────────────────────────────────┐
│  🔍 Rechercher...                    │
│                                      │
│  Tiers : [Tous] [Tier 1] [Tier 2]   │
│                                      │
│  ┌──────────────────────────────┐    │
│  │ 🖼️ get over    ★★★★☆  85%  │    │
│  │ 🖼️ run out     ★★★☆☆  45%  │    │
│  │ 🖼️ turn up    ★★☆☆☆  30%  │    │
│  │ ...                          │    │
│  └──────────────────────────────┘    │
│                                      │
│  Chaque ligne est cliquable pour     │
│  voir le détail + l'image + les      │
│  exemples.                           │
└──────────────────────────────────────┘
```

---

## 4. Comment le client utilisera l'appli au quotidien

### 4.1 Rythme typique

```
Matin (café, téléphone)
└── 5 min : révision des mots du jour (review)

Soir (PC)
└── 10 min : apprendre 5 nouveaux mots (learn)
└── 5 min  : re-révision rapide

Avant coucher (téléphone)
└── 2 min  : vérifier le streak, voir la progression
```

### 4.2 Contexte d'utilisation

- **Chez moi** : sur PC (Ubuntu, brave), via `http://192.168.x.x:8000`
- **Dans le canapé** : sur téléphone (Android, même réseau local), QR code scanné une fois
- **Pas de création de compte externe** : pas de Google, pas de email validation

### 4.3 Règle d'or de l'expérience

> **Moins de friction que de ne pas ouvrir l'appli.**

- Si j'ouvre l'appli, je dois pouvoir commencer à réviser en moins de 2 clics
- Pas de chargement inutile (le SRS est pré-calculé)
- Pas de décisions à prendre (l'appli sait ce que je dois réviser)
- Le dashboard me dit exactement ce qu'il reste à faire

---

## 5. Critères de succès (du point de vue client)

### 5.1 Critères impératifs

| # | Critère | Mesure |
|---|---------|--------|
| 1 | Je retiens les phrasal verbs sur le long terme | Mastery score > 80% après 3 mois |
| 2 | Je ne perds jamais ma progression | Backup automatique, pas de perte de données |
| 3 | L'appli est utilisable sur téléphone et PC | Interface responsive, QR code |
| 4 | Je peux réviser même sans internet | Tout est local (sauf génération IA) |
| 5 | L'image mentale m'aide à retenir | Je reconnais le phrasal verb en voyant l'image |
| 6 | Le système s'adapte à mon rythme | Si je fais des erreurs, je vois plus souvent le mot |

### 5.2 Critères de confort

| # | Critère | Pourquoi |
|---|---------|----------|
| 1 | Streak visible et motivant | La gamification me fait revenir |
| 2 | Temps de réponse < 1s entre les cartes | La fluidité évite l'abandon |
| 3 | Pas plus de 30 min par jour | Si c'est plus long, je vais arrêter |
| 4 | Les images sont cohérentes entre elles | Même style = moins de distraction cognitive |
| 5 | L'URL locale est facile à trouver | QR code ou fichier url.txt |

### 5.3 Ce qui n'est PAS un critère de succès

- ❌ Avoir 10 000 expressions dans la base
- ❌ Une interface "moderne" avec animations complexes
- ❌ Des statistiques avancées que personne ne regarde
- ❌ Un classement ou du social
- ❌ Une version mobile native (le web responsive suffit)

---

## 6. Contre-exemples : ce que le client ne veut PAS

| Scénario | Pourquoi c'est un échec |
|----------|------------------------|
| L'image contient du texte | Je lis le texte au lieu de mémoriser l'image → pas d'ancrage visuel |
| L'appli est lente à charger | Je ferme et je reviens plus tard → le streak est cassé |
| Je perds mon streak à cause d'un bug | Je suis démotivé, je ne reviens pas |
| Je dois deviner quel bouton cliquer | La friction fait que j'abandonne la session |
| Les révisions sont aléatoires | Je vois des mots que je connais déjà → ennui |
| Je vois des mots que je n'ai jamais appris en révision | Je me sens perdu, je ne sais plus où j'en suis |
| L'image ne représente pas bien le sens | Je suis confus, j'apprends mal |
| Pas moyen d'utiliser sur téléphone | Je ne peux pas réviser dans le canapé → sessions sautées |

---

## 7. Parcours utilisateur complet (User Journey)

```
DÉCOUVERTE
  ┌─ Je clone le dépôt sur mon T460
  ├─ Je lance `docker compose up` (ou systemd)
  ├─ Je scanne le QR code avec mon téléphone
  └─ Je crée mon compte

JOUR 1
  ┌─ Dashboard : 0 streak, 0 mot appris
  ├─ J'apprends 5 mots (get over, run out, turn up, give up, break down)
  ├─ Je vois les images → je les associe aux sens
  └─ Quiz : je valide ma compréhension

JOUR 2
  ┌─ Dashboard : 🔥 1 jour de streak, 5 mots en cours
  ├─ Je révise les 5 mots d'hier
  ├─ J'en apprends 3 nouveaux
  └─ Memory Engine ajuste : "run out" → difficile → revoir demain

JOUR 7
  ┌─ Streak : 7 jours 🔥🔥🔥
  ├─ 23 mots en cours, 5 maîtrisés
  ├─ Review priorise "get away with" (fragile)
  └─ Je commence à utiliser "get over" dans mes phrases en anglais

JOUR 30
  ┌─ Streak : 30 jours 🔥
  ├─ 40 mots maîtrisés, 30 en cours
  ├─ Les mots les plus faciles sont espacés à 1 semaine
  └─ Je ne les oublie plus

MOIS 3
  ┌─ 100+ mots maîtrisés
  ├─ Intervalle > 1 mois pour les mots consolidés
  ├─ Je regarde une série en VO et j'entends "run out of"
  └─ Je comprends instantanément → l'appli a fonctionné
```

---

## 8. Contraintes non-négociables

| Contrainte | Pourquoi |
|------------|----------|
| **Aucun abonnement** | C'est mon appli, j'héberge chez moi |
| **Image sans texte** | Principe pédagogique fondamental |
| **Performance sur T460** | 16GB RAM, i5-6300U, SSD |
| **Langue = français → anglais** | Mon cerveau pense en français |
| **Dépendance internet partielle** | Seule la génération IA (DeepSeek) nécessite internet — le cœur SRS et les quiz fonctionnent hors-ligne |

---

## 9. Récit utilisateur (user stories)

```
En tant qu'apprenant, je veux :

U1.  ...me connecter avec email + mot de passe
U2.  ...voir mon tableau de bord avec mon streak et mes révisions du jour
U3.  ...apprendre N nouveaux mots par jour avec image + sens + exemples
U4.  ...réviser les mots que je risque d'oublier (SRS)
U5.  ...voir une image qui représente chaque expression (sans texte)
U6.  ...répondre à des quiz (QCM, phrase à trou, traduction)
U7.  ...voir ma progression (courbe de maîtrise, points faibles)
U8.  ...paramétrer le nombre de nouveaux mots par jour
U9.  ...utiliser l'appli sur mon téléphone sur le même réseau
U10. ...parcourir la bibliothèque des expressions
U11. ...rechercher une expression spécifique
U12. ...ne jamais perdre ma progression
U13. ...utiliser l'appli sans connexion internet
U14. ...voir le détail d'une expression (image, sens, exemples, erreurs fréquentes)
U15. ...choisir combien de mots apprendre à chaque session d'apprentissage
U16. ...choisir combien de mots réviser ET quels types d'exercices à chaque session de révision
U17. ...voir UNE SEULE carte à la fois pendant l'apprentissage (pas de distraction)
U18. ...pouvoir activer/désactiver le mini-test après chaque carte dans les paramètres
U19. ...choisir combien de mots apprendre, combien réviser, et quels exercices à chaque session
```

---

## 10. Vérification d'alignement

Avant de livrer chaque phase, vérifier :

```
□ L'appli se lance avec une commande (ou docker compose up)
□ QR code s'affiche dans le terminal
□ Je peux créer un compte
□ Dashboard affiche mon état actuel
□ Je peux apprendre un nouveau mot (image + texte + quiz)
□ Je peux réviser (carte → réponse → feedback)
□ Le SRS adapte les intervalles
□ Je vois ma progression
□ L'image ne contient pas de texte
□ Tout fonctionne sur téléphone (LAN)
□ Aucune donnée personnelle n'est envoyée à l'extérieur ( sauf generation de question par appel API )
□ Les backups sont automatisés
□ **Je choisis combien de mots apprendre avant chaque session d'apprentissage**
□ **Je choisis combien de mots réviser + les types d'exercices avant chaque révision**
□ **Pendant l'apprentissage, une seule carte à la fois — mini-test optionnel après chaque carte (paramètre)**
□ **Le paramètre mini-test est dans les settings — pas forcé**
```

**Si une seule de ces cases est rouge, le projet n'est pas livrable.**
