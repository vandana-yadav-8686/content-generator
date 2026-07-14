import os
import secrets
from pathlib import Path

from cryptography.fernet import Fernet
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    encryption_key: str = ""
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days
    data_dir: str = "./data"
    cors_origins: str = "http://localhost:3000,http://localhost:3003"
    mongodb_uri: str = ""
    mongodb_db: str = "content_repurposing"
    openai_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def data_path(self) -> Path:
        path = Path(self.data_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def mongodb_enabled(self) -> bool:
        return bool(self.mongodb_uri.strip())


def _is_valid_fernet_key(key: str) -> bool:
    try:
        Fernet(key.strip().encode())
        return True
    except (ValueError, TypeError):
        return False


def _resolve_encryption_key() -> str:
    env_key = os.environ.get("ENCRYPTION_KEY", "").strip()
    if env_key:
        if _is_valid_fernet_key(env_key):
            return env_key
        raise RuntimeError(
            "ENCRYPTION_KEY must be a valid Fernet key (32 url-safe base64-encoded bytes). "
            "Render's auto-generated value is NOT valid. Generate one with: "
            'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" '
            "Then set the SAME key in local .env and Render Environment."
        )

    key_file = Path(settings.data_dir) / ".encryption_key"
    key_file.parent.mkdir(parents=True, exist_ok=True)

    if key_file.exists():
        stored = key_file.read_text().strip()
        if _is_valid_fernet_key(stored):
            return stored

    key = Fernet.generate_key().decode()
    key_file.write_text(key)
    return key


def _resolve_jwt_secret() -> str:
    env_secret = os.environ.get("JWT_SECRET", "").strip()
    if env_secret:
        return env_secret

    secret_file = Path(settings.data_dir) / ".jwt_secret"
    secret_file.parent.mkdir(parents=True, exist_ok=True)
    if secret_file.exists():
        return secret_file.read_text().strip()

    secret = secrets.token_urlsafe(48)
    secret_file.write_text(secret)
    return secret


settings = Settings()
settings.encryption_key = _resolve_encryption_key()
settings.jwt_secret = _resolve_jwt_secret()
if settings.openai_api_key and not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key
