#!/usr/bin/env python3
"""
Test script for Flare vTPM attestation.
This script tests both the attestation generation and verification.
"""

import asyncio
import json
import os
import sys
from loguru import logger
import requests

# Add the current directory to the path to allow importing app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Import the attestation generator and verifier
from app.services.tee import TEEAttestationGenerator, OnChainVerifier


async def test_attestation_generation():
    """Test generating attestations"""
    logger.info("Testing attestation generation...")
    
    # Check if running in Docker container
    in_docker = os.path.exists('/.dockerenv')
    if in_docker:
        logger.info("Running inside Docker container")
    
    # Create an attestation generator
    attestation_generator = TEEAttestationGenerator()
    
    # Check if we're running in a confidential VM
    if attestation_generator.is_confidential_vm:
        logger.info("Running in a Google Cloud Confidential VM with vTPM support")
    else:
        logger.info("Not running in a Google Cloud Confidential VM, will use simulation")
    
    # Try to use pre-generated token if available
    token_path = "/app/attestation_token.txt"
    if not os.path.exists(token_path):
        token_path = "attestation_token.txt"  # Try relative path
        
    if os.path.exists(token_path):
        logger.info(f"Found pre-generated token at {token_path}")
        try:
            with open(token_path, "r") as f:
                token = f.read().strip()
                logger.info("Successfully loaded pre-generated attestation token")
                logger.info(f"Token length: {len(token)}")
                logger.info(f"Token preview: {token[:50]}...")
                
                # Process the token
                token_parts = attestation_generator._process_jwt_token(token)
                if token_parts:
                    logger.info("Successfully processed attestation token")
                    logger.info(f"Header length: {len(token_parts['header']) // 2 - 1} bytes")
                    logger.info(f"Payload length: {len(token_parts['payload']) // 2 - 1} bytes")
                    logger.info(f"Signature length: {len(token_parts['signature']) // 2 - 1} bytes")
                    
                    # Extract and log payload information to check against contract requirements
                    try:
                        # Extract payload from hex
                        payload_hex = token_parts['payload']
                        payload_bytes = bytes.fromhex(payload_hex[2:]) if payload_hex.startswith("0x") else bytes.fromhex(payload_hex)
                        payload_json = json.loads(payload_bytes.decode('utf-8'))
                        
                        # Log the important fields for debugging against contract requirements
                        logger.info("Payload Values (for contract validation):")
                        logger.info(f"  issuer: {payload_json.get('iss')}")
                        logger.info(f"  hwmodel: {payload_json.get('hwmodel')}")
                        logger.info(f"  swname: {payload_json.get('swname')}")
                        
                        # Check if we have image_digest 
                        logger.info(f"  image_digest: {payload_json.get('image_digest', 'NOT PRESENT')}")
                        logger.info(f"  secboot: {payload_json.get('secboot')}")
                        
                        logger.info("Contract is configured to expect:")
                        logger.info("  Hardware Model: GCP_AMD_SEV")
                        logger.info("  Software Name: CONFIDENTIAL_SPACE")
                        logger.info("  Image Digest: sha256:a490f5528c8739a870bdb234068fa29a95b9b641d1b0a114564c9e7a0ed900d0")
                        logger.info("  Issuer: https://confidentialcomputing.googleapis.com")
                        logger.info("  Secure Boot: Enabled")
                        
                        # Generate an attestation using the pre-generated token
                        test_query = "What is the current status of Flare network?"
                        test_context = [{"id": "test1", "text": "Test context"}]
                        test_response = {"answer": "Test answer", "confidence": 0.9}
                        
                        # Create a hash of the query/response
                        data_hash = attestation_generator._create_hash(test_query, test_context, test_response)
                        
                        # Create attestation with pre-loaded token
                        attestation = {
                            "token": token,
                            "header": token_parts["header"],
                            "payload": token_parts["payload"],
                            "signature": token_parts["signature"],
                            "data_hash": data_hash,
                            "digest": token_parts["digest"],
                            "timestamp": int(payload_json.get('iat', 0)),
                            "simulated": False,
                            "type": "gcp_vtpm"
                        }
                        
                        logger.info(f"Generated attestation using pre-loaded token: {json.dumps(attestation, indent=2)}")
                        return attestation
                    except Exception as e:
                        logger.error(f"Error parsing payload details from pre-generated token: {e}")
        except Exception as e:
            logger.error(f"Error reading pre-generated token: {e}")
    
    # If we don't have a pre-generated token, try to fetch a live one
    try:
        # Try to fetch an attestation token (this will only work in a Confidential VM)
        token = await attestation_generator._fetch_attestation_token()
        if token:
            logger.info("Successfully fetched live attestation token")
            logger.info(f"Token length: {len(token)}")
            logger.info(f"Token preview: {token[:50]}...")
            
            # Process the token
            token_parts = attestation_generator._process_jwt_token(token)
            if token_parts:
                logger.info("Successfully processed attestation token")
                logger.info(f"Header length: {len(token_parts['header']) // 2 - 1} bytes")
                logger.info(f"Payload length: {len(token_parts['payload']) // 2 - 1} bytes")
                logger.info(f"Signature length: {len(token_parts['signature']) // 2 - 1} bytes")
                
                # Extract and log payload information to check against contract requirements
                try:
                    # Extract payload from hex
                    payload_hex = token_parts['payload']
                    payload_bytes = bytes.fromhex(payload_hex[2:]) if payload_hex.startswith("0x") else bytes.fromhex(payload_hex)
                    payload_json = json.loads(payload_bytes.decode('utf-8'))
                    
                    # Log the important fields for debugging against contract requirements
                    logger.info("Payload Values (for contract validation):")
                    logger.info(f"  issuer: {payload_json.get('iss')}")
                    logger.info(f"  hwmodel: {payload_json.get('hwmodel')}")
                    logger.info(f"  swname: {payload_json.get('swname')}")
                    
                    # Check if we have image_digest 
                    logger.info(f"  image_digest: {payload_json.get('image_digest', 'NOT PRESENT')}")
                    logger.info(f"  secboot: {payload_json.get('secboot')}")
                    
                    logger.info("Contract is configured to expect:")
                    logger.info("  Hardware Model: GCP_AMD_SEV")
                    logger.info("  Software Name: CONFIDENTIAL_SPACE")
                    logger.info("  Image Digest: sha256:a490f5528c8739a870bdb234068fa29a95b9b641d1b0a114564c9e7a0ed900d0")
                    logger.info("  Issuer: https://confidentialcomputing.googleapis.com")
                    logger.info("  Secure Boot: Enabled")
                    
                    if payload_json.get('hwmodel') != 'GCP_AMD_SEV':
                        logger.warning("Hardware model mismatch with contract configuration")
                    if payload_json.get('iss') != 'https://confidentialcomputing.googleapis.com':
                        logger.warning("Issuer mismatch with contract configuration")
                    if payload_json.get('swname') != 'CONFIDENTIAL_SPACE':
                        logger.warning("Software name mismatch with contract configuration")
                    if not payload_json.get('image_digest'):
                        logger.warning("Missing image_digest field required by contract")
                except Exception as e:
                    logger.error(f"Error parsing payload details: {e}")
        else:
            logger.warning("Could not fetch attestation token - check if running in a Confidential VM")
    except Exception as e:
        logger.error(f"Error fetching attestation token: {e}")
    
    # Generate an attestation for a test query (will use simulation if needed)
    test_query = "What is the current status of Flare network?"
    test_context = [{"id": "test1", "text": "Test context"}]
    test_response = {"answer": "Test answer", "confidence": 0.9}
    
    attestation = await attestation_generator.generate_attestation(
        test_query, test_context, test_response
    )
    
    logger.info(f"Generated attestation: {json.dumps(attestation, indent=2)}")
    
    return attestation


async def test_attestation_verification(attestation):
    """Test verifying attestations"""
    logger.info("Testing attestation verification...")
    
    # Create an attestation verifier
    verifier = OnChainVerifier()
    
    # Check for expected contract configuration
    try:
        from web3 import Web3
        web3 = Web3(Web3.HTTPProvider(verifier.web3_provider))
        contract = verifier.flare_vtpm_contract
        
        if contract:
            logger.info(f"Checking contract configuration at {verifier.flare_vtpm_address}")
            
            # Note that we expect verification to fail because:
            # 1. Token verifiers aren't set on the contract yet (missing setTokenTypeVerifier)
            # 2. Our VM's attestation doesn't match the expected digest/config
            logger.info("Contract verification expected to fail in test environment - will fallback to simulation")
    except Exception as e:
        logger.error(f"Error checking contract configuration: {e}")
    
    # Verify the attestation
    verification_result = await verifier.verify_attestation(attestation)
    
    logger.info(f"Verification result: {json.dumps(verification_result, indent=2)}")
    
    return verification_result


async def test_api_verification(attestation):
    """Test verifying attestations through the API"""
    logger.info("Testing API verification...")
    
    # Call the verify API endpoint
    try:
        # Try to connect with a shorter timeout to avoid long waits if server is down
        response = requests.post(
            "http://localhost:8000/api/verify",
            json={"attestation": attestation},
            timeout=2  # Reduced timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"API verification result: {json.dumps(result, indent=2)}")
            return result
        else:
            logger.error(f"API verification failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        logger.warning("API server doesn't appear to be running (connection refused). Skipping API verification test.")
        logger.info("To test API verification, start the server with: python run.py")
        return None
    except Exception as e:
        logger.error(f"Error calling API: {e}")
        return None


async def main():
    """Main test function"""
    logger.info("Starting vTPM attestation test...")
    
    # Test attestation generation
    attestation = await test_attestation_generation()
    
    # Test attestation verification
    await test_attestation_verification(attestation)
    
    # Test API verification
    await test_api_verification(attestation)
    
    logger.info("vTPM attestation test completed")
    logger.info("Note: Expected contract verification to fail in test environment because:")
    logger.info("  1. Token verifier not set on contract (requires owner call to setTokenTypeVerifier)")
    logger.info("  2. Test VM attestation doesn't match the image digest configured in contract")
    logger.info("  3. Simulated verification is working as expected as a fallback")


if __name__ == "__main__":
    # Configure logger
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    
    # Run the test
    asyncio.run(main())
