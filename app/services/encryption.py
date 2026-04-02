"""
app/services/encryption.py
AES-256-GCM encryption service for sensitive data at rest.
"""

from __future__ import annotations

import base64
import json
import os
from typing import Any, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings


class EncryptionError(Exception):
    pass


class EncryptionService:
    PBKDF2_ITERATIONS = 100000
    KEY_LENGTH = 32
    SALT_LENGTH = 16
    NONCE_LENGTH = 12
    
    def __init__(self, master_key: Optional[str] = None):
        key = master_key or settings.ENCRYPTION_KEY
        if not key:
            raise EncryptionError("Encryption key not configured")
        if len(key) < 32:
            raise EncryptionError("Encryption key too short")
        self._key = self._derive_key(key)
        self._aesgcm = AESGCM(self._key)
    
    @staticmethod
    def _derive_key(master_key: str) -> bytes:
        salt = b"career_platform_v1"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=EncryptionService.KEY_LENGTH,
            salt=salt,
            iterations=EncryptionService.PBKDF2_ITERATIONS,
        )
        return kdf.derive(master_key.encode("utf-8"))
    
    def encrypt(self, data: str | dict | list) -> str:
        try:
            if not isinstance(data, str):
                plaintext = json.dumps(data)
            else:
                plaintext = data
            nonce = os.urandom(self.NONCE_LENGTH)
            ciphertext = self._aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
            encrypted_blob = nonce + ciphertext
            return base64.b64encode(encrypted_blob).decode("utf-8")
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {str(e)}")
    
    def decrypt(self, encrypted: str) -> str:
        try:
            encrypted_blob = base64.b64decode(encrypted)
            nonce = encrypted_blob[:self.NONCE_LENGTH]
            ciphertext = encrypted_blob[self.NONCE_LENGTH:]
            plaintext = self._aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode("utf-8")
        except Exception as e:
            raise EncryptionError(f"Decryption failed: {str(e)}")
    
    def decrypt_json(self, encrypted: str) -> dict | list:
        try:
            decrypted = self.decrypt(encrypted)
            return json.loads(decrypted)
        except json.JSONDecodeError as e:
            raise EncryptionError(f"Failed to parse decrypted JSON: {str(e)}")


class CredentialManager:
    def __init__(self):
        self._encryption = None
    
    @property
    def _enc(self) -> EncryptionService:
        """Lazy initialization of encryption service."""
        if self._encryption is None:
            self._encryption = EncryptionService()
        return self._encryption
    
    def store_credential(
        self,
        credential_type: str,
        credentials: dict,
        display_name: str,
        scope: Optional[dict] = None,
    ) -> dict:
        encrypted_data = self._enc.encrypt(credentials)
        return {
            "display_name": display_name,
            "encrypted_data": encrypted_data,
            "scope": json.dumps(scope) if scope else None,
        }
    
    def retrieve_credential(self, encrypted_data: str) -> dict:
        return self._enc.decrypt_json(encrypted_data)
    
    def validate_scope(self, scope_json: Optional[str], requested_action: str) -> bool:
        if not scope_json:
            return True
        try:
            scope = json.loads(scope_json)
            allowed_actions = scope.get("allowed_actions", [])
            if not allowed_actions:
                return True
            return requested_action in allowed_actions
        except json.JSONDecodeError:
            return True


encryption_service: Optional[EncryptionService] = None
credential_manager = CredentialManager()
