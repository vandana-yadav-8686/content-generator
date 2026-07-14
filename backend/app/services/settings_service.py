"""Provider settings persistence — MongoDB Atlas (encrypted API keys)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from app.config import settings
from app.context import get_user_id
from app.database.mongodb import ensure_settings_indexes, get_settings_collection
from app.models.schemas import ProviderConfig, ProviderId
from app.providers.factory import ProviderFactory
from app.services.encryption import encryption_service

logger = logging.getLogger(__name__)


class SettingsRepository:
    def __init__(self) -> None:
        if settings.mongodb_enabled:
            ensure_settings_indexes()

    def _require_user_id(self) -> str:
        user_id = get_user_id()
        if not user_id:
            raise RuntimeError("Authentication required to access provider settings.")
        return user_id

    def _user_query(self, extra: dict | None = None) -> dict:
        q = {"user_id": self._require_user_id()}
        if extra:
            q.update(extra)
        return q

    def ensure_provider_defaults(self) -> None:
        """Seed all known providers in MongoDB for the current user."""
        try:
            col = self._collection()
            user_id = self._require_user_id()
        except Exception:
            logger.exception("provider_seed_skipped")
            return

        now = datetime.now(timezone.utc)
        inserted = 0
        for provider_id in ProviderId:
            meta = ProviderFactory.get_provider_class(provider_id).metadata
            result = col.update_one(
                {"user_id": user_id, "provider_id": provider_id.value},
                {
                    "$setOnInsert": {
                        "user_id": user_id,
                        "provider_id": provider_id.value,
                        "enabled": False,
                        "encrypted_api_key": None,
                        "model": meta.default_model,
                        "base_url": meta.default_base_url,
                        "created_at": now,
                        "updated_at": now,
                    }
                },
                upsert=True,
            )
            if result.upserted_id is not None:
                inserted += 1

        if inserted:
            logger.info("seeded provider_settings user=%s count=%s", user_id, inserted)

    def _decrypt_api_key(self, encrypted: str | None, provider_id: str) -> str | None:
        if not encrypted:
            return None
        try:
            return encryption_service.decrypt(encrypted)
        except ValueError:
            logger.warning(
                "Could not decrypt API key for provider=%s — re-save in Settings "
                "(ENCRYPTION_KEY may have changed since the key was stored).",
                provider_id,
            )
            return None

    def _collection(self):
        if not settings.mongodb_enabled:
            raise RuntimeError(
                "MongoDB is required for provider settings. Set MONGODB_URI in your environment."
            )
        return get_settings_collection()

    def get_all(self) -> dict[ProviderId, ProviderConfig]:
        result: dict[ProviderId, ProviderConfig] = {}
        for doc in self._collection().find(self._user_query()):
            try:
                provider_id = ProviderId(doc["provider_id"])
            except ValueError:
                logger.warning("skipping unknown provider_id=%r", doc.get("provider_id"))
                continue
            encrypted = doc.get("encrypted_api_key")
            api_key = self._decrypt_api_key(encrypted, provider_id.value)
            result[provider_id] = ProviderConfig(
                provider_id=provider_id,
                enabled=bool(doc.get("enabled", False)),
                api_key=api_key,
                model=doc.get("model") or "",
                base_url=doc.get("base_url"),
            )
        return result

    def get_all_safe(self) -> dict[ProviderId, ProviderConfig]:
        """Load saved provider settings; return {} if MongoDB is unavailable."""
        try:
            return self.get_all()
        except Exception:
            logger.exception("settings_get_all_failed")
            return {}

    def get(self, provider_id: ProviderId) -> Optional[ProviderConfig]:
        doc = self._collection().find_one(
            self._user_query({"provider_id": provider_id.value})
        )
        if not doc:
            return None
        api_key = None
        encrypted = doc.get("encrypted_api_key")
        api_key = self._decrypt_api_key(encrypted, provider_id.value)
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
                self._user_query({"provider_id": config.provider_id.value}),
                {"encrypted_api_key": 1},
            )
            if existing and existing.get("encrypted_api_key"):
                encrypted_key = existing["encrypted_api_key"]

        user_id = self._require_user_id()
        now = datetime.now(timezone.utc)
        self._collection().update_one(
            {"user_id": user_id, "provider_id": config.provider_id.value},
            {
                "$set": {
                    "user_id": user_id,
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
            for doc in self._collection().find(self._user_query({"enabled": True})):
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
