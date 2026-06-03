from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()

# ── Config (read from .env) ───────────────────────────────────────────────────

SECRET_KEY      = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM       = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# ── Password context (bcrypt) ─────────────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Return bcrypt hash of a plain-text password.
    bcrypt silently truncates at 72 bytes — we raise early in the schema,
    but we also truncate here as a safety net.
    """
    # encode → truncate at 72 bytes → decode back to str
    safe_password = plain_password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.hash(safe_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if plain_password matches the stored hash."""
    safe_password = plain_password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.verify(safe_password, hashed_password)


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Sign a JWT with the given payload dict.
    `data` should contain at minimum {"sub": user_id, "email": ..., "user_type": ...}
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT.
    Returns the payload dict, or None if invalid / expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f"[JWT ERROR] {type(e).__name__}: {e}")   # shows exact reason in server console
        return None


# ── Convenience: seconds until token expires ─────────────────────────────────

def token_expires_in_seconds() -> int:
    return ACCESS_TOKEN_EXPIRE_MINUTES * 60
