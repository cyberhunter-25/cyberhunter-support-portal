# Flask-Session Redis Connection Fix

## Problem
The CyberHunter Security Portal was experiencing 500 errors because Flask-Session was trying to connect to `localhost:6379` instead of the Redis container at `redis:6379`.

## Root Cause Analysis
1. **Flask-Session Configuration**: `app/extensions.py` was using `REDIS_URL` instead of `SESSION_REDIS_URL`
2. **Missing Environment Variable**: `SESSION_REDIS_URL` was not defined in environment configuration
3. **Default Fallback**: When `SESSION_REDIS_URL` was missing, it defaulted to `redis://localhost:6379/0`

## Changes Made

### 1. Environment Configuration
**File**: `.env.production.configured`
```bash
# Added SESSION_REDIS_URL configuration
SESSION_REDIS_URL=redis://:b350d381ea8db815d7a15e28ac387578@redis:6379/2
```

### 2. Docker Compose Configuration  
**File**: `docker-compose.yml`
```yaml
# Added SESSION_REDIS_URL to web service environment
environment:
  # ... other variables ...
  SESSION_REDIS_URL: redis://:${REDIS_PASSWORD:-changeme}@redis:6379/2
```

### 3. Flask-Session Configuration
**File**: `app/extensions.py`
```python
# Changed from REDIS_URL to SESSION_REDIS_URL
redis_url = app.config.get('SESSION_REDIS_URL', 'redis://localhost:6379/2')
```

## Redis Database Allocation
- **DB 0**: General Redis cache (`REDIS_URL`)
- **DB 1**: Celery broker (`CELERY_BROKER_URL`)  
- **DB 2**: Flask-Session storage (`SESSION_REDIS_URL`) ← **Fixed**
- **DB 3**: Rate limiting (`RATELIMIT_STORAGE_URL`)

## Deployment Steps
1. Copy updated files to server
2. Stop containers: `docker-compose --env-file .env.production.configured down`
3. Start containers: `docker-compose --env-file .env.production.configured up -d`
4. Check logs: `docker-compose --env-file .env.production.configured logs web`

## Verification
- Check container logs for Redis connection errors
- Test application endpoints
- Verify session functionality works

## Files Modified
- `/Users/cdodunski/claude/SUPPORT-PORTAL/.env.production.configured`
- `/Users/cdodunski/claude/SUPPORT-PORTAL/docker-compose.yml`
- `/Users/cdodunski/claude/SUPPORT-PORTAL/app/extensions.py`

## Note
The `app/config.py` file already had the correct `SESSION_REDIS_URL` configuration (line 32), so no changes were needed there.