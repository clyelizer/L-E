# learnEnglish — Pipeline & Corpus

> Application personnelle adaptative de consolidation linguistique
> Basée sur mémoire dynamique + répétition espacée (SRS) + génération contrôlée par IA

---

## 1. Philosophie & Principes fondateurs

```
┌──────────────────────────────────────────────────┐
│ Frontend  = AFFICHAGE uniquement                  │
│ Backend   = LOGIQUE                               │
│ PostgreSQL = VÉRITÉ (source of truth)             │
│ AI        = GÉNÉRATION uniquement, jamais mémoire  │
│ Image     = ANCRE VISUELLE (jamais de texte)       │
└──────────────────────────────────────────────────┘
```

### 1.1 Séparation stricte image/texte

| Principe | Pourquoi |
|----------|----------|
| **Image sans texte** | L'image ne contient jamais d'information linguistique. Elle ne fait que la renforcer. |
| **Texte = DB uniquement** | Le sens, la traduction, les exemples viennent exclusivement de PostgreSQL. |
| **Double codage** | Image → mémoire visuelle pure. Texte → mémoire sémantique. Les deux canaux sont distincts. |

### 1.2 Contraintes fondamentales

| Règle | Explication |
|-------|-------------|
| **L'IA ne touche pas à la mémoire** | Elle reformule, génère, enrichit. Le `mastery_score`, l'historique, l'oubli sont déterministes (SRS). |
| **Frontend = client léger** | Zéro logique métier côté navigateur. JSON → affichage → réponse. |
| **SRS déterministe** | Algorithme SM-2 codé en dur, paramétrable, reproductible. Pas d'IA dans le moteur mémoire. |
| **Tout est traçable** | Chaque réponse, erreur, révision est horodatée et conservée. |
| **Image ne porte pas le sens** | Elle renforce un sens déjà stocké ailleurs. Si tu inverses ça, le système devient fragile et dépendant du modèle. |

---

## 2. Pipeline global — 3 phases

```
PHASE 1                    PHASE 2                     PHASE 3
┌──────────────┐          ┌───────────────┐           ┌──────────────┐
│  CORPUS      │ ──────→  │  IA TEXTUELLE │ ────────→ │  IMAGES      │
│  expressions │          │  DeepSeek v4 Flash│        │  batch       │
│  figé        │          │  → JSON       │           │  pipeline    │
│  tiers 1-3   │          │  → DB         │           │  script      │
└──────────────┘          └───────────────┘           └──────────────┘
       │                         │                           │
       │ validation               │ validation                │ validation
       │ manuelle                 │ automatique               │ qualité
       ▼                         ▼                           ▼
    corpus figé              fiches en DB               images stockées
```

### 2.1 Règles strictes du pipeline

1. **Le corpus est figé avant toute génération IA** — sinon perte de cohérence
2. **L'IA remplit un schéma strict** (JSON validé par Pydantic) — pas de liberté
3. **Validation intermédiaire entre chaque phase** — sanity checks
4. **Génération d'images = script batch déterministe** — pas interactif

### 2.2 Séparation des responsabilités

```
Couche        → Rôle
──────────────────────────────
Corpus        → fixe (défini manuellement)
IA            → enrichit (génération contrôlée)
DB            → source de vérité (stockage)
Images        → représentation visuelle (illustration uniquement)
Frontend      → affichage (consomme DB)
```

---

## 3. Phase 1 — Corpus

### 3.1 Structure du corpus

```
corpus = {
  "tier1": ["get_up", "get_over", ...],     # ultra-fréquents
  "tier2": ["turn_on", "look_up", ...],     # très fréquents
  "tier3": ["call_off", "pick_up", ...]     # fréquents
}
```

Le corpus est une liste plate d'expressions, organisée en 3 tiers de priorité d'apprentissage.

### 3.2 Convention de notation

```
✓ = sens encore lisible depuis la logique spatiale (get_up → se lever)
✗ = sens figé à mémoriser (get_away_with → faire sans punition)
```

---

### 3.3 Tier 1 — Ultra-fréquents (priorité absolue)

**GET** — 20 expressions

| Phrasal verb | Sens | Logique |
|---|---|---|
| get up | se lever | ✓ |
| get down | s'abaisser / déprimer | ✓ |
| get on | monter dans / s'entendre avec | ✓ |
| get off | descendre de / s'en tirer | ✓ |
| get out | sortir / quitter | ✓ |
| get in | entrer / rentrer | ✓ |
| get over | surmonter / se remettre de | ✓ |
| get through | traverser une épreuve / joindre qqn | ✓ |
| get away | s'échapper | ✓ |
| get away with | faire sans être puni | ✗ |
| get back | revenir / récupérer | ✓ |
| get back to | reprendre contact | ✓ |
| get along | s'entendre avec qqn | ✓ |
| get around | contourner / circuler | ✓ |
| get at | vouloir dire / sous-entendre | ✗ |
| get by | se débrouiller | ✗ |
| get rid of | se débarrasser de | ✗ |
| get together | se réunir | ✓ |
| get ahead | progresser | ✓ |
| get behind | prendre du retard | ✓ |

**TAKE** — 15 expressions

| Phrasal verb | Sens | Logique |
|---|---|---|
| take off | décoller / enlever | ✓ |
| take on | accepter / embaucher | ✓ |
| take out | sortir / emmener | ✓ |
| take up | commencer / occuper l'espace | ✓ |
| take down | noter / démolir | ✓ |
| take over | reprendre le contrôle | ✓ |
| take in | comprendre / absorber / héberger | ✓ |
| take back | reprendre / rétracter | ✓ |
| take away | emporter / retirer | ✓ |
| take after | ressembler à (parent) | ✗ |
| take apart | démonter | ✓ |
| take care of | s'occuper de | ✓ |
| take place | avoir lieu | ✗ |
| take turn | se relayer | ✗ |
| take it out on | passer ses nerfs sur | ✗ |

**PUT** — 12 expressions

| Phrasal verb | Sens | Logique |
|---|---|---|
| put on | mettre (vêtement) / allumer | ✓ |
| put off | reporter / dégoûter | ✓ |
| put out | éteindre / publier | ✓ |
| put up | afficher / loger / construire | ✓ |
| put up with | tolérer / supporter | ✗ |
| put down | poser / noter / critiquer | ✓ |
| put back | remettre en place | ✓ |
| put away | ranger | ✓ |
| put aside | mettre de côté | ✓ |
| put through | connecter / faire subir | ✓ |
| put forward | proposer | ✓ |
| put across | communiquer / faire comprendre | ✓ |

**GO** — 14 expressions

| Phrasal verb | Sens | Logique |
|---|---|---|
| go on | continuer / se passer | ✓ |
| go off | exploser / sonner / se gâter | ✓ |
| go out | sortir / s'éteindre | ✓ |
| go over | réviser / vérifier | ✓ |
| go through | traverser / vivre difficile | ✓ |
| go back | retourner | ✓ |
| go ahead | y aller / commencer | ✓ |
| go down | descendre / baisser | ✓ |
| go up | monter / augmenter | ✓ |
| go away | partir | ✓ |
| go along with | accepter / suivre | ✓ |
| go around | circuler / suffire | ✓ |
| go without | se passer de | ✓ |
| go under | couler / faire faillite | ✓ |

**COME** — 13 expressions

| Phrasal verb | Sens | Logique |
|---|---|---|
| come up | surgir / se présenter | ✓ |
| come up with | trouver / inventer | ✗ |
| come across | tomber sur / paraître | ✓ |
| come out | sortir / être révélé | ✓ |
| come in | entrer / arriver | ✓ |
| come on | allez ! / progresser | ✓ |
| come off | se détacher / réussir | ✓ |
| come back | revenir | ✓ |
| come down | descendre / baisser | ✓ |
| come over | passer chez qqn / envahir | ✓ |
| come around | changer d'avis / reprendre connaissance | ✓ |
| come through | s'en sortir / arriver | ✓ |
| come from | venir de | ✓ |

**MAKE** — 8 expressions

| Phrasal verb | Sens | Logique |
|---|---|---|
| make up | inventer / se réconcilier | ✗ |
| make out | déchiffrer / prétendre | ✗ |
| make off | s'enfuir | ✓ |
| make up for | compenser | ✗ |
| make do with | se débrouiller avec | ✗ |
| make for | se diriger vers | ✓ |
| make of | penser de | ✗ |
| make it | réussir / y arriver | ✗ |

---

### 3.4 Tier 2 — Très fréquents

**TURN** — 10 expressions : turn on, turn off, turn up, turn down, turn out, turn back, turn around, turn into, turn over, turn away

**LOOK** — 11 expressions : look up, look down on, look out, look for, look after, look into, look forward to, look back, look over, look up to, look through

**BREAK** — 8 expressions : break down, break up, break out, break in, break through, break off, break away, break into

**GIVE** — 7 expressions : give up, give out, give in, give away, give back, give off, give over

**RUN** — 8 expressions : run out, run into, run away, run over, run through, run up, run off, run down

**BRING** — 8 expressions : bring up, bring out, bring back, bring down, bring in, bring off, bring about, bring forward

**HOLD** — 7 expressions : hold on, hold up, hold back, hold out, hold off, hold down, hold together

**KEEP** — 7 expressions : keep up, keep on, keep out, keep back, keep away, keep down, keep up with

**SET** — 7 expressions : set up, set off, set out, set back, set aside, set in, set down

---

### 3.5 Tier 3 — Fréquents

| Verbe | Expressions |
|-------|-------------|
| **CALL** | call off (annuler), call back (rappeler), call on (visiter / interpeller), call out (dénoncer), call up (appeler / mobiliser) |
| **PICK** | pick up (ramasser / apprendre), pick out (choisir), pick on (harceler), pick apart (décortiquer) |
| **PULL** | pull off (réussir), pull out (se retirer), pull through (s'en sortir), pull up (s'arrêter), pull down (démolir) |
| **FALL** | fall out (se disputer), fall through (échouer), fall behind (retard), fall apart (s'effondrer), fall for (amoureux / arnaque) |
| **WORK** | work out (entraîner / résoudre), work on (travailler sur), work up (développer), work through (surmonter) |
| **CUT** | cut off (couper / isoler), cut down (réduire), cut out (supprimer), cut back (réduire dépenses), cut in (interrompre) |
| **CARRY** | carry on (continuer), carry out (exécuter), carry over (reporter), carry away (emporter / enthousiasme) |
| **SHOW** | show up (se pointer), show off (se vanter), show around (faire visiter), show out (raccompagner) |
| **STAND** | stand up (lever / poser lapin), stand out (distinguer), stand by (soutenir), stand for (représenter), stand down (retirer) |
| **PASS** | pass out (évanouir / distribuer), pass on (transmettre), pass by (passer devant), pass up (laisser passer) |

---

## 4. Phase 2 — Génération IA textuelle

### 4.1 Principe

L'IA reçoit une **expression fixe** du corpus et produit une **fiche structurée** (JSON validé). Elle ne choisit pas les expressions, ne modifie pas le corpus.

### 4.2 Schéma de sortie obligatoire

```json
{
  "expression": "get over",
  "meaning_fr": "surmonter (une difficulté émotionnelle ou physique)",
  "metaphor": "traverser un mur émotionnel — passer de l'autre côté d'un obstacle",
  "part_of_speech": "phrasal verb",
  "difficulty": 3,
  "frequency_score": 85,
  "synonyms": ["recover from", "move past"],
  "examples": [
    "It took her months to get over the breakup.",
    "I finally got over my fear of public speaking."
  ],
  "common_errors": ["get over of (incorrect)", "get over it → get over him/her"],
  "tags": ["phrasal_verb", "emotion", "tier1"]
}
```

### 4.3 Validation automatique

Avant stockage en DB :

```python
checks = [
    expression non vide ET identique à l'input,
    meaning_fr non vide,
    metaphor non vide (utilisé pour prompt image),
    examples >= 2,
    tags non vides,
    difficulty entre 1 et 5,
    no hallucination (expression inchangée)
]
```

### 4.4 Prompt IA textuel — template

```
Tu es un lexicographe spécialisé dans l'enseignement de l'anglais.

Pour l'expression figée suivante : "{expression}"
(Sens : {meaning}, niveau : {tier})

Génère une fiche complète au format JSON avec :
- meaning_fr : définition précise
- metaphor : une métaphore mentale pour visualiser le sens (critique pour la génération d'image)
- synonyms : 1-3 synonymes
- examples : 2-4 phrases d'exemple naturelles
- common_errors : erreurs fréquentes des francophones
- difficulty : 1-5
- tags : mots-clés pertinents

Contraintes :
- L'expression ne doit pas être modifiée
- Les exemples doivent être en anglais courant
- La métaphore doit être visuelle et concrète (pas abstraite)
- Pas d'hallucination — ne pas inventer de sens qui n'existe pas

Réponds UNIQUEMENT en JSON valide.
```

---

## 5. Phase 3 — Génération d'images batch

### 5.1 Principe

Une fois les fiches stabilisées en DB, un script batch génère les images déterministiquement :

```
for each expression in DB where image IS NULL:
    metaphor = get_metaphor(expression)
    prompt = build_image_prompt(expression, metaphor, meaning_fr)
    image = call_image_api(prompt)
    save(f"images/{expression.slug}_v1.png")
    update DB row: images.path, images.prompt_used
```

### 5.2 Convention de nommage

```
get_over_v1.png
run_out_v1.png
put_up_with_v1.png
```

Versioning `_v1` permet de régénérer sans conflit si le prompt est amélioré.

### 5.3 Prompt image — template système

```
You are generating a pedagogical memory image for language learning.

TASK:
Create a single, clear, symbolic illustration of the phrasal verb: "{expression}".

LINGUISTIC MEANING:
- English: {expression}
- French meaning: {meaning_fr}

MENTAL MODEL (CRITICAL):
{metaphor}

VISUAL REQUIREMENTS:
- No text in the image — no letters, no words, no symbols
- One central scene only
- Simple composition (not crowded)
- Strong visual metaphor
- Easy to understand in less than 2 seconds
- Emotionally expressive but minimalistic
- Focus on clarity of action

STYLE:
- Semi-realistic illustration
- Soft lighting, high contrast
- Clean background
- Educational visual style (not artistic abstraction)

COMPOSITION RULES:
- One main subject (human figure or object)
- One main obstacle / concept
- Clear directional movement (left→right or bottom→top)
- No extra objects that distract meaning

GOAL:
The image must help a learner instantly associate:
"{expression}" → "{meaning_fr}"
```

### 5.4 Exemple complet

```
Expression : "run out"
Meaning     : "être à court de"
Metaphor    : "un réservoir qui se vide jusqu'à être complètement vide"

MENTAL MODEL:
A container of fuel or resources is being actively depleted
until it becomes completely empty. The liquid or energy
visibly disappears, leaving an empty container.

GOAL:
run out → être à court de
```

### 5.5 Script batch — pseudo-code

```python
def generate_all_images(db_session, image_api_client):
    expressions = db_session.query(Expression).filter(Expression.image_path == None).all()

    for expr in expressions:
        metaphor = expr.metaphor
        prompt = build_prompt(expr.text, expr.meaning_fr, metaphor)

        try:
            image_data = image_api_client.generate(prompt)
            filename = f"{slugify(expr.text)}_v1.png"
            filepath = IMAGE_DIR / filename
            filepath.write_bytes(image_data)

            # Enregistrer en DB
            image_record = Image(
                expression_id=expr.id,
                path=str(filepath),
                prompt_used=prompt,
                version=1
            )
            db_session.add(image_record)

        except APIError:
            log.error(f"Échec génération image: {expr.text}")
            continue

        # Rate limiting
        time.sleep(1)

    db_session.commit()
```

### 5.6 Validation des images

- Vérifier que l'image n'est pas vide / corrompue
- Vérifier dimensions minimales (512x512)
- Optionnel : détection de texte dans l'image (OCR) — rejeter si texte détecté
- Log manuel des images ambiguës

---

## 6. Résumé des dépendances entre phases

```
Phase 1 (Corpus)
    │
    ▼
Phase 2 (IA textuelle) ──nécessite──> Phase 1 figée
    │
    ▼
Phase 3 (Images batch) ──nécessite──> Phase 2 stockée en DB
    │
    ▼
Runtime (Frontend) ──lit──> DB + images
```

**Règle d'or :** Chaque phase dépend de la précédente. On ne génère pas d'image avant d'avoir la métaphore. On ne génère pas de fiche avant d'avoir le corpus figé.
