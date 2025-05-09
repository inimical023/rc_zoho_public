#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RingCentral-Zoho CRM Integration - Secure Credential Management
This script handles encryption and decryption of API credentials.
"""

import os
import sys
import json
import base64
import logging
from cryptography.fernet import Fernet, InvalidToken

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/secure_credentials.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SecureCredentials:
    """Class to handle secure storage of API credentials."""
    
    def __init__(self, key_file="data/encryption.key", credentials_file="data/credentials.enc"):
        """
        Initialize secure credentials manager.
        
        Args:
            key_file (str): Path to encryption key file
            credentials_file (str): Path to encrypted credentials file
        """
        self.key_file = key_file
        self.credentials_file = credentials_file
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        os.makedirs(os.path.dirname(credentials_file), exist_ok=True)
    
    def generate_key(self):
        """
        Generate a new encryption key and save it to file.
        
        Returns:
            bytes: The generated key
        """
        logger.info(f"Generating new encryption key at {self.key_file}")
        key = Fernet.generate_key()
        
        with open(self.key_file, 'wb') as key_file:
            key_file.write(key)
        
        logger.info("Encryption key generated successfully")
        return key
    
    def load_key(self):
        """
        Load encryption key from file or generate if not exists.
        
        Returns:
            bytes: The encryption key
        """
        try:
            if os.path.exists(self.key_file):
                logger.info(f"Loading encryption key from {self.key_file}")
                with open(self.key_file, 'rb') as key_file:
                    key = key_file.read()
            else:
                logger.info(f"Key file not found, generating new key")
                key = self.generate_key()
            
            return key
        except Exception as e:
            logger.error(f"Error loading encryption key: {str(e)}")
            raise
    
    def encrypt_credentials(self, credentials):
        """
        Encrypt credentials dictionary and save to file.
        
        Args:
            credentials (dict): Credentials to encrypt
            
        Returns:
            bool: Success status
        """
        try:
            logger.info("Encrypting credentials")
            key = self.load_key()
            cipher = Fernet(key)
            
            credentials_json = json.dumps(credentials).encode('utf-8')
            encrypted_data = cipher.encrypt(credentials_json)
            
            with open(self.credentials_file, 'wb') as cred_file:
                cred_file.write(encrypted_data)
            
            logger.info(f"Credentials encrypted successfully to {self.credentials_file}")
            return True
        except Exception as e:
            logger.error(f"Error encrypting credentials: {str(e)}")
            return False
    
    def decrypt_credentials(self):
        """
        Decrypt credentials from file.
        
        Returns:
            dict: Decrypted credentials dictionary or None if error
        """
        try:
            if not os.path.exists(self.credentials_file):
                logger.warning(f"Credentials file not found: {self.credentials_file}")
                return None
            
            logger.info(f"Loading encrypted credentials from {self.credentials_file}")
            key = self.load_key()
            cipher = Fernet(key)
            
            with open(self.credentials_file, 'rb') as cred_file:
                encrypted_data = cred_file.read()
            
            decrypted_data = cipher.decrypt(encrypted_data)
            credentials = json.loads(decrypted_data.decode('utf-8'))
            
            logger.info("Credentials decrypted successfully")
            return credentials
        except InvalidToken:
            logger.error("Invalid encryption key or corrupted data")
            return None
        except Exception as e:
            logger.error(f"Error decrypting credentials: {str(e)}")
            return None

def main():
    """Main function for direct script execution."""
    print("RingCentral-Zoho CRM Integration - Secure Credential Management")
    print("This script should be used via setup_credentials.py")
    print("For direct usage, import the SecureCredentials class")

if __name__ == "__main__":
    main()
