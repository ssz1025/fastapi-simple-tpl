"""
Create superuser script.

Usage:
    python scripts/create_superuser.py --email admin@example.com --username admin --password yourpassword
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db_manager
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.future import select


async def create_superuser(email: str, username: str, password: str):
    """Create a superuser account."""
    print(f"👤 Creating superuser: {email}")
    
    db_manager = get_db_manager()
    
    async with db_manager.session() as session:
        # Check if user exists
        result = await session.execute(
            select(User).where(User.email == email)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"⚠️  User {email} already exists!")
            
            # Update to superuser
            existing.is_superuser = True
            existing.is_active = True
            existing.hashed_password = get_password_hash(password)
            await session.commit()
            print(f"✅ User {email} updated to superuser")
            return
        
        # Create new user
        user = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True,
        )
        session.add(user)
        await session.commit()
        
        print(f"✅ Superuser created: {email}")
        print(f"   Username: {username}")
        print(f"   Password: {password}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a superuser")
    parser.add_argument("--email", required=True, help="User email")
    parser.add_argument("--username", required=True, help="Username")
    parser.add_argument("--password", required=True, help="Password")
    
    args = parser.parse_args()
    
    asyncio.run(create_superuser(args.email, args.username, args.password))
