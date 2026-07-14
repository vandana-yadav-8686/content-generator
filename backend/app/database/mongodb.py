"""MongoDB Atlas client — singleton with indexes for production querying."""

from __future__ import annotations

import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

_client: Any = None
_indexes_ready = False


def get_mongo_client():
    global _client
    if not settings.mongodb_enabled:
        return None
    if _client is not None:
        return _client

    from pymongo import MongoClient

    # Single long-lived client for the FastAPI process (reuse across requests).
    # maxPoolSize sized for moderate concurrent generation traffic.
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


def get_content_collection():
    client = get_mongo_client()
    if client is None:
        raise RuntimeError("MongoDB is not configured (set MONGODB_URI)")
    return client[settings.mongodb_db]["repurposed_content"]


def ensure_indexes() -> None:
    global _indexes_ready
    if _indexes_ready or not settings.mongodb_enabled:
        return
    try:
        col = get_content_collection()
        col.create_index("created_at")
        col.create_index("workflow_id", unique=False)
        col.create_index("workflow_status")
        col.create_index("provider_id")
        col.create_index("prompt_version")
        col.create_index([("tenant_id", 1), ("created_at", -1)])
        # Future vector search: create Atlas Vector Search index in Atlas UI on `embedding`
        _indexes_ready = True
    except Exception:
        logger.exception("Failed creating Mongo indexes")
