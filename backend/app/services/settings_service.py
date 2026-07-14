"""Provider settings persistence — MongoDB Atlas (encrypted API keys)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from app.config import settings
from app.database.mongodb import ensure_settings_indexes, get_settings_collection
from app.models.schemas import ProviderConfig, ProviderId
from app.services.encryption import encryption_service

logger = logging.getLogger(__name__)


class SettingsRepository:
    def __init__(self) -> None:
        if settings.mongodb_enabled:
            ensure_settings_indexes()

    def _collection(self):
        if not settings.mongodb_enabled:
            raise RuntimeError(
                "MongoDB is required for provider settings. Set MONGODB_URI in your environment."
            )
        return get_settings_collection()

    def get_all(self) -> dict[ProviderId, ProviderConfig]:
        result: dict[ProviderId, ProviderConfig] = {}
        for doc in self._collection().find({}):
            provider_id = ProviderId(doc["provider_id"])
            api_key = None
            encrypted = doc.get("encrypted_api_key")
            if encrypted:
                api_key = encryption_service.decrypt(encrypted)
            result[provider_id] = ProviderConfig(
                provider_id=provider_id,
                enabled=bool(doc.get("enabled", False)),
                api_key=api_key,
                model=doc.get("model") or "",
                base_url=doc.get("base_url"),
            )
        return result

    def get(self, provider_id: ProviderId) -> Optional[ProviderConfig]:
        doc = self._collection().find_one({"provider_id": provider_id.value})
        if not doc:
            return None
        api_key = None
        encrypted = doc.get("encrypted_api_key")
        if encrypted:
            api_key = encryption_service.decrypt(encrypted)
        return ProviderConfig(
            provider_id=provider_id,
            enabled=bool(doc.get("enabled", False)),
            api_key=api_key,
            model=doc.get("model") or "",
            base_url=doc.get("base_url"),
        )

    def save(self, config: ProviderConfig) -> None:
        encrypted_key = None
        if config.api_key:
            encrypted_key = encryption_service.encrypt(config.api_key)
        else:
            existing = self._collection().find_one(
                {"provider_id": config.provider_id.value},
                {"encrypted_api_key": 1},
            )
            if existing and existing.get("encrypted_api_key"):
                encrypted_key = existing["encrypted_api_key"]

        now = datetime.now(timezone.utc)
        self._collection().update_one(
            {"provider_id": config.provider_id.value},
            {
                "$set": {
                    "provider_id": config.provider_id.value,
                    "enabled": bool(config.enabled),
                    "encrypted_api_key": encrypted_key,
                    "model": config.model or "",
                    "base_url": config.base_url,
                    "updated_at": now,
                },
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
        )
        logger.info("saved provider_settings provider=%s enabled=%s", config.provider_id.value, config.enabled)

    def get_active_provider(self) -> Optional[ProviderConfig]:
        try:
            for doc in self._collection().find({"enabled": True}):
                provider_id = ProviderId(doc["provider_id"])
                config = self.get(provider_id)
                if config and config.api_key:
                    return config
        except ValueError as exc:
            logger.exception("settings_decrypt_failed")
            raise ValueError(
                "Could not read saved API keys. Re-save your key in Settings. "
                "Ensure ENCRYPTION_KEY is set and does not change between deploys."
            ) from exc
        return None


settings_repository = SettingsRepository()
