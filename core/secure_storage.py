"""Secure encryption utilities for sensitive data using Windows DPAPI."""
import base64
import json
import sys
from pathlib import Path
from typing import Optional


class SecureStorage:
    """Handles encryption/decryption of sensitive data using Windows DPAPI."""
    
    def __init__(self, app_name: str = "AIAssistantPro"):
        """Initialize secure storage.
        
        Args:
            app_name: Application name for the encryption context
        """
        self.app_name = app_name
        self._encryption_available = sys.platform == 'win32'
        
    def _get_cryptography_module(self):
        """Import cryptography modules only when needed."""
        if not self._encryption_available:
            return None
        try:
            import ctypes
            from ctypes import wintypes
            return ctypes, wintypes
        except ImportError:
            return None
    
    def encrypt(self, data: str) -> Optional[str]:
        """Encrypt a string using Windows DPAPI.
        
        Args:
            data: String to encrypt
            
        Returns:
            Base64-encoded encrypted string, or None if encryption fails
        """
        if not data:
            return data
            
        if not self._encryption_available:
            # Fallback: return as-is with marker on non-Windows
            return f"[UNENCRYPTED]{data}"
        
        try:
            ctypes_module, wintypes_module = self._get_cryptography_module()
            if not ctypes_module:
                return None
            
            # Constants for DPAPI
            CRYPTPROTECT_UI_FORBIDDEN = 0x01
            
            # Load crypt32.dll
            crypt32 = ctypes_module.windll.crypt32
            
            # Convert data to bytes
            data_bytes = data.encode('utf-8')
            data_len = len(data_bytes)
            
            # Prepare DATA_BLOB structures
            class DATA_BLOB(ctypes_module.Structure):
                _fields_ = [
                    ("cbData", wintypes_module.DWORD),
                    ("pbData", ctypes_module.POINTER(ctypes_module.c_char))
                ]
            
            # Input blob
            input_blob = DATA_BLOB()
            input_blob.cbData = data_len
            input_blob.pbData = ctypes_module.cast(
                ctypes_module.create_string_buffer(data_bytes),
                ctypes_module.POINTER(ctypes_module.c_char)
            )
            
            # Output blob
            output_blob = DATA_BLOB()
            
            # Call CryptProtectData
            result = crypt32.CryptProtectData(
                ctypes_module.byref(input_blob),
                None,  # Description
                None,  # Optional entropy
                None,  # Reserved
                None,  # Prompt struct
                CRYPTPROTECT_UI_FORBIDDEN,
                ctypes_module.byref(output_blob)
            )
            
            if not result:
                return None
            
            # Extract encrypted data
            encrypted_bytes = ctypes_module.string_at(
                output_blob.pbData,
                output_blob.cbData
            )
            
            # Free memory
            kernel32 = ctypes_module.windll.kernel32
            kernel32.LocalFree(output_blob.pbData)
            
            # Return base64-encoded
            return base64.b64encode(encrypted_bytes).decode('ascii')
            
        except Exception as e:
            from .logger import get_logger
            get_logger().error(f"Encryption failed: {e}")
            return None
    
    def decrypt(self, encrypted_data: str) -> Optional[str]:
        """Decrypt a string using Windows DPAPI.
        
        Args:
            encrypted_data: Base64-encoded encrypted string
            
        Returns:
            Decrypted string, or None if decryption fails
        """
        if not encrypted_data:
            return encrypted_data
        
        # Check for unencrypted marker (migration or non-Windows)
        if encrypted_data.startswith("[UNENCRYPTED]"):
            return encrypted_data[len("[UNENCRYPTED]"):]
        
        # Check if it's plaintext (legacy data)
        if not self._looks_like_encrypted(encrypted_data):
            # Return as-is, likely unencrypted legacy data
            return encrypted_data
        
        if not self._encryption_available:
            return None
        
        try:
            ctypes_module, wintypes_module = self._get_cryptography_module()
            if not ctypes_module:
                return None
            
            # Constants for DPAPI
            CRYPTPROTECT_UI_FORBIDDEN = 0x01
            
            # Load crypt32.dll
            crypt32 = ctypes_module.windll.crypt32
            
            # Decode base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            data_len = len(encrypted_bytes)
            
            # Prepare DATA_BLOB structures
            class DATA_BLOB(ctypes_module.Structure):
                _fields_ = [
                    ("cbData", wintypes_module.DWORD),
                    ("pbData", ctypes_module.POINTER(ctypes_module.c_char))
                ]
            
            # Input blob
            input_blob = DATA_BLOB()
            input_blob.cbData = data_len
            input_blob.pbData = ctypes_module.cast(
                ctypes_module.create_string_buffer(encrypted_bytes),
                ctypes_module.POINTER(ctypes_module.c_char)
            )
            
            # Output blob
            output_blob = DATA_BLOB()
            
            # Call CryptUnprotectData
            result = crypt32.CryptUnprotectData(
                ctypes_module.byref(input_blob),
                None,  # Description
                None,  # Optional entropy
                None,  # Reserved
                None,  # Prompt struct
                CRYPTPROTECT_UI_FORBIDDEN,
                ctypes_module.byref(output_blob)
            )
            
            if not result:
                return None
            
            # Extract decrypted data
            decrypted_bytes = ctypes_module.string_at(
                output_blob.pbData,
                output_blob.cbData
            )
            
            # Free memory
            kernel32 = ctypes_module.windll.kernel32
            kernel32.LocalFree(output_blob.pbData)
            
            return decrypted_bytes.decode('utf-8')
            
        except Exception as e:
            from .logger import get_logger
            get_logger().error(f"Decryption failed: {e}")
            return None
    
    def _looks_like_encrypted(self, data: str) -> bool:
        """Check if data appears to be base64-encoded encrypted data.
        
        Args:
            data: String to check
            
        Returns:
            True if data looks like encrypted base64
        """
        try:
            # Base64 strings are typically alphanumeric with + and /
            # and may end with = padding
            if len(data) < 20:  # Too short to be encrypted
                return False
            
            # Try to decode
            decoded = base64.b64decode(data)
            # Encrypted data should contain non-printable characters
            return any(b < 32 or b > 126 for b in decoded)
        except Exception:
            return False
    
    def encrypt_list(self, items: list[str]) -> list[str]:
        """Encrypt a list of strings.
        
        Args:
            items: List of strings to encrypt
            
        Returns:
            List of encrypted strings (None for failed items)
        """
        return [self.encrypt(item) for item in items]
    
    def decrypt_list(self, encrypted_items: list[str]) -> list[str]:
        """Decrypt a list of strings.
        
        Args:
            encrypted_items: List of encrypted strings
            
        Returns:
            List of decrypted strings (excluding failed items)
        """
        result = []
        for item in encrypted_items:
            decrypted = self.decrypt(item)
            if decrypted is not None:
                result.append(decrypted)
        return result
