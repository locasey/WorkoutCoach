# LOC-12: Migrate Auth Sessions to Persistent Storage

**Type:** Improvement
**Priority:** Low
**Effort:** Small

## TL;DR

Replace in-memory session store with persistent storage so sessions survive container restarts and can scale across multiple instances.

## Current State

- Auth sessions stored in Python dict (`_sessions = {}` in `auth_service.py`)
- Sessions lost on container restart = users logged out
- Can't scale to multiple backend instances (each has separate session store)

## Expected Outcome

- Sessions persist across container restarts
- Users stay logged in after deployments
- (Future) Can scale to multiple backend instances if needed

## Storage Options (TBD)

1. **PostgreSQL** (Neon) - No extra infra, already have DB, slightly slower
2. **Redis** - Faster, but adds another service to manage
3. **Flask-Session** - Library that handles this, supports both backends

## Files to Touch

- [backend/services/auth_service.py](backend/services/auth_service.py) - Replace `_sessions` dict with DB/Redis calls
- [backend/models/](backend/models/) - Add `AuthSession` model if using PostgreSQL
- [backend/requirements.txt](backend/requirements.txt) - Add `flask-session` or `redis` if needed

## Notes

- Not urgent for single-instance Lightsail deployment
- Current 24h session expiry means max disruption is re-login after deploy
- Consider implementing when scaling becomes a concern
