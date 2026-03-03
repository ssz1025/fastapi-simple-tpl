# FastAPI Project Template

## Project Structure

```
my-fastapi-project/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection & session
│   ├── redis_client.py         # Redis client management
│   ├── models/                 # SQLModel models
│   │   ├── __init__.py
│   │   └── base.py
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── health.py
│   └── core/                   # Core utilities
│       ├── __init__.py
│       └── security.py
├── config/
│   └── settings.yaml            # Environment-specific settings
├── tests/                       # Test files
├── .env                         # Environment variables (gitignored)
├── .env.example                 # Example environment file
├── requirements.txt             # Python dependencies
├── requirements-dev.txt        # Dev dependencies
├── requirements-prod.txt        # Production dependencies
├── alembic.ini                  # Alembic configuration
└── README.md
```

## Quick Start

### 1. Install Dependencies

```bash
# Development
pip install -r requirements.txt

# Production
pip install -r requirements-prod.txt
```

### 2. Configure Environment

Copy and edit configuration:

```bash
cp .env.example .env
cp config/settings.yaml config/settings.yaml.bak
```

Edit `.env`:
```env
ENVIRONMENT=development
APP_NAME=my-fastapi-app
APP_HOST=0.0.0.0
APP_PORT=8000
```

Edit `config/settings.yaml` to configure database and Redis.

### 3. Run

```bash
# Development
uvicorn app.main:app --reload --env-file .env

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Configuration Guide

### Database Configuration

Edit `config/settings.yaml`:

```yaml
database:
  # Options: sqlite, mysql, postgresql
  type: sqlite
  # SQLite
  sqlite:
    path: "./data/app.db"
  # MySQL
  mysql:
    host: localhost
    port: 3306
    username: root
    password: your_password
    database: your_database
    charset: utf8mb4
  # PostgreSQL
  postgresql:
    host: localhost
    port: 5432
    username: postgres
    password: your_password
    database: your_database
```

### Redis Configuration

Edit `config/settings.yaml`:

```yaml
redis:
  enabled: true
  # Options: single, cluster
  mode: single
  # Single Redis
  single:
    host: localhost
    port: 6379
    password: your_password  # optional
    db: 0
  # Redis Cluster
  cluster:
    nodes:
      - host: localhost
        port: 7001
      - host: localhost
        port: 7002
      - host: localhost
        port: 7003
```

### Environment-Specific Configuration

Create separate config files:

- `config/settings.yaml` - Base config (shared)
- `config/settings.dev.yaml` - Development overrides
- `config/settings.prod.yaml` - Production overrides

The application will automatically load environment-specific overrides.
# fastapi-simple-tpl
