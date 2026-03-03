"""
Pytest configuration and fixtures.

Provides:
- Database fixtures (async)
- Test client fixtures
- Authentication fixtures
- Redis fixtures
"""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db_manager
from app.main import app
from app.models.user import User
from app.core.security import get_password_hash, create_access_token
from app.config import get_settings


# =============================================================================
# Settings
# =============================================================================

settings = get_settings()


# =============================================================================
# Test Database URL
# =============================================================================

# Use SQLite in-memory for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# =============================================================================
# Async Engine for Tests
# =============================================================================

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


test_session_factory = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with test_session_factory() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override."""
    
    # Override database dependency
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db_manager] = lambda: type('FakeDB', (), {
        'session': lambda: db_session,
        'async_engine': test_engine,
    })()
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def superuser(db_session: AsyncSession) -> User:
    """Create a superuser for testing."""
    user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("adminpassword123"),
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_token(test_user: User) -> str:
    """Create authentication token for test user."""
    return create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email}
    )


@pytest_asyncio.fixture
async def superuser_token(superuser: User) -> str:
    """Create authentication token for superuser."""
    return create_access_token(
        data={"sub": str(superuser.id), "email": superuser.email}
    )


@pytest_asyncio.fixture
async def auth_headers(auth_token: str) -> dict:
    """Create authorization headers."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest_asyncio.fixture
async def superuser_headers(superuser_token: str) -> dict:
    """Create superuser authorization headers."""
    return {"Authorization": f"Bearer {superuser_token}"}


# =============================================================================
# Helper Functions
# =============================================================================

def create_test_user_data(
    email: str = "newuser@example.com",
    username: str = "newuser",
    password: str = "password123"
) -> dict:
    """Helper to create test user data."""
    return {
        "email": email,
        "username": username,
        "password": password,
    }
