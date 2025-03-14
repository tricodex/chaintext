import json
import time
from typing import Dict, List, Optional, Any
import asyncio
from web3 import Web3
from redis.asyncio import Redis
from loguru import logger

from app.core.config import settings

# Load FTSO Registry ABI from file
try:
    with open('app/data/ftso_registry_abi.json', 'r') as f:
        FTSO_REGISTRY_ABI = json.load(f)
    logger.info("Loaded FTSO Registry ABI from file")
except Exception as e:
    logger.warning(f"Could not load FTSO Registry ABI from file: {e}")
    # Fallback to minimal ABI definition
    FTSO_REGISTRY_ABI = [
    {
        "inputs": [{"internalType": "uint256", "name": "_symbolIndex", "type": "uint256"}],
        "name": "getCurrentPrice",
        "outputs": [
            {"internalType": "uint256", "name": "_price", "type": "uint256"},
            {"internalType": "uint256", "name": "_timestamp", "type": "uint256"},
            {"internalType": "uint256", "name": "_decimals", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getSupportedSymbols",
        "outputs": [{"internalType": "string[]", "name": "", "type": "string[]"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getSupportedSymbolsCount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "_symbolIndex", "type": "uint256"}],
        "name": "getSupportedSymbol",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "_symbol", "type": "string"}],
        "name": "getSupportedSymbolIndex",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

class FTSODataCollector:
    """Collects price data from Flare's FTSO system"""
    
    def __init__(self, web3_provider: Optional[str] = None, redis_client: Optional[Redis] = None):
        """Initialize FTSO data collector"""
        self.web3_provider = web3_provider or settings.WEB3_PROVIDER_URI
        self.web3 = Web3(Web3.HTTPProvider(self.web3_provider))
        self.redis = redis_client
        self.ftso_registry_address = settings.FTSO_REGISTRY_ADDRESS
        
        # Initialize FTSO contract
        self.ftso_registry = self.web3.eth.contract(
            address=self.ftso_registry_address,
            abi=FTSO_REGISTRY_ABI
        )
        
        logger.info(f"Initialized FTSO Data Collector with provider: {self.web3_provider}")
    
    async def set_redis_client(self, redis_client: Redis):
        """Set Redis client after initialization"""
        self.redis = redis_client
    
    async def get_supported_symbols(self) -> List[str]:
        """Get list of supported symbols from the FTSO registry"""
        try:
            # Try to get from cache first if Redis is available
            if self.redis:
                symbols_cache = await self.redis.get("ftso:symbols")
                if symbols_cache:
                    cached_symbols = json.loads(symbols_cache)
                    logger.debug(f"Got {len(cached_symbols)} symbols from cache")
                    return cached_symbols
            
            # If not in cache or no Redis, fetch from contract
            logger.info("Fetching supported symbols from FTSO registry")
            try:
                symbols = await asyncio.to_thread(
                    self.ftso_registry.functions.getSupportedSymbols().call,
                    timeout=10  # Add timeout to prevent hanging
                )
                
                # Cache the results if Redis is available
                if self.redis and symbols:
                    await self.redis.set("ftso:symbols", json.dumps(symbols), ex=3600)  # 1 hour expiry
                    logger.debug(f"Cached {len(symbols)} symbols")
                
                return symbols
            except asyncio.TimeoutError:
                logger.warning("Timeout fetching symbols from FTSO registry")
                raise
                
        except Exception as e:
            logger.error(f"Error fetching supported symbols: {e}")
            # Return default symbols if we can't fetch from the contract
            default_symbols = ["FLR", "BTC", "ETH", "XRP", "USDC", "USDT", "ALGO", "DOGE", "ADA"]
            logger.info(f"Using default symbols: {default_symbols}")
            return default_symbols
    
    async def collect_2s_data(self) -> Dict[str, Dict]:
        """Collect 2-second latency data from FTSO feeds"""
        try:
            symbols = await self.get_supported_symbols()
            prices = {}
            
            # For each symbol, get current price
            for symbol in symbols:
                try:
                    # Get symbol index
                    symbol_index = await asyncio.to_thread(
                        self.ftso_registry.functions.getSupportedSymbolIndex(symbol).call
                    )
                    
                    # Get current price
                    price_data = await asyncio.to_thread(
                        self.ftso_registry.functions.getCurrentPrice(symbol_index).call
                    )
                    
                    # Apply decimals to get actual price
                    price_value = price_data[0] / 10**price_data[2]
                    timestamp = price_data[1]
                    
                    # Create price data object
                    price_obj = {
                        "price": price_value,
                        "timestamp": timestamp if timestamp > 0 else int(time.time()),
                        "source": "ftso_2s",
                        "symbol": symbol,
                        "decimals": price_data[2]
                    }
                    
                    prices[symbol] = price_obj
                    
                    # Store in cache if Redis is available
                    if self.redis:
                        await self.redis.set(
                            f"ftso:2s:{symbol}",
                            json.dumps(price_obj),
                            ex=300  # 5-minute expiry
                        )
                    
                    # Note: In a real implementation, we'd also store in MongoDB here
                    
                except Exception as e:
                    logger.error(f"Error getting price for {symbol}: {e}")
            
            return prices
        except Exception as e:
            logger.error(f"Error collecting 2s data: {e}")
            return {}
    
    async def collect_90s_data(self) -> Dict[str, Dict]:
        """
        Collect 90-second latency (anchor) data from FTSO feeds
        Note: This is a simplified implementation as it uses the same endpoint
        as 2s data but would be different in a real-world scenario
        """
        try:
            # In a real implementation, we'd use a different endpoint for 90s data
            # For the hackathon, we'll simulate by using the same data with minor adjustments
            prices_2s = await self.collect_2s_data()
            prices_90s = {}
            
            # Adjust the 2s data to simulate 90s data (slightly different prices)
            for symbol, price_data in prices_2s.items():
                # Create a copy with slight variations to simulate different source
                price_90s = price_data.copy()
                price_90s["source"] = "ftso_90s"
                # Simulate slight price difference (up to 0.5% difference)
                variation = (1.0 + (hash(str(time.time())) % 10 - 5) / 1000)  
                price_90s["price"] = price_data["price"] * variation
                
                prices_90s[symbol] = price_90s
                
                # Store in cache if Redis is available
                if self.redis:
                    await self.redis.set(
                        f"ftso:90s:{symbol}",
                        json.dumps(price_90s),
                        ex=600  # 10-minute expiry
                    )
            
            return prices_90s
        except Exception as e:
            logger.error(f"Error collecting 90s data: {e}")
            return {}
    
    async def start_collection_loop(self):
        """Start continuous collection of FTSO data"""
        logger.info("Starting FTSO data collection loop")
        while True:
            try:
                # Collect 2s data
                await self.collect_2s_data()
                
                # Every 30 iterations (roughly 1 minute), collect 90s data
                if int(time.time()) % 60 < 2:
                    await self.collect_90s_data()
                
                # Wait before next collection
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Error in FTSO collection loop: {e}")
                await asyncio.sleep(5)  # Wait longer on error
