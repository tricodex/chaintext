import os
from typing import List, Dict, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Database
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/chaincontext")
    REDIS_URI: str = os.getenv("REDIS_URI", "redis://localhost:6379/0")
    
    # Vector Database
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    
    # Blockchain
    WEB3_PROVIDER_URI: str = os.getenv(
        "WEB3_PROVIDER_URI", 
        "https://flare-api.flare.network/ext/C/rpc"
    )
    FTSO_REGISTRY_ADDRESS: str = os.getenv(
        "FTSO_REGISTRY_ADDRESS", 
        "0x1000000000000000000000000000000000000003"
    )
    TEE_VERIFIER_ADDRESS: str = os.getenv(
        "TEE_VERIFIER_ADDRESS", 
        "0x28432EC82268eE4A9fa051e9005DCea26ae21160"  # Use correct address
    )
    
    # Flare vTPM Attestation
    FLARE_VTPM_ATTESTATION_ADDRESS: str = os.getenv(
        "FLARE_VTPM_ATTESTATION_ADDRESS", 
        "0x93012953008ef9AbcB71F48C340166E8f384e985"  # Using the updated contract address from the deployment report
    )
    
    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Social Media
    TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "")
    
    # TPM
    TPM_DEVICE: str = os.getenv("TPM_DEVICE", "/dev/tpm0")
    GOTPM_PATH: str = os.getenv("GOTPM_PATH", "/home/pc/chaincontext/tools/go-tpm-tools/cmd/gotpm/gotpm")
    
    # Trust Scores
    SOURCE_RELIABILITY: Dict[str, float] = {
        'ftso_2s': 0.95,       # FTSO 2s latency feed (highest reliability)
        'ftso_90s': 0.9,       # FTSO 90s latency feed
        'blockchain_state': 0.95,  # Actual blockchain state
        'flare_docs': 0.85,    # Official documentation
        'github_code': 0.8,    # GitHub repository code
        'github_issues': 0.6,  # GitHub issues
        'twitter_official': 0.7,  # Official Twitter accounts
        'twitter_community': 0.4,  # Community Twitter
    }
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Application name
    APP_NAME: str = "ChainContext"
    
    # Version
    VERSION: str = "0.1.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

