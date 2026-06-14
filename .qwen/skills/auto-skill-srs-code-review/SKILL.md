---
name: srs-code-review
description: Systematic security & correctness review for SRS (spaced repetition) APIs — SM-2 spec compliance, MCQ answer leak prevention, session ownership, transaction integrity, REST hygiene.
source: auto-skill
extracted_at: '2026-06-14T17:29:01.993Z'
---

# SRS Code Review — Security & Correctness Checklist

Use this skill when performing a rigorous code review on a spaced repetition system (SRS) — typically a FastAPI + SQLAlchemy async app with SM-2 algorithm, learning/review sessions, and MCQ exercises.

This is not a general code review — it targets vulnerabilities and correctness issues **specific to SRS backends**, drawn from real-world findings.

---

## Review Checklist

Go through each finding area in order. Each has a concrete test you can apply to the codebase.

### 1. SM-2 Algorithm Compliance

| Check | What to look for |
|-------|------------------|
| **EF only on quality >= 3** | The SM-2 spec says ease factor is ONLY modified when quality >= 3. If the formula runs unconditionally, it's a bug. |
| **Quality mapping** | Verify `quality_from_correct()` correctly handles boundary values: 0ms, 3000ms, 8000ms. |
| **EF clamping** | EF must be clamped to [1.30, 3.00] after every calculation. |
| **Repetition reset** | Quality < 3 must reset repetitions to 0 and interval to 1. |

**Test:** Run the SM-2 engine with quality=0 on a card with EF=2.50. If EF changes, the formula is unconditional → bug. Correct behavior: EF stays 2.50.

### 2. MCQ Security — Answer Exposure

| Check | What to look for |
|-------|------------------|
| **`correct` field in MCQ response** | The correct answer must NEVER be in the response sent to the client. Server evaluates correctness during submission. |
| **`correct_index` field** | Same — leaks which option is correct. Remove from response dict. |

**Test:** Trace the full data path from generator → service → API response. If `correct` or `correct_index` appears in any dict that reaches `return` in an API handler, it will leak to the client.

### 3. Session Ownership Enforcement

| Check | What to look for |
|-------|------------------|
| **Every submit/complete endpoint** | Must verify `StudySession.user_id == current_user.id`. A session_id alone is not enough — any authenticated user could submit to another user's session. |
| **Not just session lookup** | A simple `select(StudySession).where(id == session_id)` doesn't verify ownership. Must add `.where(user_id == user_id)`. |

**Test:** For every endpoint that takes a `session_id`, check whether the query also filters by `user_id`. If not, it's vulnerable to session hijacking.

### 4. Transaction Integrity — Rollback

| Check | What to look for |
|-------|------------------|
| **Every `except ValueError` in API routes** | Must call `await db.rollback()` before raising `HTTPException`. Without rollback, the DB transaction remains in a failed state and subsequent queries will crash. |

**Test:** Count all `except ValueError` or `except Exception` blocks in API files. Each one that catches and re-raises must have `await db.rollback()` before the raise.

### 5. REST Hygiene — POST Body Models

| Check | What to look for |
|-------|------------------|
| **POST mutations must use Pydantic body models** | FastAPI `Query()` params for POST endpoints expose data in URLs/logs and are a REST anti-pattern. |

**Search pattern:** `@router.post(...` followed by `= Query(...` → should use a Pydantic body model instead.

### 6. `is_learning` Flag Consistency

| Check | What to look for |
|-------|------------------|
| **Same logic across services** | If `learning.py` uses `not is_correct` and `review.py` uses `repetitions < 2`, they're inconsistent. Both should use the same criterion. |

### 7. Dead Code

| Check | What to look for |
|-------|------------------|
| **Unused imports** | e.g., `joinedload`, `Session` — remove them. |
| **Lazy imports** | `from X import Y` inside a function body when it could be at module level. |
| **Unused parameters** | Function parameters that are never referenced. |
| **Redundant processing** | Code that strips fields that were already removed upstream. |

---

## Correction Execution Strategy

After the review produces findings, execute corrections in this order:

### Step 1: Group by dependency

Group findings into independent clusters. A finding in group A may change the contract of a function used by group B — identify these dependencies.

**Good grouping example:**
- **Group A**: SM-2 engine + tests (self-contained, no dependencies)
- **Group B**: Question generator (changes output shape used by review service)
- **Group C**: Service layer (session ownership + rollback logic)
- **Group D**: API layer (body models — depends on service signatures being final)
- **Group E**: Consistency fixes (depends on logic being stable)
- **Group F**: Dead code cleanup (do last — may become irrelevant after other fixes)

### Step 2: Apply sequentially with verification gates

```
For each group:
  1. Apply all changes in the group
  2. Run tests
  3. Only if ALL tests pass → proceed to next group
  4. If any test fails → fix within the current group, don't cascade
```

### Step 3: Full suite + import verification

After all groups:
```bash
pytest -v --tb=short
python -c "from app.x import y"  # check imports
```

---

## Common Code Patterns to Fix

### Session ownership — add filter to query

```python
# BAD — no ownership check
result = await db.execute(
    select(StudySession).where(StudySession.id == session_id)
)
# GOOD — filters by user_id too
result = await db.execute(
    select(StudySession).where(
        StudySession.id == session_id,
        StudySession.user_id == user_id,
    )
)
```

### Transaction rollback

```python
# BAD — no rollback, leaves transaction in failed state
try:
    result = await service_func(...)
    await db.commit()
except ValueError as exc:
    raise HTTPException(status_code=400, detail=str(exc))

# GOOD — rollback before re-raising
try:
    result = await service_func(...)
    await db.commit()
except ValueError as exc:
    await db.rollback()
    raise HTTPException(status_code=400, detail=str(exc))
```

### MCQ security — strip answer from response

```python
# BAD — leaks answer to client
return {
    "type": "MCQ",
    "options": options,
    "correct_index": 2,       # ← LEAKS
    "correct": "answer",      # ← LEAKS
}

# GOOD — only the question data
return {
    "type": "MCQ",
    "options": options,
}
```

### Distractor deduplication

```python
# BAD — two expressions with same meaning produce duplicate options
distractors = [c.meaning for c in candidates[:count]]

# GOOD — deduplicate by meaning
seen_meanings: set[str] = set()
distractors: list[str] = []
for c in candidates:
    if c.meaning not in seen_meanings:
        seen_meanings.add(c.meaning)
        distractors.append(c.meaning)
    if len(distractors) >= count:
        break
```
