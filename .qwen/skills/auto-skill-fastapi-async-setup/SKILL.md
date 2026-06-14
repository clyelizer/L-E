---
name: fastapi-async-setup
description: Troubleshoot common SQLAlchemy async + FastAPI integration issues — string relationship resolution, UUID auto-generation timing, passlib replacement, QR terminal rendering.
source: auto-skill
extracted_at: '2026-06-14T16:34:34.476Z'
---

# FastAPI + SQLAlchemy Async Setup Troubleshooting

Use this skill when setting up a FastAPI async application with SQLAlchemy 2.0 asyncio, encountering issues like `InvalidRequestError: failed to locate a name`, `NotNullViolationError: null value in column`, or passlib bcrypt errors.

## 1. String Relationship Reference Resolution

**Symptom:** `sqlalchemy.exc.InvalidRequestError: When initializing Mapper[X], expression 'Y' failed to locate a name ('Y').`

**Cause:** SQLAlchemy string-based relationship targets (e.g., `relationship("UserMemory")` or `relationship("User", back_populates="user_memories")`) require the referenced model module to be imported before any query or mapper configuration occurs. This is especially common in async setups where models are imported lazily.

**Fix:** Add eager imports of ALL model modules at the application entrypoint AND in any standalone scripts (seed scripts, management commands):

```python
# app/main.py — at the top, before FastAPI app instantiation
from app.models.base import Base
import app.models.user       # noqa: F401
import app.models.expression  # noqa: F401
import app.models.memory      # noqa: F401
import app.models.session     # noqa: F401
import app.models.mistake     # noqa: F401
```

The same applies to standalone scripts:

```python
# scripts/seed_corpus.py
from app.models.base import Base
import app.models.user       # noqa: F401
import app.models.expression  # noqa: F401
import app.models.memory      # noqa: F401
import app.models.session     # noqa: F401
import app.models.mistake     # noqa: F401
```

**Why:** SQLAlchemy uses registry-based configuration. Model classes are added to the registry when their module is imported. String relationship references are resolved lazily during mapper configuration — if the target class isn't in the registry yet, the resolution fails.

**How to apply:** Add eager model imports at every Python entrypoint that touches the database. The `# noqa: F401` comment prevents linting tools from flagging unused imports.

## 2. Auto-Generated UUID Not Available Before Flush

**Symptom:** `psycopg2.errors.NotNullViolation: null value in column "user_id"` (or similar FK violation).

**Cause:** When a model uses `default=str(uuid.uuid4())` or `default=new_uuid` for its primary key, the default function is called by Python at insert time — but only AFTER `db.flush()` synchronizes the in-memory state to the DB. If you try to reference `model.id` before flushing, it may be `None`.

```python
# WRONG — user.id is None
user = User(email="a@b.com", password_hash="...")
db.add(user)
settings = UserSettings(user_id=user.id)  # user.id is None!

# RIGHT — flush first
user = User(email="a@b.com", password_hash="...")
db.add(user)
await db.flush()          # populates user.id from DB
settings = UserSettings(user_id=user.id)  # user.id is set
```

**Why:** SQLAlchemy's `default=` callable is evaluated by Python when the object is added to the session, but the resulting value is only sent to the DB during `flush()`. Before flush, `model.id` returns `None` because the DB hasn't generated/assigned the value yet.

**How to apply:** Always `await db.flush()` after `db.add(obj)` before referencing `obj.id` in subsequent operations that depend on it. Use `await db.commit()` at the end to persist everything.

## 3. passlib bcrypt Backend Detection Failure

**Symptom:** `ValueError: password cannot be longer than 72 bytes, truncate manually if necessary` when calling `pwd_context.hash(password)`.

**Cause:** passlib's bcrypt backend detection fails on some systems (specific libc/pycryptodome versions), causing it to fall back to a broken backend that hits bcrypt's 72-byte password limit check incorrectly.

**Fix:** Replace passlib with the direct `bcrypt` library:

```python
# app/core/security.py
import bcrypt

BCRYPT_ROUNDS = 12

def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt (cost=12)."""
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    ).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""
    return bcrypt.checkpw(
        plain.encode("utf-8"),
        hashed.encode("utf-8")
    )
```

Also add `bcrypt` to your project dependencies (it's a standalone package, not passlib's bundled bcrypt).

**Why:** passlib wraps bcrypt through multiple backends (bcrypt, pycryptodome, os_crypt). When all backends fail detection, passlib's stub handler raises a confusing error about 72-byte limits. The standalone `bcrypt` library is simpler and more reliable.

**How to apply:** Remove passlib from dependencies, add `bcrypt`, update all hash/verify calls to use `bcrypt.hashpw`/`bcrypt.checkpw`. Clean `__pycache__` afterward to prevent stale .pyc from loading old code.

## 4. QR Code Terminal Rendering

**Symptom:** `AttributeError: 'Image' object has no attribute 'to_terminal'`

**Cause:** The `qrcode` library's `PIL` image backend does not have a `.to_terminal()` method. The correct method is `print_ascii()` on the QR code object itself, not on the rendered image.

```python
# WRONG
qr.make_image().to_terminal()

# RIGHT
import io
buf = io.StringIO()
qr.print_ascii(out=buf)
print(buf.getvalue())
```

**How to apply:** Always use `qr.print_ascii(out=buf)` on the `qrcode.QRCode` object, not on the `Image` returned by `qr.make_image()`.

## 5. Stale Bytecode Cache (`__pycache__`)

**Symptom:** Code changes don't take effect; old errors persist even though `.py` files are correct.

**Cause:** Python caches compiled bytecode in `__pycache__/` directories. When running background tasks or long-lived processes, they may load stale `.pyc` files instead of the current `.py` source.

**Fix:** Clean all bytecode caches:

```bash
find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null
find . -name '*.pyc' -delete 2>/dev/null
```

**How to apply:** Always clean `__pycache__` after making code changes, especially when running multiple background tasks or when errors reference line numbers that no longer match the current file.
