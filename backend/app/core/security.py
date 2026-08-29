"""
Volt Authentication & Security Primitives
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from jose import jwt
import bcrypt
from backend.app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored bcrypt or pbkdf2 hash."""
    try:
        if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
            return bcrypt.checkpw(
                plain_password.encode("utf-8")[:72],
                hashed_password.encode("utf-8"),
            )
        # Fallback PBKDF2 hash check
        salt, h = hashed_password.split(":", 1)
        check = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
        return secrets.compare_digest(h, check)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Generate bcrypt hash from plain text password."""
    try:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8")[:72], salt)
        return hashed.decode("utf-8")
    except Exception:
        # Fallback PBKDF2-HMAC-SHA256
        salt = secrets.token_hex(16)
        h = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
        return f"{salt}:{h}"



def create_access_token(
    subject: Union[str, Any],
    role: str = "viewer",
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "role": role,
        "iss": "volt-platform",
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except Exception:
        return None


def generate_api_key(prefix: str = "volt_live_") -> tuple[str, str]:
    """Generate a raw API key and its SHA-256 hash for secure database storage."""
    raw_secret = secrets.token_urlsafe(32)
    api_key = f"{prefix}{raw_secret}"
    key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()
    return api_key, key_hash


def verify_api_key(raw_api_key: str, stored_hash: str) -> bool:
    """Verify raw API key matches the stored SHA-256 hash."""
    computed_hash = hashlib.sha256(raw_api_key.encode("utf-8")).hexdigest()
    return secrets.compare_digest(computed_hash, stored_hash)
