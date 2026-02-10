# Environment Configuration Guide

## Overview
The `.env` file is **critical** for Docker and Django configuration. It contains sensitive information and environment-specific settings that should never be committed to version control.

## File Location
- **For Docker**: Place `.env` in the root directory (`/opt/app/promo_py/.env`)
- **For Development**: Also in root (`/opt/app/promo_py/.env`) — Python-dotenv will find it automatically

## Environment Variables Explained

### Django Core Settings

#### `DEBUG` (default: `True`)
```env
DEBUG=True    # Development
DEBUG=False   # Production (IMPORTANT: Set to False in production!)
```
- When `True`: Shows detailed error pages, disables CSRF protection partially
- When `False`: Shows generic error pages, enables security checks
- **Security Warning**: Never set to `True` in production

#### `SECRET_KEY` (default: `django-insecure-dev-key-change-in-production`)
```env
SECRET_KEY=your-super-secret-key-here
```
- Used for password hashing, CSRF tokens, session management
- Must be unique and kept secret
- Generate a new one for production: `python manage.py shell` → `from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())`

#### `ALLOWED_HOSTS` (default: `localhost,127.0.0.1,0.0.0.0`)
```env
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,example.com
```
- Comma-separated list of hostnames/IPs that Django will accept
- Prevents HTTP Host header attacks
- Use `*` in development only; explicitly list domains in production

### Database Configuration

#### `DB_ENGINE` (default: `django.db.backends.sqlite3`)
```env
# SQLite (Development)
DB_ENGINE=django.db.backends.sqlite3

# PostgreSQL (Production)
DB_ENGINE=django.db.backends.postgresql
```
- Determines which database backend to use
- SQLite: File-based, no additional setup needed
- PostgreSQL: Requires separate database server

#### PostgreSQL-Specific Variables
Only used when `DB_ENGINE=django.db.backends.postgresql`

```env
DB_NAME=promo_db          # Database name
DB_USER=postgres          # Database user
DB_PASSWORD=secure_pass   # Database password
DB_HOST=localhost         # Host (localhost for local, service name for Docker)
DB_PORT=5432              # PostgreSQL default port
```

### Application Settings

#### `PYTHONUNBUFFERED` (default: `1`)
```env
PYTHONUNBUFFERED=1
```
- Forces Python to output immediately instead of buffering
- Important for Docker to see logs in real-time
- Always set to `1` in containers

---

## Quick Start Templates

### 📝 Development (SQLite + Debug)
```env
DEBUG=True
SECRET_KEY=dev-key-12345-change-this
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

DB_ENGINE=django.db.backends.sqlite3

PYTHONUNBUFFERED=1
```

### 🚀 Production (PostgreSQL + Secure)
```env
DEBUG=False
SECRET_KEY=your-production-secret-key-here-generate-a-new-one
ALLOWED_HOSTS=example.com,www.example.com,your-domain.com

DB_ENGINE=django.db.backends.postgresql
DB_NAME=promo_production
DB_USER=postgres_user
DB_PASSWORD=very-secure-password-here
DB_HOST=db.example.com
DB_PORT=5432

PYTHONUNBUFFERED=1
```

### 🐳 Docker Local Development
```env
DEBUG=True
SECRET_KEY=docker-dev-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,host.docker.internal

DB_ENGINE=django.db.backends.sqlite3

PYTHONUNBUFFERED=1
```

---

## How Django Loads .env

The `settings.py` uses `python-dotenv` to automatically load variables:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-value')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
```

This means:
- .env variables override defaults
- Missing variables use fallback values (shown above)
- Environment variables set in Docker/shell override .env

---

## 🔒 Security Best Practices

1. **Never commit .env to git**
   ```bash
   # Add to .gitignore
   .env
   .env.local
   .env.*.local
   ```

2. **Generate unique SECRET_KEY for each environment**
   ```bash
   cd promo && python manage.py shell
   >>> from django.core.management.utils import get_random_secret_key
   >>> print(get_random_secret_key())
   ```

3. **Use strong passwords for DB_PASSWORD**
   - Minimum 16 characters
   - Mix of uppercase, lowercase, numbers, symbols
   - Never reuse across environments

4. **Set DEBUG=False in production**
   - Shows detailed errors only in development
   - Prevents information leakage in production

5. **Use environment-specific ALLOWED_HOSTS**
   - Development: `localhost,127.0.0.1,0.0.0.0`
   - Production: `your-domain.com,www.your-domain.com`

---

## 🐛 Common Issues & Solutions

### "ModuleNotFoundError: No module named 'ninja'"
**Cause**: django-ninja not installed
**Solution**: Added to requirements.txt automatically. Rebuild Docker:
```bash
docker compose up --build
```

### "ConfigError: STATIC_ROOT not configured"
**Cause**: Missing STATIC_ROOT in settings
**Solution**: Already fixed. STATIC_ROOT now set to `BASE_DIR / 'staticfiles'`

### "Permission denied: entrypoint.sh"
**Cause**: entrypoint.sh not executable
**Solution**: Added `RUN chmod +x /app/entrypoint.sh` to Dockerfile

### "Connection refused" (Database)
**Cause**: Database host wrong or DB not running
**Solution**: 
- For SQLite: No DB needed, works out of box
- For PostgreSQL: Ensure `DB_HOST` points to running PostgreSQL server
- In Docker Compose: Use service name as host (e.g., `db`)

### ".env file not loaded"
**Cause**: File in wrong location or Django not calling load_dotenv()
**Solution**: 
- Ensure .env is in root (`/opt/app/promo_py/.env`)
- Check settings.py has `load_dotenv()` imported and called

---

## 📋 Checklist for Deployment

- [ ] Generated unique `SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Configured `ALLOWED_HOSTS` with production domain
- [ ] Set `DB_ENGINE` to PostgreSQL
- [ ] Configured `DB_*` variables with production database
- [ ] Set strong `DB_PASSWORD`
- [ ] Tested connection to production database
- [ ] Added `.env` to `.gitignore`
- [ ] Verified `PYTHONUNBUFFERED=1`
- [ ] Backed up `.env` securely (password manager)

---

## Reference

| Variable | Default | Environment | Required |
|----------|---------|-------------|----------|
| DEBUG | True | Dev/Prod | No |
| SECRET_KEY | dev-key | Dev/Prod | No |
| ALLOWED_HOSTS | * | Dev/Prod | No |
| DB_ENGINE | sqlite3 | Dev/Prod | No |
| DB_NAME | N/A | Prod (PostgreSQL) | Yes if using PostgreSQL |
| DB_USER | N/A | Prod (PostgreSQL) | Yes if using PostgreSQL |
| DB_PASSWORD | N/A | Prod (PostgreSQL) | Yes if using PostgreSQL |
| DB_HOST | localhost | Prod (PostgreSQL) | Yes if using PostgreSQL |
| DB_PORT | 5432 | Prod (PostgreSQL) | Yes if using PostgreSQL |
| PYTHONUNBUFFERED | 1 | Docker | No |

