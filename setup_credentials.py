#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RingCentral-Zoho CRM Integration - Credentials Setup
This script guides users through setting up API credentials for RingCentral and Zoho.
"""

import os
import sys
import json
import logging
from secure_credentials import SecureCredentials

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/setup_credentials.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def clear_screen():
    """Clear terminal screen for better UI."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print script header."""
    print("=" * 60)
    print(" RingCentral-Zoho CRM Integration - Credentials Setup")
    print("=" * 60)
    print()

def get_ringcentral_credentials():
    """
    Guide user through entering RingCentral credentials.
    
    Returns:
        dict: RingCentral credentials
    """
    print("\nRingCentral API Credentials")
    print("-" * 30)
    print("Please enter the following credentials from your RingCentral Developer Console:")
    print()
    
    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()
    jwt_private_key = input("JWT Private Key (press Enter for multi-line input): ").strip()
    
    if not jwt_private_key:
        print("\nEnter JWT Private Key (press Ctrl+D or Ctrl+Z on an empty line when done):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            jwt_private_key = "\n".join(lines)
    
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "jwt_private_key": jwt_private_key
    }

def get_zoho_credentials():
    """
    Guide user through entering Zoho CRM credentials.
    
    Returns:
        dict: Zoho CRM credentials
    """
    print("\nZoho CRM API Credentials")
    print("-" * 30)
    print("Please enter the following credentials from your Zoho API Console:")
    print()
    
    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()
    refresh_token = input("Refresh Token: ").strip()
    
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }

def save_credentials(ringcentral_credentials, zoho_credentials):
    """
    Save credentials securely.
    
    Args:
        ringcentral_credentials (dict): RingCentral credentials
        zoho_credentials (dict): Zoho CRM credentials
        
    Returns:
        bool: Success status
    """
    try:
        credentials = {
            "ringcentral": ringcentral_credentials,
            "zoho": zoho_credentials
        }
        
        secure = SecureCredentials()
        result = secure.encrypt_credentials(credentials)
        
        return result
    except Exception as e:
        logger.error(f"Error saving credentials: {str(e)}")
        return False

def main():
    """Main function."""
    try:
        # Initialize
        clear_screen()
        print_header()
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
        
        # Check for existing credentials
        secure = SecureCredentials()
        existing_credentials = secure.decrypt_credentials()
        
        if existing_credentials:
            print("Existing credentials found!")
            overwrite = input("Do you want to overwrite them? (y/n): ").strip().lower()
            
            if overwrite != 'y':
                print("\nKeeping existing credentials. Exiting...")
                return
        
        # Get RingCentral credentials
        print("\nLet's set up your RingCentral API credentials.")
        print("You will need credentials from your RingCentral Developer Console.")
        input("Press Enter to continue...")
        
        ringcentral_credentials = get_ringcentral_credentials()
        
        # Get Zoho credentials
        print("\nNow, let's set up your Zoho CRM API credentials.")
        print("You will need credentials from your Zoho API Console.")
        input("Press Enter to continue...")
        
        zoho_credentials = get_zoho_credentials()
        
        # Save credentials
        print("\nSaving credentials securely...")
        success = save_credentials(ringcentral_credentials, zoho_credentials)
        
        if success:
            print("\nCredentials saved successfully!")
            print("You can now run the RingCentral-Zoho CRM Integration scripts.")
        else:
            print("\nFailed to save credentials. Please check logs and try again.")
        
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"\nAn error occurred: {str(e)}")
        print("Please check the logs for more information.")

if __name__ == "__main__":
    main()
