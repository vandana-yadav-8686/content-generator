"""User registration, login, and JWT — MongoDB Atlas storage."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.config import settings
from app.database.mongodb import ensure_user_indexes, get_users_collection
from app.models.user import UserCreate, UserLogin, UserPublic

logger = logging.getLogger(__name__)


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False


def _doc_to_public(doc: dict[str, Any]) -> UserPublic:
    return UserPublic(
        id=doc["user_id"],
        email=doc["email"],
        name=doc.get("name") or "",
        created_at=doc.get("created_at") or datetime.now(timezone.utc),
    )


def create_access_token(user_id: str, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": user_id, "email": email, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def register_user(data: UserCreate) -> tuple[UserPublic, str]:
    ensure_user_indexes()
    col = get_users_collection()
    email = data.email.strip().lower()

    if col.find_one({"email": email}):
        raise ValueError("An account with this email already exists")

    now = datetime.now(timezone.utc)
    user_id = str(uuid.uuid4())
    doc = {
        "user_id": user_id,
        "email": email,
        "name": data.name.strip(),
        "password_hash": _hash_password(data.password),
        "created_at": now,
        "updated_at": now,
    }
    col.insert_one(doc)
    logger.info("user_registered user_id=%s", user_id)
    user = _doc_to_public(doc)
    return user, create_access_token(user_id, email)


def login_user(data: UserLogin) -> tuple[UserPublic, str]:
    ensure_user_indexes()
    col = get_users_collection()
    email = data.email.strip().lower()
    doc = col.find_one({"email": email})
    if not doc or not _verify_password(data.password, doc.get("password_hash", "")):
        raise ValueError("Invalid email or password")
    user = _doc_to_public(doc)
    return user, create_access_token(doc["user_id"], email)


def get_user_by_id(user_id: str) -> UserPublic | None:
    doc = get_users_collection().find_one({"user_id": user_id})
    if not doc:
        return None
    return _doc_to_public(doc)


def verify_token(token: str) -> UserPublic | None:
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return None
        return get_user_by_id(str(user_id))
    except JWTError:
        return None
