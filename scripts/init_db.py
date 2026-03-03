"""
Database initialization script.

Usage:
    python scripts/init_db.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db_manager
from app.models.user import User
from app.core.security import get_password_hash


async def init_db():
    """Initialize database with tables and seed data."""
    print("🚀 Initializing database...")
    
    db_manager = get_db_manager()
    
    # Create tables
    print("📋 Creating tables...")
    await db_manager.init_db()
    print("✅ Tables created successfully")
    
    # Seed initial data
    print("🌱 Seeding initial data...")
    
    async with db_manager.session() as session:
        # Check if admin user exists
        from sqlalchemy.future import select
        result = await session.execute(
            select(User).where(User.email == "admin@example.com")
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin_user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True,
            )
            session.add(admin_user)
            print("✅ Admin user created (admin@example.com / admin123)")
        
        # Create test user
        result = await session.execute(
            select(User).where(User.email == "user@example.com")
        )
        test_user = result.scalar_one_or_none()
        
        if not test_user:
            test_user = User(
                email="user@example.com",
                username="user",
                hashed_password=get_password_hash("user123"),
                is_active=True,
                is_superuser=False,
            )
            session.add(test_user)
            print("✅ Test user created (user@example.com / user123)")
        
        await session.commit()
    
    print("✨ Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(init_db())
