"""
Configuration management for FastAPI application.

Loads settings from YAML files with environment-specific overrides.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

import yaml


class DatabaseSQLiteConfig:
    """SQLite database configuration."""
    def __init__(self, path: str = "./data/app.db", check_same_thread: bool = False):
        self.path = path
        self.check_same_thread = check_same_thread


class DatabaseMySQLConfig:
    """MySQL database configuration."""
    def __init__(self, host: str = "localhost", port: int = 3306, username: str = "root",
                 password: str = "", database: str = "app_db", charset: str = "utf8mb4"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.charset = charset

    @property
    def url(self) -> str:
        pw = f":{self.password}" if self.password else ""
        return f"mysql+aiomysql://{self.username}{pw}@{self.host}:{self.port}/{self.database}?charset={self.charset}"

    @property
    def sync_url(self) -> str:
        pw = f":{self.password}" if self.password else ""
        return f"mysql+pymysql://{self.username}{pw}@{self.host}:{self.port}/{self.database}?charset={self.charset}"


class DatabasePostgreSQLConfig:
    """PostgreSQL database configuration."""
    def __init__(self, host: str = "localhost", port: int = 5432, username: str = "postgres",
                 password: str = "", database: str = "app_db"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database

    @property
    def url(self) -> str:
        pw = f":{self.password}" if self.password else ""
        return f"postgresql+asyncpg://{self.username}{pw}@{self.host}:{self.port}/{self.database}"

    @property
    def sync_url(self) -> str:
        pw = f":{self.password}" if self.password else ""
        return f"postgresql://{self.username}{pw}@{self.host}:{self.port}/{self.database}"


class DatabaseConfig:
    """Database configuration."""
    def __init__(self, type: str = "sqlite", echo: bool = False, pool_size: int = 5,
                 max_overflow: int = 10, pool_recycle: int = 3600, pool_pre_ping: bool = True,
                 sqlite: Dict = None, mysql: Dict = None, postgresql: Dict = None):
        self.type = type
        self.echo = echo
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_recycle = pool_recycle
        self.pool_pre_ping = pool_pre_ping
        self.sqlite = DatabaseSQLiteConfig(**(sqlite or {}))
        self.mysql = DatabaseMySQLConfig(**(mysql or {}))
        self.postgresql = DatabasePostgreSQLConfig(**(postgresql or {}))

    @property
    def url(self) -> str:
        if self.type == "sqlite":
            return f"sqlite+aiosqlite:///{self.sqlite.path}"
        elif self.type == "mysql":
            return self.mysql.url
        elif self.type == "postgresql":
            return self.postgresql.url
        raise ValueError(f"Unsupported database type: {self.type}")

    @property
    def sync_url(self) -> str:
        if self.type == "sqlite":
            return f"sqlite:///{self.sqlite.path}"
        elif self.type == "mysql":
            return self.mysql.sync_url
        elif self.type == "postgresql":
            return self.postgresql.sync_url
        raise ValueError(f"Unsupported database type: {self.type}")


class RedisSingleConfig:
    """Single Redis node configuration."""
    def __init__(self, host: str = "localhost", port: int = 6379, password: str = "", db: int = 0):
        self.host = host
        self.port = port
        self.password = password
        self.db = db

    @property
    def url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class RedisClusterNode:
    """Redis cluster node."""
    def __init__(self, host: str = "localhost", port: int = 7001):
        self.host = host
        self.port = port


class RedisClusterConfig:
    """Redis cluster configuration."""
    def __init__(self, nodes: List[Dict] = None):
        self.nodes = [RedisClusterNode(**n) for n in (nodes or [])]

    @property
    def urls(self) -> List[str]:
        return [f"redis://{n.host}:{n.port}" for n in self.nodes]


class RedisConfig:
    """Redis configuration."""
    def __init__(self, enabled: bool = True, mode: str = "single", socket_timeout: int = 5,
                 socket_connect_timeout: int = 5, retry_on_timeout: bool = True,
                 max_connections: int = 10, single: Dict = None, cluster: Dict = None):
        self.enabled = enabled
        self.mode = mode
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.retry_on_timeout = retry_on_timeout
        self.max_connections = max_connections
        self.single = RedisSingleConfig(**(single or {}))
        self.cluster = RedisClusterConfig(**(cluster or {}))

    @property
    def url(self) -> str:
        return self.single.url

    @property
    def urls(self) -> List[str]:
        if self.mode == "cluster":
            return self.cluster.urls
        return [self.single.url]


class AppConfig:
    """Application configuration."""
    def __init__(self, name: str = "FastAPI Application", version: str = "1.0.0",
                 debug: bool = False, api_prefix: str = "/api/v1", cors_origins: List[str] = None):
        self.name = name
        self.version = version
        self.debug = debug
        self.api_prefix = api_prefix
        self.cors_origins = cors_origins or ["http://localhost:3000"]


class AuthConfig:
    """Authentication configuration."""
    def __init__(self, secret_key: str = "your-secret-key-change-in-production",
                 algorithm: str = "HS256", access_token_expire_minutes: int = 30,
                 refresh_token_expire_days: int = 7):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days


class LoggingConfig:
    """Logging configuration."""
    def __init__(self, level: str = "INFO", format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                 file: Dict = None):
        file = file or {}
        self.level = level
        self.format = format
        self.file_enabled = file.get("enabled", False)
        self.file_path = file.get("path", "./logs/app.log")
        self.max_bytes = file.get("max_bytes", 10485760)
        self.backup_count = file.get("backup_count", 5)


class Settings:
    """Application settings."""
    
    def __init__(self, environment: str = "development", app_host: str = "0.0.0.0", app_port: int = 8000,
                 app: Dict = None, auth: Dict = None, database: Dict = None, redis: Dict = None, 
                 logging_config: Dict = None):
        self.environment = environment
        self.app_host = app_host
        self.app_port = app_port
        self.app = AppConfig(**(app or {}))
        self.auth = AuthConfig(**(auth or {}))
        self.database = DatabaseConfig(**(database or {}))
        self.redis = RedisConfig(**(redis or {}))
        self.logging = LoggingConfig(**(logging_config or {}))

    @classmethod
    def load_from_yaml(cls, config_dir: Path = Path("config")) -> Dict:
        env = os.getenv("ENVIRONMENT", "development")
        base_config_path = config_dir / "settings.yaml"
        config = {}
        
        if base_config_path.exists():
            with open(base_config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        
        env_config_path = config_dir / f"settings.{env}.yaml"
        if env_config_path.exists():
            with open(env_config_path, "r", encoding="utf-8") as f:
                env_config = yaml.safe_load(f) or {}
                config = cls._merge_config(config, env_config)
        
        return config

    @staticmethod
    def _merge_config(base: Dict, override: Dict) -> Dict:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Settings._merge_config(result[key], value)
            else:
                result[key] = value
        return result


@lru_cache()
def get_settings() -> Settings:
    config_dict = Settings.load_from_yaml()
    
    return Settings(
        environment=os.getenv("ENVIRONMENT", "development"),
        app_host=os.getenv("APP_HOST", "0.0.0.0"),
        app_port=int(os.getenv("APP_PORT", "8000")),
        app=config_dict.get("app"),
        auth=config_dict.get("auth"),
        database=config_dict.get("database"),
        redis=config_dict.get("redis"),
        logging_config=config_dict.get("logging"),
    )
