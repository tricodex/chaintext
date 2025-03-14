#!/usr/bin/env python3
"""
Script to set up the token type verifier for the Flare vTPM Attestation contract.
This needs to be run by the contract owner.
"""

import json
import os
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
WEB3_PROVIDER_URI = os.getenv("WEB3_PROVIDER_URI", "https://flare-api.flare.network/ext/C/rpc")
FLARE_VTPM_ATTESTATION_ADDRESS = os.getenv("FLARE_VTPM_ATTESTATION_ADDRESS", "0x93012953008ef9AbcB71F48C340166E8f384e985")
PRIVATE_KEY = os.getenv("OWNER_PRIVATE_KEY", "")  # Contract owner's private key

# Token verifier address - this should be the address of the OIDC verifier contract
# For testing, we can deploy a simple verifier contract or use a mock address
TOKEN_VERIFIER_ADDRESS = os.getenv("TOKEN_VERIFIER_ADDRESS", "")

def main():
    # Check if private key is provided
    if not PRIVATE_KEY:
        print("Error: OWNER_PRIVATE_KEY environment variable is not set.")
        print("Please set it to the private key of the contract owner.")
        return
    
    if not TOKEN_VERIFIER_ADDRESS:
        print("Error: TOKEN_VERIFIER_ADDRESS environment variable is not set.")
        print("Please set it to the address of the token verifier contract.")
        return
    
    # Initialize Web3
    web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))
    
    # Check connection
    if not web3.is_connected():
        print(f"Error: Could not connect to {WEB3_PROVIDER_URI}")
        return
    
    print(f"Connected to {WEB3_PROVIDER_URI}")
    
    # Load contract ABI
    try:
        with open('app/data/flare_vtpm_attestation_abi.json', 'r') as f:
            contract_abi = json.load(f)
        print("Loaded Flare vTPM Attestation ABI from file")
    except Exception as e:
        print(f"Error loading contract ABI: {e}")
        return
    
    # Initialize contract
    try:
        contract_address = web3.to_checksum_address(FLARE_VTPM_ATTESTATION_ADDRESS)
        contract = web3.eth.contract(address=contract_address, abi=contract_abi)
        print(f"Initialized contract at {contract_address}")
    except Exception as e:
        print(f"Error initializing contract: {e}")
        return
    
    # Get account from private key
    try:
        account = web3.eth.account.from_key(PRIVATE_KEY)
        print(f"Using account: {account.address}")
    except Exception as e:
        print(f"Error creating account from private key: {e}")
        return
    
    # Check if the account is the contract owner
    try:
        owner = contract.functions.owner().call()
        if owner.lower() != account.address.lower():
            print(f"Error: The provided account ({account.address}) is not the contract owner ({owner}).")
            return
        print(f"Confirmed account is the contract owner")
    except Exception as e:
        print(f"Error checking contract owner: {e}")
        return
    
    # Set token type verifier for OIDC tokens
    try:
        token_verifier = web3.to_checksum_address(TOKEN_VERIFIER_ADDRESS)
        
        # Build transaction
        tx = contract.functions.setTokenTypeVerifier(token_verifier).build_transaction({
            'from': account.address,
            'nonce': web3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': web3.eth.gas_price
        })
        
        # Sign transaction
        signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        
        # Send transaction
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Transaction sent: {tx_hash.hex()}")
        
        # Wait for transaction receipt
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            print("Transaction successful!")
            print(f"Token verifier set to {token_verifier}")
        else:
            print("Transaction failed!")
            print(receipt)
    except Exception as e:
        print(f"Error setting token type verifier: {e}")
        return

if __name__ == "__main__":
    main()
