"""MongoDB Atlas client — singleton with indexes for production querying."""

from __future__ import annotations

import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

_client: Any = None
_content_indexes_ready = False
_settings_indexes_ready = False


def get_mongo_client():
    global _client
    if not settings.mongodb_enabled:
        return None
    if _client is not None:
        return _client

    from pymongo import MongoClient

    _client = MongoClient(
        settings.mongodb_uri,
        maxPoolSize=50,
        minPoolSize=0,
        maxIdleTimeMS=60_000,
        serverSelectionTimeoutMS=5_000,
        connectTimeoutMS=5_000,
        retryWrites=True,
    )
    try:
        _client.admin.command("ping")
        logger.info("MongoDB connected db=%s", settings.mongodb_db)
    except Exception:
        logger.exception("MongoDB ping failed — check MONGODB_URI")
        raise
    return _client


def _require_client():
    client = get_mongo_client()
    if client is None:
        raise RuntimeError(
            "MongoDB is not configured. Set MONGODB_URI in your environment."
        )
    return client


def get_content_collection():
    return _require_client()[settings.mongodb_db]["repurposed_content"]


def get_settings_collection():
    """Provider API keys and config (encrypted)."""
    return _require_client()[settings.mongodb_db]["provider_settings"]


def ensure_content_indexes() -> None:
    global _content_indexes_ready
    if _content_indexes_ready or not settings.mongodb_enabled:
        return
    try:
        col = get_content_collection()
        col.create_index("created_at")
        col.create_index("workflow_id", unique=False)
        col.create_index("workflow_status")
        col.create_index("provider_id")
        col.create_index("prompt_version")
        col.create_index([("tenant_id", 1), ("created_at", -1)])
        _content_indexes_ready = True
    except Exception:
        logger.exception("Failed creating content Mongo indexes")


def ensure_settings_indexes() -> None:
    global _settings_indexes_ready
    if _settings_indexes_ready or not settings.mongodb_enabled:
        return
    try:
        col = get_settings_collection()
        col.create_index("provider_id", unique=True)
        col.create_index("enabled")
        col.create_index("updated_at")
        _settings_indexes_ready = True
    except Exception:
        logger.exception("Failed creating settings Mongo indexes")


def ensure_indexes() -> None:
    """Ensure indexes for all collections."""
    ensure_content_indexes()
    ensure_settings_indexes()
