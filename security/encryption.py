# security/encryption.py
# Service for encrypting and decrypting data.

from cryptography.fernet import Fernet
from core.config import settings

# Point-wise comment: Initialize the Fernet cipher suite
# This uses the encryption key from the application settings.
cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode())

# Point-wise comment: Function to encrypt data
def encrypt_data(data: str) -> bytes:
    if not data:
        return None
    return cipher_suite.encrypt(data.encode())

# Point-wise comment: Function to decrypt data
def decrypt_data(encrypted_data: bytes) -> str:
    if not encrypted_data:
        return None
    return cipher_suite.decrypt(encrypted_data).decode()
