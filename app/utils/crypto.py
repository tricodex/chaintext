"""Cryptographic utilities for ChainContext"""
import os
import hashlib
import base64
import json
import time
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


def generate_hash(data: Any) -> str:
    """
    Generate a SHA-256 hash of data
    
    Args:
        data: Data to hash (string, dict, list, etc.)
        
    Returns:
        Hex digest of the hash
    """
    if isinstance(data, (dict, list)):
        # Convert to JSON and sort keys for deterministic serialization
        data_str = json.dumps(data, sort_keys=True)
    else:
        data_str = str(data)
    
    return hashlib.sha256(data_str.encode()).hexdigest()


def generate_nonce(size: int = 16) -> bytes:
    """
    Generate a random nonce
    
    Args:
        size: Size of the nonce in bytes
        
    Returns:
        Random bytes
    """
    return os.urandom(size)


def encode_base64(data: bytes) -> str:
    """
    Encode bytes as base64 string
    
    Args:
        data: Bytes to encode
        
    Returns:
        Base64-encoded string
    """
    return base64.b64encode(data).decode()


def decode_base64(data: str) -> bytes:
    """
    Decode base64 string to bytes
    
    Args:
        data: Base64-encoded string
        
    Returns:
        Decoded bytes
    """
    return base64.b64decode(data)


def encrypt_data(data: Any, key: bytes) -> Dict[str, str]:
    """
    Encrypt data using AES-256-CBC
    
    Args:
        data: Data to encrypt (string, dict, list, etc.)
        key: Encryption key (32 bytes for AES-256)
        
    Returns:
        Dictionary with initialization vector, ciphertext, and timestamp
    """
    if isinstance(data, (dict, list)):
        plaintext = json.dumps(data, sort_keys=True).encode()
    else:
        plaintext = str(data).encode()
    
    # Create a padder
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_plaintext = padder.update(plaintext) + padder.finalize()
    
    # Generate initialization vector
    iv = os.urandom(16)
    
    # Create encryptor
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    
    # Encrypt data
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
    
    return {
        "iv": encode_base64(iv),
        "ciphertext": encode_base64(ciphertext),
        "timestamp": int(time.time())
    }


def decrypt_data(encrypted_data: Dict[str, str], key: bytes) -> Any:
    """
    Decrypt data encrypted with AES-256-CBC
    
    Args:
        encrypted_data: Dictionary with initialization vector and ciphertext
        key: Decryption key (must match encryption key)
        
    Returns:
        Decrypted data
    """
    iv = decode_base64(encrypted_data["iv"])
    ciphertext = decode_base64(encrypted_data["ciphertext"])
    
    # Create decryptor
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    
    # Decrypt data
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Remove padding
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    
    # Try to parse as JSON
    try:
        return json.loads(plaintext.decode())
    except json.JSONDecodeError:
        # Return as string if not valid JSON
        return plaintext.decode()


def sign_data(data: Any, private_key: bytes) -> str:
    """
    Sign data with private key
    Note: This is a placeholder for actual cryptographic signing
    
    Args:
        data: Data to sign
        private_key: Private key for signing
        
    Returns:
        Base64-encoded signature
    """
    # In a real implementation, we would use a proper signing algorithm
    # For the hackathon, we'll simulate with a hash of the data + key
    if isinstance(data, (dict, list)):
        data_str = json.dumps(data, sort_keys=True)
    else:
        data_str = str(data)
    
    signature_data = data_str.encode() + private_key
    signature = hashlib.sha256(signature_data).digest()
    
    return encode_base64(signature)


def verify_signature(data: Any, signature: str, public_key: bytes) -> bool:
    """
    Verify signature with public key
    Note: This is a placeholder for actual signature verification
    
    Args:
        data: Data that was signed
        signature: Base64-encoded signature
        public_key: Public key for verification
        
    Returns:
        True if signature is valid, False otherwise
    """
    # In a real implementation, we would use a proper verification algorithm
    # For the hackathon, we'll simulate with a hash of the data + key
    if isinstance(data, (dict, list)):
        data_str = json.dumps(data, sort_keys=True)
    else:
        data_str = str(data)
    
    # For simulation, we're using the same key for signing and verification
    signature_data = data_str.encode() + public_key
    expected_signature = hashlib.sha256(signature_data).digest()
    
    return decode_base64(signature) == expected_signature
