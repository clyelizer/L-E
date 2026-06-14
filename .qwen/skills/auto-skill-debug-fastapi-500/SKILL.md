---
name: debug-fastapi-500
description: Systematic approach to debug FastAPI 500 Internal Server Errors in production/background mode where no Python stack trace is visible.
source: auto-skill
extracted_at: '2026-06-14T17:09:15.388Z'
---

# Debug FastAPI 500 Internal Server Errors

Use this skill when a FastAPI endpoint returns HTTP 500 with no useful error detail — just "Internal Server Error" in the response body, no stack trace logged to stdout/stderr.

## Root Cause

FastAPI's default 500 handler returns a minimal `text/plain` body with no context. Common hidden causes:

- **Unhandled exception** in the endpoint or service function (not caught by a try/except)
- **Missing import** scoped inside a conditional branch (e.g., `from datetime import timedelta` inside `if is_correct:` but also used in `else:`)
- **Async/sync mismatch** — calling a sync function in an async context without proper await
- **SQLAlchemy session issue** — using a session after it's closed or committing outside a transaction
- **TypeError** — `None` passed where a value expected, or wrong type to an operator

## Diagnostic Steps

### Step 1: Get the raw HTTP response

Use `curl -sv` (verbose, show headers and status code):

```bash
curl -sv -X POST "http://localhost:8080/api/v1/memory/learning/submit?session_id=SID&expression_id=EID&user_answer=test" \
  -H "Authorization: Bearer $TOKEN" 2>&1
```

Look for:
- `HTTP/1.1 500 Internal Server Error` — confirms it's a server-side error, not a validation (400) or auth (401) issue
- `content-type: text/plain; charset=utf-8` — FastAPI's default minimal error format
- The body (usually just "Internal Server Error" or empty)

### Step 2: Read the endpoint code end-to-end

Trace through the exact function that handles the route. Focus especially on **every branch**:

```python
# Look for this pattern — a name used outside its import scope
if condition:
    from datetime import timedelta  # ← scoped import!
    value = now + timedelta(hours=1)
else:
    value = now + timedelta(minutes=5)  # ← NameError! timedelta not imported here
```

Check these common scoping traps:
- Is every imported symbol available in ALL code paths (not just one branch)?
- Are there any `from X import Y` statements inside `if`/`else`/`for`/`try` blocks?
- If a helper is imported inside a conditional, is it also used outside that conditional?

### Step 3: Check for None/null propagation

If the route processes a user-supplied value, trace what happens when it's `None`:

```python
# Common crash: calling .strip() on None
is_correct = user_answer.strip().lower() == expression.meaning.strip().lower()
#            ^^^^^^^^^^^^^^^^^^^ — crashes if user_answer is None
```

FastAPI `Query(...)` with `min_length=1` protects against empty strings but not against `null` in JSON body parameters.

### Step 4: Verify async boundaries

Check that all database operations use `await`:

```python
# WRONG — missing await, returns a coroutine object
result = db.execute(stmt)

# RIGHT
result = await db.execute(stmt)
```

Also check that no sync database calls are made in an async context.

### Step 5: Enable more verbose server logging as a last resort

If the above doesn't reveal the issue, run the server with `--log-level debug` or add a global exception handler:

```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    traceback.print_exc()  # will appear in server stderr
    return JSONResponse(status_code=500, content={"detail": str(exc)})
```

**Important:** Use this only temporarily — it leaks internal details in production.

## Verification

After applying the fix, reproduce the exact failing curl command — it should now return 200/201/400 instead of 500.

## Common Patterns Found in Practice

| Pattern | Symptom | Fix |
|---------|---------|-----|
| Import scoped in conditional | 500 only on one code path (e.g., wrong answers vs correct) | Move `import` to module level |
| `None` value on `.strip()` | 500 when optional query param is omitted | Check for `None` before `.strip()` |
| Missing `await` | 500 with `TypeError: cannot await` or coroutine leaks | Add `await` |
| Using session after commit | 500 with `sqlalchemy.exc.ResourceClosedError` | Move operations before `db.commit()` |
| Sync SQLAlchemy in async | 500 on first DB access | Use `AsyncSession` and `select()` not `Query` |
