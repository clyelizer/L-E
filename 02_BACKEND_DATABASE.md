# learnEnglish — Backend & Base de Données

---

## 1. Stack technique

| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| Langage | **Python 3.12+** | Maturité, écosystème IA/ML |
| API | **FastAPI** | Async natif, validation Pydantic, docs auto |
| ASGI | **Uvicorn** | Standard FastAPI |
| ORM | **SQLAlchemy 2.0** | Async, mature |
| Migrations | **Alembic** | Standard SQLAlchemy |
| DB | **PostgreSQL 16** | JSONB, FULLTEXT, fiable |
| Cache | **Redis** (optionnel) | Cache réponses LLM, sessions |
| LLM Client | **DeepSeek v4 Flash** | Génération textuelle |

---

## 2. Architecture backend

### 2.1 Arborescence

```
app/
├── main.py                       # Entrypoint FastAPI, lifespan, CORS
├── core/
│   ├── config.py                 # Settings Pydantic (.env)
│   ├── database.py               # Engine, AsyncSession
│   ├── dependencies.py           # get_db, get_current_user
│   └── security.py               # bcrypt, JWT
│
├── models/                       # SQLAlchemy ORM
│   ├── base.py                   # Declarative base, TimestampMixin
│   ├── user.py                   # User, UserSettings
│   ├── expression.py             # Expression, Tag, ExpressionTag
│   ├── image.py                  # Image (NOUVEAU)
│   ├── memory.py                 # UserMemory (SRS state)
│   ├── session.py                # StudySession, SessionAnswer
│   └── mistake.py                # Mistake
│
├── schemas/                      # Pydantic request/response
│   ├── auth.py
│   ├── user.py
│   ├── expression.py
│   ├── image.py                  # (NOUVEAU)
│   ├── memory.py
│   ├── session.py
│   ├── review.py
│   ├── quiz.py
│   └── progress.py
│
├── api/                          # Route handlers
│   ├── router.py
│   ├── auth.py
│   ├── users.py
│   ├── expressions.py
│   ├── images.py                 # (NOUVEAU — GET images)
│   ├── learning.py
│   ├── review.py
│   ├── quiz.py
│   ├── progress.py
│   └── ai.py
│
├── services/                     # Business logic
│   ├── auth_service.py
│   ├── learning_service.py
│   ├── review_service.py
│   ├── progress_service.py
│   └── expression_service.py
│
├── engines/                      # Cœur algorithmique — déterministe
│   ├── memory_engine.py          # SM-2, mastery_score
│   ├── selection_engine.py       # Choix mots à réviser
│   ├── quiz_engine.py            # Génération questions
│   └── scheduling_engine.py      # Prochaines révisions
│
├── ai/                           # LLM isolé
│   ├── prompt_builder.py         # Templates prompts
│   ├── llm_client.py             # Client HTTP LLM
│   ├── generators/
│   │   ├── examples.py
│   │   ├── questions.py
│   │   ├── metaphor.py           # (NOUVEAU)
│   │   └── image_prompt.py       # (NOUVEAU)
│   └── validators/
│       └── response_validator.py # Validation Pydantic
│
├── tasks/                        # Tâches CRON
│   └── scheduler.py
│
└── utils/
    ├── scoring.py
    ├── time_utils.py
    └── logging_config.py
```

### 2.2 Dépendances strictes

```
api/ ──appelle──> services/ ──appelle──> engines/   (déterministe)
                    │                      │
                    └──appelle──> ai/      │
                                           │
models/ <──lit/écrit── engines/ <──────────┘
```

- `engines/` ne dépend jamais de `api/`, `services/`, ou `ai/`
- `services/` orchestre : appele `engines/` + `ai/`
- `ai/` est remplaçable (interface `LLMClient`)

---

## 3. Base de données — schéma complet

### 3.1 Diagramme ER

```
users ──1:1──> user_settings
  │
  ├──1:N──> user_memory ──N:1──> expressions
  │                                      │
  ├──1:N──> study_sessions               │
  │           │                          │
  │           └──1:N──> session_answers ──┘
  │                          │
  │                          └──1:N──> mistakes
  │
  └──1:N──> images ────────N:1──> expressions (NOUVEAU)
```

### 3.2 Tables

#### `expressions` (enrichie — nouveau champ `metaphor`)

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `text` | `VARCHAR(500)` | NOT NULL | Expression en anglais |
| `meaning` | `TEXT` | NOT NULL | Sens en français |
| **`metaphor`** | **`TEXT`** | **DEFAULT NULL** | **Métaphore mentale (pour prompt image)** |
| `part_of_speech` | `VARCHAR(30)` | DEFAULT NULL | Verb, noun, phrasal verb, idiom... |
| `difficulty` | `INTEGER` | CHECK 1-5, DEFAULT 3 | Difficulté |
| `frequency_score` | `DECIMAL(4,2)` | DEFAULT NULL | Fréquence corpus (0-100) |
| `example_sentence` | `TEXT` | DEFAULT NULL | Exemple |
| `notes` | `TEXT` | DEFAULT NULL | Notes |
| `source` | `VARCHAR(100)` | DEFAULT NULL | tier1, tier2, tier3 |
| `tags` | `TEXT[]` | DEFAULT {} | Tags |
| `tier` | `INTEGER` | CHECK 1-3 | Tier d'apprentissage |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | |

**Index** : GIN full-text sur `text`, GIN sur `tags`, BTREE sur `difficulty`

#### `images` (NOUVELLE TABLE)

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `expression_id` | `UUID` | FK → expressions.id, NOT NULL | Expression associée |
| `path` | `VARCHAR(500)` | NOT NULL | Chemin du fichier image |
| `prompt_used` | `TEXT` | NOT NULL | Prompt complet envoyé au modèle |
| `version` | `INTEGER` | DEFAULT 1 | Version de l'image |
| `width` | `INTEGER` | DEFAULT NULL | Dimensions |
| `height` | `INTEGER` | DEFAULT NULL | |
| `file_size_bytes` | `INTEGER` | DEFAULT NULL | Taille fichier |
| `hash_sha256` | `VARCHAR(64)` | DEFAULT NULL | Hash pour dédoublonnage |
| `is_active` | `BOOLEAN` | DEFAULT true | Image active (peut être désactivée si mauvaise qualité) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | |

**Index** : BTREE `(expression_id)`, BTREE `(expression_id, is_active)`, UNIQUE `(expression_id, version)`

#### `users`

| Colonne | Type | Contraintes |
|---------|------|-------------|
| `id` | `UUID` | PK |
| `email` | `VARCHAR(255)` | UNIQUE, NOT NULL |
| `username` | `VARCHAR(100)` | UNIQUE, NOT NULL |
| `password_hash` | `VARCHAR(255)` | NOT NULL |
| `is_active` | `BOOLEAN` | DEFAULT true |
| `created_at` | `TIMESTAMPTZ` | NOT NULL |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL |

#### `user_settings`

| Colonne | Type | Contraintes |
|---------|------|-------------|
| `id` | `UUID` | PK |
| `user_id` | `UUID` | FK → users.id, UNIQUE |
| `daily_new_words` | `INTEGER` | DEFAULT 5, CHECK > 0 |
| `daily_review_cap` | `INTEGER` | DEFAULT 50, CHECK > 0 |
| `question_types` | `TEXT[]` | DEFAULT {MCQ,FILL_BLANK,FR_TO_EN} |
| `difficulty_bias` | `VARCHAR(20)` | DEFAULT 'adaptive' |
| `ai_generation_enabled` | `BOOLEAN` | DEFAULT true |
| `native_language` | `VARCHAR(10)` | DEFAULT 'fr' |
| `mini_test_enabled` | `BOOLEAN` | DEFAULT false | Mini-test après chaque carte d'apprentissage (optionnel) |
| `timezone` | `VARCHAR(50)` | DEFAULT 'UTC' |
| `created_at` | `TIMESTAMPTZ` | |
| `updated_at` | `TIMESTAMPTZ` | |

#### `user_memory` (cœur SRS)

| Colonne | Type | Contraintes | Description |
|---------|------|-------------|-------------|
| `id` | `UUID` | PK | |
| `user_id` | `UUID` | FK → users.id | |
| `expression_id` | `UUID` | FK → expressions.id | |
| `mastery_score` | `DECIMAL(4,3)` | DEFAULT 0, CHECK 0-1 | Score de maîtrise |
| `interval` | `INTEGER` | DEFAULT 0, CHECK >= 0 | Intervalle (heures) |
| `ease_factor` | `DECIMAL(3,2)` | DEFAULT 2.50, CHECK 1.30-3.00 | Facteur facilité |
| `repetitions` | `INTEGER` | DEFAULT 0 | Réussites consécutives |
| `lapses` | `INTEGER` | DEFAULT 0 | Fois oublié |
| `last_reviewed_at` | `TIMESTAMPTZ` | DEFAULT NULL | |
| `next_review_at` | `TIMESTAMPTZ` | DEFAULT NULL | Prochaine révision |
| `first_seen_at` | `TIMESTAMPTZ` | NOT NULL | |
| `total_reviews` | `INTEGER` | DEFAULT 0 | |
| `correct_count` | `INTEGER` | DEFAULT 0 | |
| `incorrect_count` | `INTEGER` | DEFAULT 0 | |
| `streak` | `INTEGER` | DEFAULT 0 | |
| `max_streak` | `INTEGER` | DEFAULT 0 | |
| `avg_response_time_ms` | `INTEGER` | DEFAULT NULL | |
| `is_learning` | `BOOLEAN` | DEFAULT true | En apprentissage ? |
| `created_at` | `TIMESTAMPTZ` | | |
| `updated_at` | `TIMESTAMPTZ` | | |

**Contrainte** : UNIQUE `(user_id, expression_id)`
**Index** : BTREE `(user_id, next_review_at)`, BTREE `(user_id, mastery_score)`

#### `study_sessions`

| Colonne | Type | Contraintes |
|---------|------|-------------|
| `id` | `UUID` | PK |
| `user_id` | `UUID` | FK → users.id |
| `session_type` | `VARCHAR(20)` | NOT NULL, CHECK IN ('learn','review','mixed') |
| `status` | `VARCHAR(20)` | DEFAULT 'in_progress' |
| `score` | `DECIMAL(4,3)` | DEFAULT NULL |
| `total_questions` | `INTEGER` | DEFAULT 0 |
| `correct_answers` | `INTEGER` | DEFAULT 0 |
| `duration_seconds` | `INTEGER` | DEFAULT NULL |
| `started_at` | `TIMESTAMPTZ` | NOT NULL |
| `completed_at` | `TIMESTAMPTZ` | DEFAULT NULL |
| `created_at` | `TIMESTAMPTZ` | |

#### `session_answers`

| Colonne | Type | Contraintes |
|---------|------|-------------|
| `id` | `UUID` | PK |
| `session_id` | `UUID` | FK → study_sessions.id |
| `expression_id` | `UUID` | FK → expressions.id |
| `user_id` | `UUID` | FK → users.id |
| `question_type` | `VARCHAR(30)` | NOT NULL |
| `question_data` | `JSONB` | NOT NULL |
| `user_answer` | `TEXT` | DEFAULT NULL |
| `correct_answer` | `TEXT` | NOT NULL |
| `is_correct` | `BOOLEAN` | NOT NULL |
| `response_time_ms` | `INTEGER` | DEFAULT NULL |
| `hint_used` | `BOOLEAN` | DEFAULT false |
| `confidence` | `VARCHAR(10)` | DEFAULT NULL |
| `created_at` | `TIMESTAMPTZ` | |

#### `mistakes`

| Colonne | Type | Contraintes |
|---------|------|-------------|
| `id` | `UUID` | PK |
| `user_id` | `UUID` | FK → users.id |
| `expression_id` | `UUID` | FK → expressions.id |
| `error_type` | `VARCHAR(30)` | NOT NULL |
| `user_incorrect_answer` | `TEXT` | DEFAULT NULL |
| `context` | `JSONB` | DEFAULT NULL |
| `times_repeated` | `INTEGER` | DEFAULT 1 |
| `resolved` | `BOOLEAN` | DEFAULT false |
| `created_at` | `TIMESTAMPTZ` | |
| `updated_at` | `TIMESTAMPTZ` | |

#### Tables auxiliaires

**`tags`** : id (UUID PK), name (VARCHAR UNIQUE), description, color, created_at
**`expression_tags`** : expression_id (FK), tag_id (FK) — PK composite

---

## 4. API — Routes et contrats

### 4.1 Auth

| Méthode | Route | Description |
|---------|-------|-------------|
| `POST` | `/api/v1/auth/register` | Créer un compte |
| `POST` | `/api/v1/auth/login` | Connexion |
| `POST` | `/api/v1/auth/refresh` | Rafraîchir token |

### 4.2 Utilisateurs

| Méthode | Route |
|---------|-------|
| `GET/PUT` | `/api/v1/users/me` |
| `GET/PUT` | `/api/v1/users/me/settings` | GET : paramètres actuels. PUT : `{ daily_new_words?: int, daily_review_cap?: int, question_types?: string[], mini_test_enabled?: bool, ... }` |

### 4.3 Apprentissage

| Méthode | Route | Description | Body |
|---------|-------|-------------|------|
| `GET` | `/api/v1/learning/next` | Prochains nouveaux mots (quantité dispo) | — |
| `POST` | `/api/v1/learning/start` | Démarrer session LEARN | `{ word_count: int }` |
| `POST` | `/api/v1/learning/submit` | Soumettre réponse (mini-test) | `{ session_id, expression_id, answer, response_time_ms }` |
| `POST` | `/api/v1/learning/complete` | Terminer session | `{ session_id }` |

> **Note :** Le mini-test après chaque carte utilise la même mécanique que les quiz (QCM généré via `/api/v1/quiz/generate`, validé via `/api/v1/quiz/answer`). Si `mini_test_enabled` est `false`, la phase quiz est sautée et `POST /learning/submit` n'est pas appelé — on passe directement à la carte suivante.

### 4.4 Révision

| Méthode | Route | Description | Body |
|---------|-------|-------------|------|
| `GET` | `/api/v1/review/today` | Révisions disponibles aujourd'hui | — |
| `POST` | `/api/v1/review/start` | Démarrer session REVIEW | `{ word_count: int, exercise_types: string[] }` |
| `POST` | `/api/v1/review/submit` | Soumettre réponses | `{ session_id, expression_id, exercise_type, answer, response_time_ms }` |
| `POST` | `/api/v1/review/complete` | Terminer la session | `{ session_id }` |

### 4.5 Quiz

| Méthode | Route |
|---------|-------|
| `POST` | `/api/v1/quiz/generate` | Générer questions |
| `POST` | `/api/v1/quiz/answer` | Valider réponse |

### 4.6 Progrès

| Méthode | Route |
|---------|-------|
| `GET` | `/api/v1/progress/dashboard` |
| `GET` | `/api/v1/progress/history` |
| `GET` | `/api/v1/progress/mastery` |
| `GET` | `/api/v1/progress/weaknesses` |

### 4.7 Images (NOUVEAU)

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/api/v1/images/{expression_id}` | Récupérer l'image active d'une expression |
| `GET` | `/api/v1/images/{expression_id}/versions` | Lister les versions |
| `POST` | `/api/v1/images/{expression_id}/regenerate` | (Admin) Régénérer image |

### 4.8 Expressions (CRUD admin)

| Méthode | Route |
|---------|-------|
| `GET` | `/api/v1/expressions` | Liste paginée |
| `GET` | `/api/v1/expressions/{id}` | Détail (inclut image_path) |
| `POST` | `/api/v1/expressions` | Ajouter |
| `PUT` | `/api/v1/expressions/{id}` | Modifier |
| `DELETE` | `/api/v1/expressions/{id}` | Supprimer |

### 4.9 IA

| Méthode | Route | Description |
|---------|-------|-------------|
| `POST` | `/api/v1/ai/examples` | Générer exemples |
| `POST` | `/api/v1/ai/metaphor` | (NOUVEAU) Générer métaphore |
| `POST` | `/api/v1/ai/rephrase` | Reformuler |

---

## 5. Algorithme SRS (SM-2 modifié)

### 5.1 Paramètres

| Paramètre | Défaut | Description |
|-----------|--------|-------------|
| `new_words_per_day` | 5 | Nouveaux mots/jour |
| `reviews_per_day` | 20 | Révisions/jour |
| `initial_interval` | 1h | Premier intervalle |
| `second_interval` | 6h | Second intervalle |
| `graduating_interval` | 24h | Intervalle de sortie |
| `max_interval` | 365 jours | Maximum |
| `min_ease` | 1.3 | Ease factor min |
| `max_ease` | 3.0 | Ease factor max |

### 5.2 Algorithme

```
function update_memory(memory, answer):
    # Mise à jour compteurs
    memory.total_reviews += 1
    if answer.is_correct:
        memory.correct_count += 1
        memory.streak += 1
        memory.repetitions += 1
    else:
        memory.incorrect_count += 1
        memory.streak = 0
        memory.lapses += 1

    # Dériver la qualité (0-5) depuis is_correct + temps de réponse
    quality = 4 if answer.is_correct else 1
    if answer.is_correct and answer.response_time_ms < 3000:
        quality = 5

    # SM-2
    if answer.is_correct:
        if memory.repetitions == 1:      memory.interval = 1     # 1h
        elif memory.repetitions == 2:    memory.interval = 6     # 6h
        else:                            memory.interval = round(memory.interval * memory.ease_factor)
        memory.ease_factor += 0.1 - (5 - quality) * 0.08
    else:
        memory.repetitions = 0
        memory.interval = 1                                        # retour 1h
        memory.ease_factor = max(1.3, memory.ease_factor - 0.2)

    # Clamp ease_factor
    memory.ease_factor = clamp(memory.ease_factor, 1.3, 3.0)

    # Mastery score composite
    ratio = memory.correct_count / max(1, memory.correct_count + memory.incorrect_count)
    memory.mastery_score = ratio * (1 - exp(-memory.total_reviews / 5))

    # Bonus/malus temps de réponse
    if answer.is_correct and answer.response_time_ms < 3000:
        memory.ease_factor = min(3.0, memory.ease_factor + 0.05)
    elif answer.is_correct and answer.response_time_ms > 30000:
        memory.ease_factor = max(1.3, memory.ease_factor - 0.05)

    # Prochaine révision
    memory.next_review_at = now() + timedelta(hours=memory.interval)

    # Consolidation
    if memory.mastery_score >= 0.90 and memory.interval >= 720:
        memory.is_learning = False
```

### 5.3 Priorité de révision

```
priorité = (1 - mastery_score) * 0.5
         + age_relative * 0.3
         + error_rate_recent * 0.2
```

---

## 6. IA — Module LLM

### 6.1 Interface

```python
class LLMClient(ABC):
    async def generate_examples(self, expression, meaning, count=3) -> list[str]
    async def generate_metaphor(self, expression, meaning) -> str        # NOUVEAU
    async def generate_quiz_question(self, expression, meaning, type) -> QuizQuestion
    async def rephrase(self, expression, context=None) -> str
```

### 6.2 Cas d'usage

| Usage | Cache | Fallback |
|-------|-------|----------|
| Exemples | 7 jours | Exemples pré-écrits |
| Métaphore | 30 jours | Définition dictionnaire |
| Questions | Session | Engine déterministe |
| Reformulation | 30 jours | Phrase originale |

### 6.3 Rate limiting

```python
# Cache Redis ou mémoire
# Clé : f"ai:{type}:{expression}:{lang}"
# TTL : 7 jours (exemples), 30 jours (métaphores)
# Rate limit : 10 req/min
```

### 6.4 Validation des réponses (Pydantic)

```python
class LLMExamplesResponse(BaseModel):
    examples: list[LLMExample] = Field(..., min_length=1, max_length=5)

class LLMMetaphorResponse(BaseModel):                                  # NOUVEAU
    metaphor: str = Field(..., min_length=10, max_length=500)
    visual_elements: list[str] = Field(..., min_length=1)
```
