import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    encryption_key: str = ""
    database_path: str = "./data/settings.db"
    cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def db_path(self) -> Path:
        path = Path(self.database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


def _resolve_encryption_key() -> str:
    if os.environ.get("ENCRYPTION_KEY"):
        return os.environ["ENCRYPTION_KEY"]

    key_file = Path("./data/.encryption_key")
    key_file.parent.mkdir(parents=True, exist_ok=True)

    if key_file.exists():
        return key_file.read_text().strip()

    from cryptography.fernet import Fernet
    key = Fernet.generate_key().decode()
    key_file.write_text(key)
    return key


settings = Settings()
settings.encryption_key = _resolve_encryption_key()
