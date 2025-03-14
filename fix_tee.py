#!/usr/bin/env python3
import re

# The new implementation of the _fetch_attestation_token method
new_method = '''    async def _fetch_attestation_token(self, audience: str = None, nonce: str = None) -> Optional[str]:
        """Fetch an attestation token from the Google Cloud VM

        Args:
            audience: The intended audience for the token (used for verification)
            nonce: A nonce to prevent replay attacks

        Returns:
            The attestation token if successful, None otherwise
        """
        try:
            # Try metadata server first (original approach)
            logger.info("Attempting to fetch attestation token from metadata server")
            attestation_urls = [
                "http://metadata.google.internal/computeMetadata/v1/instance/attestation-token",
                "http://metadata.google.internal/computeMetadata/v1/instance/confidential-vm/attestation-token",
                "http://metadata.google.internal/computeMetadata/v1/instance/confidential_computing/attestation"
            ]
            
            # The request must include the Metadata-Flavor header
            headers = {"Metadata-Flavor": "Google"}
            
            # Prepare query parameters for audience and nonce if provided
            params = {}
            if audience:
                params['audience'] = audience
            if nonce:
                params['nonce'] = nonce
            else:
                # Generate a secure random nonce if not provided
                params['nonce'] = base64.b64encode(os.urandom(16)).decode('utf-8')
            
            # Try each possible metadata URL
            for url in attestation_urls:
                try:
                    logger.debug(f"Trying attestation URL: {url}")
                    response = requests.get(
                        url, 
                        headers=headers, 
                        params=params,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"Successfully fetched vTPM attestation token from {url}")
                        return response.text
                    else:
                        logger.warning(f"Failed to get attestation token from {url}: {response.status_code}")
                except Exception as e:
                    logger.warning(f"Error fetching attestation token from {url}: {e}")
            
            # If metadata server approach failed, try using gotpm tool
            logger.info("Metadata server approach failed, attempting to use gotpm for attestation token")
            import subprocess
            
            # Prepare audience parameter
            audience_param = audience or "ChainContext"
            
            # Use gotpm to generate a token
            try:
                gotpm_path = settings.GOTPM_PATH
                cmd = ["sudo", gotpm_path, "token", "--audience", audience_param]
                
                logger.debug(f"Running command: {' '.join(cmd)}")
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if process.returncode == 0 and process.stdout:
                    # Extract the token (first line contains the token)
                    token = process.stdout.strip().split("\\n")[0]
                    if token and token.count('.') == 2:  # Basic JWT format check
                        logger.info("Successfully obtained attestation token using gotpm")
                        return token
                    else:
                        logger.warning("gotpm output does not appear to be a valid JWT token")
                        logger.debug(f"gotpm output: {process.stdout}")
                else:
                    logger.warning(f"gotpm command failed with return code {process.returncode}")
                    if process.stderr:
                        logger.warning(f"gotpm stderr: {process.stderr}")
            except AttributeError:
                logger.warning("GOTPM_PATH not found in settings, skipping gotpm approach")
            except Exception as e:
                logger.warning(f"Error using gotpm: {e}")
            
            # Try using the helper script as a fallback
            try:
                logger.info("Attempting to use helper script for attestation token")
                helper_script = "/home/pc/chaincontext/chaincontext-backend/bin/get_attestation.sh"
                if os.path.exists(helper_script) and os.access(helper_script, os.X_OK):
                    cmd = [helper_script]
                    logger.debug(f"Running helper script: {helper_script}")
                    process = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    
                    if process.returncode == 0 and process.stdout:
                        token = process.stdout.strip()
                        if token and token.count('.') == 2:
                            logger.info("Successfully obtained attestation token using helper script")
                            return token
                        else:
                            logger.warning("Helper script output does not appear to be a valid JWT token")
                    else:
                        logger.warning(f"Helper script failed with return code {process.returncode}")
                else:
                    logger.warning(f"Helper script not found or not executable: {helper_script}")
            except Exception as script_error:
                logger.warning(f"Error running helper script: {script_error}")
            
            # Fallback to using pre-generated token if available
            token_path = "/home/pc/chaincontext/chaincontext-backend/attestation_token.txt"
            if os.path.exists(token_path):
                try:
                    with open(token_path, "r") as f:
                        token = f.read().strip()
                        if token and token.count('.') == 2:
                            logger.info("Using pre-generated attestation token from file")
                            return token
                        else:
                            logger.warning("Token in file does not appear to be a valid JWT token")
                except Exception as file_error:
                    logger.warning(f"Error reading token file: {file_error}")
            
            logger.error("All attestation token methods failed")
            return None
        except Exception as e:
            logger.error(f"Error fetching attestation token: {e}")
            return None'''

with open('app/services/tee.py', 'r') as f:
    content = f.read()

# Create a backup
with open('app/services/tee.py.backup_fix', 'w') as f:
    f.write(content)
print("Created backup of tee.py")

# Find the beginning of the method
pattern = r'    async def _fetch_attestation_token\(self.*?return None'

# Replace the method using regex with re.DOTALL to match across lines
import re
updated_content = re.sub(pattern, new_method, content, flags=re.DOTALL)

# Write the updated content back to the file
with open('app/services/tee.py', 'w') as f:
    f.write(updated_content)

print("Updated _fetch_attestation_token method in app/services/tee.py")