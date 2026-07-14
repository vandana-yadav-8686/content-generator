import logging
import sqlite3
from pathlib import Path
from typing import Optional

from app.config import settings
from app.models.schemas import ProviderId, ProviderConfig
from app.services.encryption import encryption_service

logger = logging.getLogger(__name__)

class SettingsRepository:
    def __init__(self) -> None:
        self._init_db()

    def _init_db(self) -> None:
        db_path = settings.db_path
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS provider_settings (
                    provider_id TEXT PRIMARY KEY,
                    enabled INTEGER NOT NULL DEFAULT 0,
                    encrypted_api_key TEXT,
                    model TEXT NOT NULL DEFAULT '',
                    base_url TEXT
                )
                """
            )
            conn.commit()

    def get_all(self) -> dict[ProviderId, ProviderConfig]:
        result: dict[ProviderId, ProviderConfig] = {}
        with sqlite3.connect(settings.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM provider_settings").fetchall()
            for row in rows:
                provider_id = ProviderId(row["provider_id"])
                api_key = None
                if row["encrypted_api_key"]:
                    api_key = encryption_service.decrypt(row["encrypted_api_key"])
                result[provider_id] = ProviderConfig(
                    provider_id=provider_id,
                    enabled=bool(row["enabled"]),
                    api_key=api_key,
                    model=row["model"] or "",
                    base_url=row["base_url"],
                )
        return result

    def get(self, provider_id: ProviderId) -> Optional[ProviderConfig]:
        return self.get_all().get(provider_id)

    def save(self, config: ProviderConfig) -> None:
        encrypted_key = None
        if config.api_key:
            encrypted_key = encryption_service.encrypt(config.api_key)

        with sqlite3.connect(settings.db_path) as conn:
            existing = conn.execute(
                "SELECT encrypted_api_key FROM provider_settings WHERE provider_id = ?",
                (config.provider_id.value,),
            ).fetchone()

            # Keep existing key if not provided in update
            if encrypted_key is None and existing and existing[0]:
                encrypted_key = existing[0]

            conn.execute(
                """
                INSERT INTO provider_settings (provider_id, enabled, encrypted_api_key, model, base_url)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(provider_id) DO UPDATE SET
                    enabled = excluded.enabled,
                    encrypted_api_key = COALESCE(excluded.encrypted_api_key, provider_settings.encrypted_api_key),
                    model = excluded.model,
                    base_url = excluded.base_url
                """,
                (
                    config.provider_id.value,
                    int(config.enabled),
                    encrypted_key,
                    config.model,
                    config.base_url,
                ),
            )
            conn.commit()

    def get_active_provider(self) -> Optional[ProviderConfig]:
        try:
            all_configs = self.get_all()
        except ValueError as exc:
            logger.exception("settings_decrypt_failed")
            raise ValueError(
                "Could not read saved API keys. Re-save your key in Settings. "
                "On Render, set a fixed ENCRYPTION_KEY env variable."
            ) from exc
        for config in all_configs.values():
            if config.enabled and config.api_key:
                return config
        return None


settings_repository = SettingsRepository()