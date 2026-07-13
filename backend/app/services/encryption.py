from cryptography.fernet import Fernet, InvalidToken

from app.config import settings


class EncryptionService:
    def __init__(self) -> None:
        self._fernet = Fernet(settings.encryption_key.encode())

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except InvalidToken:
            raise ValueError("Failed to decrypt API key")

    @staticmethod
    def mask_key(api_key: str) -> str:
        if len(api_key) <= 8:
            return "****"
        return f"{api_key[:4]}...{api_key[-4:]}"


encryption_service = EncryptionService()
