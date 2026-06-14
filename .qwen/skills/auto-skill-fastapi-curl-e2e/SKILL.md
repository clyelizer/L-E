---
name: fastapi-curl-e2e
description: End-to-end test FastAPI async endpoints from the shell using curl — token management, request chaining, edge case coverage.
source: auto-skill
extracted_at: '2026-06-14T17:09:15.388Z'
---

# FastAPI Curl E2E Testing

Use this skill to verify FastAPI async endpoints work correctly end-to-end using curl from the shell — before writing automated integration tests, or when you need to quickly validate a full user flow.

## Pattern: Token Management

Save the auth token to a temp file so multiple curl commands can share it without cluttering environment variables:

```bash
# Register or login, extract and save the access token
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass1234"}' \
  | python3 -c "import sys,json; open('/tmp/token.txt','w').write(json.load(sys.stdin).get('access_token',''))"

# Use in subsequent requests
TOKEN=$(cat /tmp/token.txt)
curl -s http://localhost:8000/api/v1/memory/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

**Why:** Environment variables (`export TOKEN=...`) work per-shell but can leak in shell history. A temp file is contained, can be read by multiple subprocesses, and is cleaned on reboot.

## Pattern: Chain Requests with Shell Variables

For multi-step flows (e.g., start session → submit → complete), extract IDs from JSON responses into shell variables:

```bash
# Step 1: Start a session, extract IDs
LEARN=$(curl -s -X POST "http://localhost:8000/api/v1/memory/learning/start?word_count=3" \
  -H "Authorization: Bearer $(cat /tmp/token.txt)")

SESSION_ID=$(echo "$LEARN" | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
CARD0_ID=$(echo "$LEARN" | python3 -c "import sys,json; print(json.load(sys.stdin)['cards'][0]['expression_id'])")
CARD0_MEANING=$(echo "$LEARN" | python3 -c "import sys,json; print(json.load(sys.stdin)['cards'][0]['meaning'])")

# Step 2: Use extracted IDs in the next request
curl -s -X POST "http://localhost:8000/api/v1/memory/learning/submit?session_id=$SESSION_ID&expression_id=$CARD0_ID&user_answer=$CARD0_MEANING" \
  -H "Authorization: Bearer $(cat /tmp/token.txt)"
```

## Pattern: URL-encoding Special Characters

Meanings often contain characters like `/`, `%`, spaces that break curl query strings. Always URL-encode when the answer comes from a variable:

```bash
# WRONG — breaks if meaning contains "/" or " "
curl -s "http://localhost:8000/api/v1/endpoint?answer=$raw_meaning"

# RIGHT — URL-encode before passing
ENCODED=$(echo "$LEARN" | python3 -c "import sys,json; import urllib.parse; print(urllib.parse.quote(json.load(sys.stdin)['meaning']))")
curl -s "http://localhost:8000/api/v1/endpoint?answer=$ENCODED"
```

**Alternative:** Use `--data-urlencode` with POST bodies instead of query parameters when answers contain special characters:

```bash
curl -s -X POST http://localhost:8000/api/v1/endpoint \
  --data-urlencode "user_answer=entrer / rentrer" \
  -H "Authorization: Bearer $(cat /tmp/token.txt)"
```

## Pattern: Edge Case Coverage

Test both success and failure paths in every flow:

```bash
# Test correct answer
echo "=== CORRECT ANSWER ==="
curl -s -X POST "http://localhost:8000/api/v1/learning/submit?...&user_answer=$CORRECT" \
  -H "Authorization: Bearer $(cat /tmp/token.txt)" \
  | python3 -m json.tool

# Test incorrect answer (should return is_correct: false, not 500)
echo "=== WRONG ANSWER ==="
curl -s -X POST "http://localhost:8000/api/v1/learning/submit?...&user_answer=wrong" \
  -H "Authorization: Bearer $(cat /tmp/token.txt)" \
  | python3 -m json.tool

# Test boundary: empty corpus
echo "=== EDGE: no due reviews ==="
curl -s -X POST "http://localhost:8000/api/v1/review/start?word_count=5" \
  -H "Authorization: Bearer $(cat /tmp/token.txt)" \
  | python3 -m json.tool
# Expected: 400 Bad Request with "Aucune révision due" message

# Test boundary: invalid input
echo "=== EDGE: invalid session_id ==="
curl -s -X POST "http://localhost:8000/api/v1/learning/complete?session_id=invalid" \
  -H "Authorization: Bearer $(cat /tmp/token.txt)"
# Expected: 400 or 404
```

## Pattern: Verify State After Flow

After completing a multi-step flow, hit the dashboard/stats endpoint to confirm state was updated:

```bash
echo "=== Dashboard After Session ==="
curl -s http://localhost:8000/api/v1/memory/dashboard \
  -H "Authorization: Bearer $(cat /tmp/token.txt)" \
  | python3 -c "
import sys,json
d = json.load(sys.stdin)
assert d['total_sessions'] > 0, 'No sessions recorded!'
assert d['overall_accuracy_pct'] >= 0, 'Invalid accuracy!'
print(f'OK: {d[\"total_sessions\"]} sessions, {d[\"total_expressions_learned\"]} learned')
"
```

## Pattern: Detect 500 Errors

When a curl response is empty or contains "Internal Server Error", use `-sv` to see the HTTP status code:

```bash
curl -sv -X POST "http://localhost:8000/api/v1/endpoint" \
  -H "Authorization: Bearer $(cat /tmp/token.txt)" 2>&1

# Output includes:
# > POST /api/v1/endpoint HTTP/1.1
# < HTTP/1.1 500 Internal Server Error
# < content-type: text/plain; charset=utf-8
# Internal Server Error
```

This reveals whether the error is a 500 (server bug), 400 (bad request), or 401 (auth issue) — even when the server doesn't print stack traces.

## Pattern: Server Port Conflicts

If a FastAPI app on the expected port serves different routes than expected, diagnose:

```bash
# Check which process owns the port
ss -tlnp | grep 8000

# Check routes via OpenAPI spec
curl -s http://localhost:8000/openapi.json | python3 -c "
import sys,json
d = json.load(sys.stdin)
for p in sorted(d.get('paths',{})):
    print(f'  {p}')
"

# If routes don't match your project, the wrong app is running
# Example: process shows 'new_ui.backend.main:app' instead of your app
# Fix: start on a different port
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## Full Flow Template

Combine all patterns into a complete test script:

```bash
#!/bin/bash
# Test script template for a multi-step FastAPI flow
set -euo pipefail

BASE="http://localhost:8080"
TOKEN=$(cat /tmp/token.txt)
AUTH="Authorization: Bearer $TOKEN"

echo "=== 1. Dashboard initial ==="
curl -s "$BASE/api/v1/memory/dashboard" -H "$AUTH" | python3 -m json.tool

echo "=== 2. Start learning ==="
LEARN=$(curl -s -X POST "$BASE/api/v1/memory/learning/start?word_count=2" -H "$AUTH")
SID=$(echo "$LEARN" | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
echo "Session: $SID"

echo "=== 3. Submit answers ==="
for i in 0 1; do
  CID=$(echo "$LEARN" | python3 -c "import sys,json; print(json.load(sys.stdin)['cards'][$i]['expression_id'])")
  curl -s -X POST "$BASE/api/v1/memory/learning/submit?session_id=$SID&expression_id=$CID&user_answer=test" -H "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Card $i: correct={d[\"is_correct\"]}, quality={d[\"quality\"]}')"
done

echo "=== 4. Complete ==="
curl -s -X POST "$BASE/api/v1/memory/learning/complete?session_id=$SID" -H "$AUTH" | python3 -m json.tool

echo "=== 5. Dashboard final ==="
curl -s "$BASE/api/v1/memory/dashboard" -H "$AUTH" | python3 -m json.tool
```
