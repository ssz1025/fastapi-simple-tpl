# FastAPI Project Template | FastAPI 项目模板

[English](#english) | [中文](#中文)

---

## English

### Project Overview

A production-ready FastAPI project template with:
- **Layered Architecture**: Routers → Services → Schemas
- **Multiple Database Support**: SQLite, MySQL, PostgreSQL
- **Redis Support**: Single node or Cluster mode
- **JWT Authentication**: Complete auth system
- **Docker & Alembic**: Production deployment ready
- **Testing**: Pytest with async support

### Project Structure

```
my-fastapi-project/
├── app/
│   ├── main.py                 # Application entry
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection
│   ├── redis_client.py         # Redis client
│   ├── schemas/                # Pydantic schemas
│   │   └── __init__.py
│   ├── services/               # Business logic
│   │   └── user_service.py
│   ├── routers/v1/            # API endpoints
│   │   ├── auth.py
│   │   └── users.py
│   ├── core/                  # Core utilities
│   │   └── security.py
│   └── utils/                 # Helper functions
├── config/
│   ├── settings.yaml          # Base config
│   ├── settings.dev.yaml      # Dev overrides
│   └── settings.prod.yaml     # Prod overrides
├── scripts/                   # Utility scripts
├── alembic/                   # Database migrations
├── tests/                     # Test files
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

### Quick Start

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
ENVIRONMENT=development
APP_HOST=0.0.0.0
APP_PORT=8000
```

Edit `config/settings.yaml` for database/Redis configuration.

#### 3. Initialize Database

```bash
python scripts/init_db.py
```

#### 4. Run

```bash
# Development
uvicorn app.main:app --reload

# Production
python scripts/run.py --prod
```

### Configuration

#### Database (`config/settings.yaml`)

```yaml
database:
  type: sqlite  # or mysql, postgresql
  sqlite:
    path: "./data/app.db"
  mysql:
    host: localhost
    port: 3306
    username: root
    password: your_password
    database: your_database
  postgresql:
    host: localhost
    port: 5432
    username: postgres
    password: your_password
    database: your_database
```

#### Redis (`config/settings.yaml`)

```yaml
redis:
  enabled: true
  mode: single  # or cluster
  single:
    host: localhost
    port: 6379
    password: your_password  # optional
    db: 0
  cluster:
    nodes:
      - host: localhost
        port: 7001
      - host: localhost
        port: 7002
      - host: localhost
        port: 7003
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | User registration |
| `/api/v1/auth/login` | POST | User login (JWT) |
| `/api/v1/auth/me` | GET | Current user info |
| `/api/v1/users` | GET | List users |
| `/api/v1/users/{id}` | GET/PUT/DELETE | User CRUD |
| `/api/v1/health` | GET | Health check |

### Docker

```bash
# Development
docker-compose up --build

# Production
# Edit docker-compose.yml: target: production
docker-compose up --build
```

### Scripts

| Script | Usage |
|--------|-------|
| `python scripts/init_db.py` | Initialize database |
| `python scripts/create_superuser.py --email x --username x --password x` | Create admin |
| `python scripts/generate_secret.py` | Generate keys |
| `python scripts/db_backup.py backup` | Backup DB |
| `python scripts/run_tests.py --cov` | Run tests |

---

## 中文

### 项目概述

一个生产级别的 FastAPI 项目模板，包含：

- **分层架构**: Routers → Services → Schemas
- **多数据库支持**: SQLite、MySQL、PostgreSQL
- **Redis 支持**: 单节点或集群模式
- **JWT 认证**: 完整的认证系统
- **Docker & Alembic**: 生产环境部署就绪
- **测试**: Pytest 异步支持

### 项目结构

```
my-fastapi-project/
├── app/
│   ├── main.py                 # 应用入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   ├── redis_client.py         # Redis 客户端
│   ├── schemas/                # Pydantic 模型
│   │   └── __init__.py
│   ├── services/               # 业务逻辑
│   │   └── user_service.py
│   ├── routers/v1/            # API 路由
│   │   ├── auth.py
│   │   └── users.py
│   ├── core/                   # 核心工具
│   │   └── security.py
│   └── utils/                 # 辅助函数
├── config/
│   ├── settings.yaml          # 基础配置
│   ├── settings.dev.yaml      # 开发环境覆盖
│   └── settings.prod.yaml     # 生产环境覆盖
├── scripts/                   # 辅助脚本
├── alembic/                   # 数据库迁移
├── tests/                     # 测试文件
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

### 快速开始

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 配置环境

```bash
cp .env.example .env
```

编辑 `.env`:
```env
ENVIRONMENT=development
APP_HOST=0.0.0.0
APP_PORT=8000
```

编辑 `config/settings.yaml` 配置数据库和 Redis。

#### 3. 初始化数据库

```bash
python scripts/init_db.py
```

#### 4. 运行

```bash
# 开发环境
uvicorn app.main:app --reload

# 生产环境
python scripts/run.py --prod
```

### 配置

#### 数据库 (`config/settings.yaml`)

```yaml
database:
  type: sqlite  # 或 mysql, postgresql
  sqlite:
    path: "./data/app.db"
  mysql:
    host: localhost
    port: 3306
    username: root
    password: 你的密码
    database: 你的数据库
  postgresql:
    host: localhost
    port: 5432
    username: postgres
    password: 你的密码
    database: 你的数据库
```

#### Redis (`config/settings.yaml`)

```yaml
redis:
  enabled: true
  mode: single  # 或 cluster
  single:
    host: localhost
    port: 6379
    password: 你的密码  # 可选
    db: 0
  cluster:
    nodes:
      - host: localhost
        port: 7001
      - host: localhost
        port: 7002
      - host: localhost
        port: 7003
```

### API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/auth/register` | POST | 用户注册 |
| `/api/v1/auth/login` | POST | 用户登录 (JWT) |
| `/api/v1/auth/me` | GET | 当前用户信息 |
| `/api/v1/users` | GET | 用户列表 |
| `/api/v1/users/{id}` | GET/PUT/DELETE | 用户 CRUD |
| `/api/v1/health` | GET | 健康检查 |

### Docker

```bash
# 开发环境
docker-compose up --build

# 生产环境
# 编辑 docker-compose.yml: target: production
docker-compose up --build
```

### 脚本

| 脚本 | 用途 |
|------|------|
| `python scripts/init_db.py` | 初始化数据库 |
| `python scripts/create_superuser.py --email x --username x --password x` | 创建管理员 |
| `python scripts/generate_secret.py` | 生成密钥 |
| `python scripts/db_backup.py backup` | 备份数据库 |
| `python scripts/run_tests.py --cov` | 运行测试 |

---

## Environment Variables | 环境变量

```env
# Application
ENVIRONMENT=development
APP_HOST=0.0.0.0
APP_PORT=8000
APP_NAME=FastAPI Application

# Database (configure in config/settings.yaml)
# DATABASE_TYPE=sqlite|mysql|postgresql

# Redis (configure in config/settings.yaml)
# REDIS_ENABLED=true|false

# Auth
# AUTH_SECRET_KEY=your-secret-key
# AUTH_ALGORITHM=HS256
# AUTH_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## License | 许可证

MIT License - See [LICENSE](LICENSE) file for details.

---

MIT License
