"""
Generate JWT secret key script.

Usage:
    python scripts/generate_secret.py
"""

import secrets
import string


def generate_secret_key(length: int = 32) -> str:
    """Generate a secure random secret key."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_jwt_secret() -> str:
    """Generate a JWT secret key (base64 encoded)."""
    return secrets.token_urlsafe(32)


if __name__ == "__main__":
    print("🔑 Generating new secret keys...\n")
    
    # Regular secret key
    secret = generate_secret_key()
    print(f"APP_SECRET_KEY={secret}")
    
    # JWT secret
    jwt_secret = generate_jwt_secret()
    print(f"JWT_SECRET_KEY={jwt_secret}")
    
    print("\n💡 Add these to your .env file:")
    print(f"   SECRET_KEY={secret}")
    print(f"   AUTH_SECRET_KEY={jwt_secret}")
