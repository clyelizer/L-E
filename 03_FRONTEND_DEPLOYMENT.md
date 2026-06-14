# learnEnglish — Frontend, Déploiement & Roadmap

---

## 1. Frontend — Application web responsive

### 1.1 Stack

| Composant | Technologie |
|-----------|-------------|
| Framework | React 18+ ou Vue 3 |
| Build | Vite |
| Routing | React Router / Vue Router |
| State | Zustand (React) / Pinia (Vue) |
| UI | Tailwind CSS + Headless UI |
| API | fetch natif + React Query / SWR |
| QR Code | qrcode.js ou généré backend |

### 1.2 Pages / Composants

```
/
├── auth/
│   ├── LoginPage
│   └── RegisterPage
│
├── dashboard/
│   ├── DashboardPage
│   ├── StreakCard
│   ├── TodaySummary
│   └── ProgressChart
│
├── learn/
│   ├── LearnConfigPage        # Écran "combien de mots apprendre ?"
│   ├── LearnSessionPage       # Découverte carte par carte
│   ├── LearnMiniTestCard      # Mini-test optionnel après chaque carte
│   └── LearnCompletePage      # Résultat session
│
├── review/
│   ├── ReviewConfigPage       # Écran "combien mots + types exercices ?"
│   ├── ReviewSessionPage      # Questions une par une
│   ├── ReviewQuestionCard     # Question directe (QCM, trou, trad)
│   └── ReviewCompletePage     # Résultat session
│
├── quiz/
│   ├── MCQQuestion
│   ├── FillBlankQuestion
│   ├── TranslationQuestion
│   ├── MatchQuestion
│   └── QuizProgress
│
├── progress/
│   ├── ProgressPage
│   ├── MasteryChart
│   ├── WeaknessList
│   └── ExpressionHistory
│
├── library/
│   ├── ExpressionListPage
│   ├── ExpressionDetail      # Affiche expression + image + exemples
│   └── SearchBar
│
├── settings/
│   ├── SettingsPage
│   └── ProfileForm
│
└── shared/
    ├── Layout
    ├── Navbar
    ├── LoadingSpinner
    ├── ErrorBoundary
    └── Toast
```

### 1.3 États de chaque composant

| État | Comportement |
|------|-------------|
| `loading` | Skeleton / spinner |
| `empty` | Message + CTA |
| `error` | Message + bouton réessayer |
| `success` | Contenu normal |

### 1.4 Responsive

- Mobile-first (breakpoints : 640, 768, 1024, 1280)
- Sidebar desktop → bottom nav mobile
- Quiz cards : full width mobile, centré desktop

### 1.5 QR Code — accès mobile

Au démarrage du serveur :
1. Détection IP LAN (`netifaces`)
2. Génération URL `http://192.168.x.x:8000`
3. QR code dans terminal (`qrcode` + `rich`)
4. URL aussi écrite dans `url.txt`

---

## 2. Déploiement

### 2.1 Architecture

```
Machine Linux (Ubuntu 24.04)
├── PostgreSQL 16          (systemd)
├── Redis (optionnel)      (systemd)
├── Uvicorn (app FastAPI)  (systemd)
│   └── Port 8000
├── Caddy / Nginx          (reverse proxy, TLS optionnel)
│   └── Port 443 / 80
├── Images/                (stockage fichiers images)
└── Cron                   (pg_dump, cleanup)
```

### 2.2 Installation

```bash
git clone <url> /opt/learnEnglish && cd /opt/learnEnglish
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Éditer DATABASE_URL, SECRET_KEY, LLM_API_KEY...

sudo -u postgres createdb learnenglish
sudo -u postgres psql -c "CREATE USER learnenglish WITH PASSWORD '...';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE learnenglish TO learnenglish;"

alembic upgrade head
sudo systemctl enable learnenglish && sudo systemctl start learnenglish
```

### 2.3 Service systemd

```ini
# /etc/systemd/system/learnenglish.service
[Unit]
Description=learnEnglish — Adaptive vocabulary learning
After=network.target postgresql.service

[Service]
Type=simple
User=coulibaly
WorkingDirectory=/opt/learnEnglish
Environment=PATH=/opt/learnEnglish/.venv/bin
EnvironmentFile=/opt/learnEnglish/.env
ExecStart=/opt/learnEnglish/.venv/bin/uvicorn app.main:app \
    --host 0.0.0.0 --port 8000 --workers 2 --log-level info
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 2.4 Backup automatisé

```bash
#!/bin/bash
# /etc/cron.daily/learnenglish-backup
BACKUP_DIR=/var/backups/learnenglish
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump -U learnenglish learnenglish | gzip > "$BACKUP_DIR/$TIMESTAMP.sql.gz"
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

# Backup des images (plus rare)
tar czf "$BACKUP_DIR/images_$TIMESTAMP.tar.gz" /opt/learnEnglish/images
```

### 2.5 Docker (optionnel)

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    volumes: [pgdata:/var/lib/postgresql/data]
    env_file: .env
  app:
    build: .
    ports: ["8000:8000"]
    depends_on: [db]
    env_file: .env
    volumes: [images:/app/images]
  redis:
    image: redis:7-alpine
    profiles: [with-cache]
volumes: {pgdata:, images:}
```

---

## 3. Sécurité

| Mesure | Détail |
|--------|--------|
| **JWT** | access_token (15min) + refresh_token (7 jours) |
| **Hash** | bcrypt (cost=12) |
| **Rate limit** | 5 tentatives/min sur `/auth/login` |
| **Cookie** | `Secure; HttpOnly; SameSite=Strict` |
| **Clé API LLM** | `.env` uniquement, jamais exposée au frontend |
| **Export** | `GET /api/v1/users/me/export` → JSON |
| **Suppression** | Soft delete + purge à 30 jours |

---

## 4. Tests

### 4.1 Pyramide

```
         ┌─────────────┐
         │   E2E (1-2) │  ← Playwright
        ┌┴─────────────┴┐
        │  Intégration   │  ← pytest + httpx AsyncClient
       ┌┴────────────────┴┐
       │   Unitaires        │  ← Engines, services
       └───────────────────┘
```

### 4.2 Priorités

| Module | Couverture cible |
|--------|-----------------|
| `engines/memory_engine.py` | 95%+ |
| `engines/selection_engine.py` | 95%+ |
| `engines/quiz_engine.py` | 95%+ |
| `engines/scheduling_engine.py` | 95%+ |
| Services | 85%+ |
| API routes | 90%+ |
| AI (mocké) | 70%+ |

### 4.3 Outils

```
pytest, pytest-asyncio, pytest-cov
httpx (AsyncClient), factory_boy (fixtures)
respx (mocking LLM), playwright (E2E)
```

---

## 5. Roadmap MVP

### Phase 1 — Fondation (Jours 1-3)

- [ ] Initialiser projet Python (pyproject.toml, .venv)
- [ ] FastAPI + Uvicorn + structure dossiers
- [ ] Core : config, database, security
- [ ] Models SQLAlchemy + migrations Alembic (incl. `images`, `metaphor`)
- [ ] Seed : les expressions de base + tags
- [ ] Auth : register + login + JWT

### Phase 2 — Moteur SRS (Jours 4-6)

- [ ] Memory Engine (SM-2 + mastery_score)
- [ ] Selection Engine (nouveaux + révisions)
- [ ] Quiz Engine (MCQ, FILL_BLANK, FR_TO_EN)
- [ ] Scheduling Engine
- [ ] Routes : learning, review, quiz

### Phase 3 — Frontend MVP (Jours 7-10)

- [ ] Projet React + Vite + Tailwind
- [ ] Pages : Login, Dashboard
- [ ] Session LEARN : config (choisir nb) → découverte carte → [mini-test si paramètre ON] → résultat
- [ ] Session REVIEW : config (choisir nb + types exercices) → questions une par une → résultat
- [ ] Composants quiz (MCQ, fill, translation, match)
- [ ] Responsive mobile
- [ ] **Affichage image** sur les cartes
- [ ] Paramètres utilisateur : nombre mots/jour, mini-test ON/OFF

### Phase 4 — Progrès & Paramètres (Jours 11-12)

- [ ] Dashboard stats (streak, progression, accuracy)
- [ ] Page progression détaillée
- [ ] Page settings
- [ ] Bibliothèque d'expressions + recherche
- [ ] **Affichage ExpressionDetail avec image**

### Phase 5 — Déploiement (Jours 13-14)

- [ ] Service systemd
- [ ] QR code + détection IP LAN
- [ ] Tests unitaires + intégration
- [ ] Documentation README
- [ ] Backup automatisé

### Phase 6 — Pipeline corpus (Prérequis ou parallèle)

- [ ] Script batch génération IA textuelle (DeepSeek v4 Flash)
- [ ] Validation automatique des fiches
- [ ] Script batch génération images
- [ ] Validation qualité des images

---

## 6. Variables d'environnement

```env
# .env
DATABASE_URL=postgresql+asyncpg://learnenglish:password@localhost:5432/learnenglish
SECRET_KEY=<generated-with-openssl>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# LLM
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-...
LLM_MODEL=deepseek-v4-flash
LLM_MAX_TOKENS=500
LLM_TEMPERATURE=0.7

# Image API (Phase 3)
IMAGE_API_PROVIDER=openai
IMAGE_API_KEY=sk-...
IMAGE_API_MODEL=dall-e-3
IMAGE_OUTPUT_DIR=/opt/learnEnglish/images

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=2
LOG_LEVEL=info

# Feature flags
ENABLE_AI=true
CACHE_ENABLED=true
REDIS_URL=redis://localhost:6379/0
```
