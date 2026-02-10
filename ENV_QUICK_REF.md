# .env Quick Reference

## 🚀 Get Started in 2 Minutes

```bash
cd /opt/app/promo_py

# Docker is ready to go - just run:
docker compose up --build

# That's it! Visit: http://localhost:8000
```

---

## 📝 What Each Variable Does

```env
# Django Security & Mode
DEBUG=True|False                    # Show detailed errors (dev only)
SECRET_KEY=your-secret              # CSRF/session encryption key
ALLOWED_HOSTS=localhost,127.0.0.1   # Accept requests from these domains

# Database
DB_ENGINE=sqlite3|postgresql        # Which database to use
DB_NAME=promo_db                    # (PostgreSQL only)
DB_USER=postgres                    # (PostgreSQL only)
DB_PASSWORD=secure_pass             # (PostgreSQL only)
DB_HOST=localhost                   # (PostgreSQL only)
DB_PORT=5432                        # (PostgreSQL only)

# App Behavior
PYTHONUNBUFFERED=1                  # See logs in real-time (Docker)
```

---

## 🔑 Essential for Docker

| Must Know | Impact |
|-----------|--------|
| `.env` loaded automatically | No extra setup needed |
| Defaults provided | Works out of box |
| SQLite (file-based) | No DB server needed for dev |
| PostgreSQL ready | Switch via `DB_ENGINE` |
| Test-gating enabled | Tests run before production build |

---

## 🎯 Common Scenarios

### ✅ Development (Default - Just Works)
- Uses SQLite (file-based)
- DEBUG=True shows errors
- No database setup needed

### 🚀 Production
Change in `.env`:
```env
DEBUG=False
SECRET_KEY=your-secure-production-key
ALLOWED_HOSTS=yourdomain.com
DB_ENGINE=django.db.backends.postgresql
DB_HOST=your-db-host.com
DB_PASSWORD=strong-password
```

### 🐳 Docker Compose
Docker auto-loads `.env` file:
```yaml
env_file:
  - .env
```

---

## 📋 Files Overview

| File | Purpose | Should Commit? |
|------|---------|--------|
| `.env` | Active config | ❌ No (ignored) |
| `.env.example` | Template | ✅ Yes (safe) |
| `ENV_GUIDE.md` | Full docs | ✅ Yes |
| `settings.py` | Reads env vars | ✅ Yes |

---

## ⚠️ 3 Critical Points

1. **DEBUG=True** = Development only (never production!)
2. **SECRET_KEY** = Keep it secret, keep it safe
3. **Database** = SQLite works locally, PostgreSQL for production

---

## ✨ What Works Now

✅ Docker builds cleanly  
✅ Tests run automatically  
✅ Database migrations applied  
✅ Static files collected  
✅ Gunicorn starts with 3 workers  
✅ Serving on port 8000  

**Run it**: `docker compose up --build`  
**Stop it**: `Ctrl+C`

---

For details, see: [ENV_GUIDE.md](ENV_GUIDE.md)
