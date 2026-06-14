---
name: client-requirements
description: Write and maintain a client requirements document as the single source of truth for a project, with explicit UX flows and an alignment checklist.
source: auto-skill
extracted_at: '2026-06-14T15:54:44.942Z'
---

# Client Requirements Document — Single Source of Truth

Use this skill when you need to capture, structure, or refine a client requirements document for any project (app, service, tool). The document serves as the **source of truth** — if the final result does not align with it, the project is a failure.

## 1. Document Structure

Create a single `.md` file with these sections in order:

| # | Section | Purpose |
|---|---------|---------|
| 1 | **Problème** | What problem does this solve? Why does the client need it? |
| 2 | **Besoin** | What the client needs, expressed as a feature table (function → what it does → why it matters) |
| 3 | **UX / Wireframes** | Step-by-step ASCII wireframes showing exactly what the client sees and does. **No hand-wavy descriptions** — every button, every screen transition must be explicit. |
| 4 | **Utilisation quotidienne** | Walk through a typical day using the product |
| 5 | **Critères de succès** | How will we know it works? Measurable outcomes. |
| 6 | **Anti-patterns** | What NOT to do — things the client explicitly rejected or that break the core promise |
| 7 | **Parcours utilisateur** | Day 1, Day 7, Day 30, Month 3 — how the user's experience evolves |
| 8 | **Contraintes non-négociables** | Hardware, network, offline, cost, privacy — anything the client will not compromise on |
| 9 | **User stories** | Numbered list (`U1..Un`) of "En tant que..., je veux..." |
| 10 | **Checklist d'alignement** | Checkboxes that must ALL be green before delivery. If one is red, the project is not deliverable. |

## 2. Writing UX Flows — Explicit Step-by-Step

When writing UX sections (section 3), do NOT write vague descriptions like "the user sees cards and interacts with them." Instead:

1. **Break every flow into numbered steps** (Étape 0, Étape 1, ...)
2. **Step 0 = Configuration** — what does the user choose before starting?
   - Always give the user control over **quantity** (combien de mots ? combien de cartes ?)
   - Optionally give control over **type** (quels types d'exercices ? quels modes ?)
   - Show the default value and the maximum available
3. **Discovery vs Testing = two distinct phases** — never mix them:
   - **Étape 1 (Discovery)** : pure exposition — one item per screen, no quiz, no test. The user just reads, looks at images, clicks "Next".
   - **Étape 2 (Mini-test)** : all items from Step 1 are tested at the END, one question at a time
4. **Each step shows exactly one screen** as ASCII block art:
   - The title/header
   - The content (image, text, input fields)
   - Every button/link with its action
   - Feedback/validation states
5. **Show the transition** between steps (e.g. `↓ après avoir cliqué ↓`)
6. **The final step = results screen** with summary of what happened

Rule: **"Un seul élément à la fois"** — during any linear sequence (learning, reviewing, filling a form), show only ONE item per screen. The user clicks "next" to advance. No quiz or test appears during the discovery phase — only at the end.

### Template for a Configuration step (Étape 0)

```
┌──────────────────────────────────────┐
│  ✨ Title (action the user takes)    │
│                                      │
│  Combien de [items] aujourd'hui ?    │
│     ┌──────────────────────────┐     │
│     │         [ 5 ]            │     │
│     └──────────────────────────┘     │
│     (défaut : 5, max dispo : 12)     │
│                                      │
│  [Options if applicable] :           │
│  ☑ Option A (défaut)                 │
│  ☑ Option B (défaut)                 │
│  ☐ Option C                          │
│                                      │
│  [✅ Commencer]                      │
└──────────────────────────────────────┘
```

### Template for a Discovery step (Étape 1)

```
Carte 1/N
┌──────────────────────────────────────┐
│                                      │
│  ┌────────────────────────────┐      │
│  │      🖼️ IMAGE              │      │
│  └────────────────────────────┘      │
│                                      │
│  [word / concept]                    │
│  = [meaning / definition]            │
│                                      │
│  "[example sentence]"                │
│                                      │
│        [⏭ Suivant →]                │
└──────────────────────────────────────┘
```

### Template for a Mini-test step (Étape 2)

```
Question 1/N
┌──────────────────────────────────────┐
│  Que signifie "[word]" ?             │
│                                      │
│  ○ a) wrong answer 1                 │
│  ○ b) correct answer                 │  ← bonne réponse
│  ○ c) wrong answer 2                 │
│  ○ d) wrong answer 3                 │
│                                      │
│         [Valider]                    │
└──────────────────────────────────────┘
```

### Template for a Results step (final)

```
┌──────────────────────────────────────┐
│  🎉 Session terminée !               │
│                                      │
│  N items [action]                    │
│  Score : X/N (XX%)                   │
│  Temps moyen : X.Xs                  │
│                                      │
│        [🏠 Retour au Dashboard]       │
└──────────────────────────────────────┘
```

## 3. Client Validation Loop

After writing the first draft:

1. **Send to the client** — ask specifically: "Qu'est-ce qui manque ? Qu'est-ce qui n'est pas assez explicite ?"
2. **Clients will identify missing details** — they know their own workflow better than anyone
3. **Every gap the client finds must be filled with more explicit text** (not hand-waved)
4. **Propagate the change everywhere**: if you add a feature or flow, add it to:
   - The correct UX section (with full step-by-step)
   - The user stories (as one or more new `U#` items)
   - The alignment checklist (as new checkboxes)
   - The feature table / needs table
5. **Repeat** until the client confirms it's complete

## 4. Alignment Checklist Rules

- Each checkbox represents a **verifiable, binary pass/fail criterion**
- Write them as **first-person statements** the client can say: "Je peux X", "Je choisis Y", "Z se passe automatiquement"
- Bold the most critical ones (`**...**`)
- Beneath the checklist, write: **"Si une seule de ces cases est rouge, le projet n'est pas livrable."**

## 5. Propagation Rule

Whenever you modify the document for a new requirement or gap:

| If you change | Also update |
|---------------|-------------|
| UX section (3.x) | User stories (9) + Checklist (10) + Needs table (2) |
| User stories (9) | UX section (3.x) + Checklist (10) |
| Needs table (2) | UX section (3.x) + User stories (9) |
| Checklist (10) | Verify all listed features exist in UX sections |

This prevents drift — every feature appears in the requirements, the stories, and the verification checklist.

## 6. Coherence Verification Pass

After updating the requirements document, **cross-check all technical documents** against the new requirements. Systematic verification:

1. **Open each tech doc** (pipeline, backend, frontend, deployment, architecture)
2. **For each new/explicit requirement**, ask:
   - Is there a route/endpoint that supports this? (backend)
   - Is there a component/page that renders this? (frontend)
   - Is there a database field or schema that stores this? (DB)
   - Is there a pipeline step that generates this? (pipeline)
   - Is the roadmap up to date with the new flow? (deployment)
3. **Mark each finding**:
   - ✅ Cohérent — requirement is fully supported
   - ⚠️ Ambigü — partially supported, needs clarification
   - ❌ Manquant — not mentioned or contradicts the requirement
4. **Fix all ❌ before coding** — update the tech docs to reflect the requirement

### Verification dimensions — exhaustive per-document pass

When doing a rigorous coherence check, verify these specific dimensions across every document:

| Dimension | What to check | Doc types |
|-----------|---------------|-----------|
| **Functional flows** | Does the LEARN flow match step-for-step (config → discover → [mini-test] → results)? Does the REVIEW flow match (config + types → questions one by one, weakest first → feedback → results)? | frontend, backend, requirements |
| **Data models / DB schema** | Every field in the requirements (e.g., `mini_test_enabled`) must exist in the DB table spec. Check column types, defaults, constraints. | backend, requirements |
| **API contracts** | Every route that supports a user flow must have documented body params. E.g., `POST /learning/start` must accept `{ word_count: int }`. Missing body params = ❌. | backend |
| **Frontend component tree** | Every config step, session page, and result page from the UX flow must have a named component. E.g., LearnConfigPage, LearnSessionPage, LearnMiniTestCard, LearnCompletePage. | frontend, requirements |
| **User story mapping** | Map each U# story to concrete implementation: which route? which component? which DB field? All must be traceable. | all docs |
| **Environment variables** | LLM model names, providers, paths must be identical across all docs. E.g., `deepseek-v4-flash` vs `deepseek-v4` is a drift. | pipeline, backend, frontend |
| **Roadmap** | The execution phases must describe the exact flow, not an outdated version. E.g., if the flow changed from "carte → quiz → feedback" to "découverte → [mini-test]", the roadmap text must be updated. | frontend/deployment |
| **Pseudo-code / algorithms** | Every variable referenced must be defined in the function scope. Check for dangling references like undefined `quality` or `total` in SM-2 formulas. | backend |
| **Section symmetry** | If the requirements document relaxes a constraint (e.g., removes "internet-free"), the constraint table (section 8) must be updated to reflect the new decision. | requirements only |

### Structured reporting format

Format each finding with a clear label:

```
### Anomalie N — Titre court

**Fichier :** `nom_du_fichier.md` §section

**Problème :** Description concise du décalage

**Correctif :** Action exacte à prendre
```

Then classify:
- 🔴 **BLOCKER** — bloque le développement, doit être corrigé avant de coder
- 🟡 **Mineure** — clarification ou documentation, pas bloquant

### Applying fixes systematically

1. Read each target file's exact current content before editing
2. Apply edits to ALL affected documents in parallel (independent edits)
3. For each fix, trace the **propagation**: changing a UX flow may require changes to routes, components, DB fields, roadmap, user stories, and checklist
4. Verify the fixes by re-reading the changed sections

### Common gaps found after requirements changes

| Client change | Typical tech gaps |
|---------------|------------------|
| User configures count per session | Routes `POST /start` missing body params for `word_count`; frontend missing config step component |
| User chooses exercise types per session | Routes `POST /start` missing body params for `exercise_types`; DB may need session-level config storage |
| "One card at a time, mini-test at end" | Roadmap says "card → quiz → feedback" (wrong); frontend needs separate Discovery phase and Mini-test phase |
| Constraints relaxed (API call allowed) | Tech docs still mention old constraints; deployment env vars need to match actual provider/model |
| New parameter added (e.g., `mini_test_enabled`) | Missing in DB `user_settings` table; missing in frontend Settings page; missing in PUT /settings route documentation |
| Model/provider name changed | `.env.example` outdated; pipeline doc still references old model; deployment env vars inconsistent |
| SM-2 or algorithm details refined | Pseudo-code may reference undefined variables; bonus/malus logic may contradict the algorithm description |
