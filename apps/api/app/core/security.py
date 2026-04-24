import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.core.config import settings

PBKDF2_PREFIX = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 600_000


def create_password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    ).hex()
    return f"{PBKDF2_PREFIX}${PBKDF2_ITERATIONS}${salt}${derived}"


def verify_password(password: str, hashed_password: str) -> bool:
    if hashed_password.startswith(f"{PBKDF2_PREFIX}$"):
        try:
            _, iterations_str, salt, expected = hashed_password.split("$", 3)
            iterations = int(iterations_str)
        except ValueError:
            return False

        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        ).hex()
        return hmac.compare_digest(actual, expected)

    # Backward compatibility for existing bcrypt hashes.
    try:
        import bcrypt

        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
