"""
Encrypted Storage - Encrypt sensitive data at rest.
"""

from cryptography.fernet import Fernet
from typing import Optional
from pathlib import Path
import json
import os

class EncryptedStorage:
    """
    Encrypt data at rest using AES-256 (via Fernet).
    
    Key management: Store encryption key securely (environment variable or key vault).
    """
    
    def __init__(self, key_file: Optional[str] = None):
        """
        Initialize encrypted storage.
        
        Args:
            key_file: Path to encryption key file (created if doesn't exist)
        """
        self.key_file = key_file or os.getenv("LAS_ENCRYPTION_KEY_FILE", "data/.encryption_key")
        self.key = self._load_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _load_or_create_key(self) -> bytes:
        """Load or create encryption key."""
        key_path = Path(self.key_file)
        
        if key_path.exists():
            # Load existing key
            return key_path.read_bytes()
        else:
            # Generate new key
            key = Fernet.generate_key()
            key_path.parent.mkdir(parents=True, exist_ok=True)
            key_path.write_bytes(key)
            
            # Set restrictive permissions (owner only)
            os.chmod(key_path, 0o600)
            
            return key
    
    def encrypt(self, data: str) -> bytes:
        """
        Encrypt text data.
        
        Args:
            data: Plain text data
        
        Returns:
            Encrypted bytes
        """
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, encrypted_data: bytes) -> str:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Encrypted bytes
        
        Returns:
            Decrypted text
        """
        return self.cipher.decrypt(encrypted_data).decode()
    
    def encrypt_dict(self, data: dict) -> bytes:
        """Encrypt a dictionary (converts to JSON first)."""
        json_str = json.dumps(data)
        return self.encrypt(json_str)
    
    def decrypt_dict(self, encrypted_data: bytes) -> dict:
        """Decrypt to dictionary."""
        json_str = self.decrypt(encrypted_data)
        return json.loads(json_str)
    
    def encrypt_file(self, input_file: str, output_file: Optional[str] = None):
        """
        Encrypt a file.
        
        Args:
            input_file: Input file path
            output_file: Output file path (defaults to input + .enc)
        """
        output_file = output_file or f"{input_file}.enc"
        
        with open(input_file, 'rb') as f:
            data = f.read()
        
        encrypted = self.cipher.encrypt(data)
        
        with open(output_file, 'wb') as f:
            f.write(encrypted)
    
    def decrypt_file(self, input_file: str, output_file: Optional[str] = None):
        """
        Decrypt a file.
        
        Args:
            input_file: Encrypted file path
            output_file: Output file path (defaults to input without .enc)
        """
        output_file = output_file or input_file.replace('.enc', '')
        
        with open(input_file, 'rb') as f:
            encrypted = f.read()
        
        decrypted = self.cipher.decrypt(encrypted)
        
        with open(output_file, 'wb') as f:
            f.write(decrypted)

# Create singleton instance
_encrypted_storage: Optional[EncryptedStorage] = None

def get_encrypted_storage() -> EncryptedStorage:
    """Get or create EncryptedStorage instance."""
    global _encrypted_storage
    if _encrypted_storage is None:
        _encrypted_storage = EncryptedStorage()
    return _encrypted_storage

# Production recommendations
"""
Key Management Best Practices:
1. Store encryption key in environment variable or secure vault (AWS KMS, HashiCorp Vault)
2. Rotate keys periodically
3. Use different keys for different data types
4. Never commit keys to version control
5. Implement key backup and recovery procedures

Example with environment variable:
export LAS_ENCRYPTION_KEY="<base64-encoded-key>"

Example key rotation:
1. Generate new key
2. Decrypt all data with old key
3. Re-encrypt with new key
4. Update key reference
5. Securely delete old key
"""
