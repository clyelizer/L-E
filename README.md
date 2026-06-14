# learnEnglish — Adaptive Phrasal Verbs App

Une application adaptive pour l'apprentissage des *phrasal verbs* anglais, avec
répétition espacée (SM-2) et imagerie mentale générée par IA.

## Stack

| Couche       | Technologie                                             |
| ------------ | ------------------------------------------------------- |
| Backend      | Python 3.12+, FastAPI, Uvicorn                          |
| Base de données | PostgreSQL 16 (Docker), SQLAlchemy 2.0 async, Alembic |
| Authentification | JWT (access 15min + refresh 7 jours), bcrypt (cost=12) |
| Génération d'images | DeepSeek v4 Flash (LLM pour les métaphores) |

## Architecture

```
app/
├── core/        # Config, database, security, dependencies
├── models/      # SQLAlchemy ORM models
├── schemas/     # Pydantic request/response schemas
├── api/         # FastAPI route handlers
├── services/    # Business logic
├── engines/     # SM-2 SRS engine
├── ai/          # LLM integration
├── tasks/       # Background tasks
└── utils/       # Helpers
```

## Prérequis

- Docker (pour PostgreSQL)
- Python >= 3.12
- uv (ou pip)

## Installation

```bash
# 1. Cloner le repo
git clone <url> && cd qwen_LE

# 2. Créer l'environnement virtuel
uv venv
source .venv/bin/activate

# 3. Installer les dépendances
uv sync

# 4. Copier et éditer la config
cp .env.example .env
# → Modifier DATABASE_URL, SECRET_KEY, etc. dans .env

# 5. Démarrer PostgreSQL
docker run -d \
  --name learnenglish-db \
  -e POSTGRES_USER=learnenglish \
  -e POSTGRES_PASSWORD=learnenglish \
  -e POSTGRES_DB=learnenglish \
  -p 5432:5432 \
  postgres:16

# 6. Appliquer les migrations
alembic upgrade head

# 7. Peupler le corpus
uv run python scripts/seed_corpus.py

# 8. Lancer le serveur
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Le QR code et l'URL locale s'affichent dans le terminal au démarrage.

## API

| Méthode | Chemin                   | Description              |
| ------- | ------------------------ | ------------------------ |
| POST    | /api/v1/auth/register    | Créer un compte          |
| POST    | /api/v1/auth/login       | Se connecter             |
| POST    | /api/v1/auth/refresh     | Rafraîchir les tokens    |
| GET     | /api/v1/auth/me          | Profil connecté          |
| GET     | /api/v1/expressions      | Liste des verbes (filtré, paginé) |
| GET     | /api/v1/expressions/{id} | Détail d'un verbe        |
| POST    | /api/v1/expressions      | Créer un verbe (admin)   |
| PUT     | /api/v1/expressions/{id} | Modifier un verbe (admin)|
| DELETE  | /api/v1/expressions/{id} | Supprimer un verbe (admin)|
| GET     | /api/v1/users/me/settings    | Mes préférences      |
| PUT     | /api/v1/users/me/settings    | Modifier mes préférences  |
| GET     | /health                  | Health check             |

## Phases

1. **✅ Backend + DB + Auth + Seed corpus** *(terminé)*
2. ⬜ Apprentissage (SM-2, révisions, mini-tests)
3. ⬜ Frontend (PWA ou mobile)
4. ⬜ Génération d'images par IA
5. ⬜ Déploiement sur CapRover / MinIO
