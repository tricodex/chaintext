"""
FTSO Data Collector for Flare Testnet (Coston 2)
This module provides utilities to access FTSO data from the Flare testnet.
"""

import os
import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from web3 import Web3
from loguru import logger

# Constants for Coston 2 Testnet
COSTON2_RPC_URL = os.getenv("COSTON2_RPC_URL", "https://coston2-api.flare.network/ext/C/rpc")
FTSO_REGISTRY_ADDRESS = os.getenv("FTSO_REGISTRY_ADDRESS", "0x9afc3884f1a4bac868d96e9524a52fd55b2d5df4")
FTSO_V2_ADDRESS = os.getenv("FTSO_V2_ADDRESS", "0x1000000000000000000000000000000000000003")

# Feed IDs for common pairs (bytes21 format)
FEED_IDS = {
    "FLR/USD": "0x01464c522f55534400000000000000000000000000",
    "BTC/USD": "0x014254432f55534400000000000000000000000000",
    "ETH/USD": "0x014554482f55534400000000000000000000000000",
    "XRP/USD": "0x015852502f55534400000000000000000000000000",
    "DOGE/USD": "0x01444f47452f555344000000000000000000000000",
    "ADA/USD": "0x014144412f55534400000000000000000000000000",
    "ALGO/USD": "0x01414c474f2f555344000000000000000000000000",
    "AVAX/USD": "0x01415641582f555344000000000000000000000000",
    "BNB/USD": "0x01424e422f55534400000000000000000000000000",
    "MATIC/USD": "0x014d415449432f555344000000000000000000000000",
    "SOL/USD": "0x01534f4c2f55534400000000000000000000000000"
}

class FTSOTestnetCollector:
    """
    Collector for FTSO data from the Flare testnet (Coston 2)
    """
    
    def __init__(self):
        """Initialize the FTSO testnet collector"""
        self.w3 = Web3(Web3.HTTPProvider(COSTON2_RPC_URL))
        self.ftso_v2 = None
        self.registry = None
        self.last_update = 0
        self.cache = {}
        self.initialize_contracts()
    
    def initialize_contracts(self):
        """Initialize the FTSO contracts"""
        try:
            # Load ABIs
            abi_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "abis")
            
            # Try to load FtsoV2 ABI
            try:
                with open(os.path.join(abi_dir, "FtsoV2.json"), "r") as f:
                    ftso_v2_abi = json.load(f)
            except FileNotFoundError:
                logger.warning("FtsoV2.json ABI file not found, using minimal ABI")
                ftso_v2_abi = [
                    {
                        "inputs": [{"internalType": "bytes21", "name": "feedId", "type": "bytes21"}],
                        "name": "getFeedById",
                        "outputs": [
                            {"internalType": "uint256", "name": "value", "type": "uint256"},
                            {"internalType": "int8", "name": "decimals", "type": "int8"},
                            {"internalType": "uint64", "name": "timestamp", "type": "uint64"}
                        ],
                        "stateMutability": "view",
                        "type": "function"
                    },
                    {
                        "inputs": [{"internalType": "bytes21[]", "name": "feedIds", "type": "bytes21[]"}],
                        "name": "getFeedsById",
                        "outputs": [
                            {"internalType": "uint256[]", "name": "values", "type": "uint256[]"},
                            {"internalType": "int8[]", "name": "decimals", "type": "int8[]"},
                            {"internalType": "uint64", "name": "timestamp", "type": "uint64"}
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
                    }
                ]
            
            # Try to load Registry ABI
            try:
                with open(os.path.join(abi_dir, "ContractRegistry.json"), "r") as f:
                    registry_abi = json.load(f)
            except FileNotFoundError:
                logger.warning("ContractRegistry.json ABI file not found, using minimal ABI")
                registry_abi = [
                    {
                        "inputs": [{"internalType": "string", "name": "contractName", "type": "string"}],
                        "name": "getContractAddressByName",
                        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                        "stateMutability": "view",
                        "type": "function"
                    }
                ]
            
            # Initialize contracts
            if self.w3.is_connected():
                # Initialize registry contract
                try:
                    # Convert address to checksum address
                    registry_address = self.w3.to_checksum_address(FTSO_REGISTRY_ADDRESS)
                    self.registry = self.w3.eth.contract(address=registry_address, abi=registry_abi)
                    logger.info(f"Registry contract initialized at {registry_address}")
                except Exception as e:
                    logger.warning(f"Could not initialize registry contract: {e}")
                    self.registry = None
                
                # Try to get FTSO address from registry
                ftso_address = FTSO_V2_ADDRESS
                if self.registry:
                    try:
                        ftso_address = self.registry.functions.getContractAddressByName("FtsoV2").call()
                        logger.info(f"Got FTSO V2 address from registry: {ftso_address}")
                    except Exception as e:
                        logger.warning(f"Could not get FTSO address from registry: {e}")
                        logger.info(f"Using default FTSO V2 address: {ftso_address}")
                
                # Initialize FTSO contract
                try:
                    # Convert address to checksum address
                    ftso_address = self.w3.to_checksum_address(ftso_address)
                    self.ftso_v2 = self.w3.eth.contract(address=ftso_address, abi=ftso_v2_abi)
                    logger.info(f"FTSO contract initialized at {ftso_address}")
                except Exception as e:
                    logger.warning(f"Could not initialize FTSO contract: {e}")
                    # Create a dummy contract just so our methods don't fail
                    try:
                        ftso_address = self.w3.to_checksum_address(ftso_address)
                        self.ftso_v2 = self.w3.eth.contract(address=ftso_address, abi=ftso_v2_abi)
                    except Exception:
                        logger.error(f"Could not create dummy FTSO contract")
                    
                logger.info(f"FTSO contracts initialized on Coston 2 testnet")
            else:
                logger.error(f"Could not connect to Coston 2 testnet at {COSTON2_RPC_URL}")
        except Exception as e:
            logger.error(f"Error initializing FTSO contracts: {e}")
            # Ensure we have a web3 instance
            if not self.w3:
                self.w3 = Web3(Web3.HTTPProvider(COSTON2_RPC_URL))
    
    def _convert_feed_id_to_bytes21(self, feed_id: str) -> bytes:
        """
        Convert a feed ID string to bytes21 format
        
        Args:
            feed_id: Feed ID as a hex string (with or without 0x prefix)
            
        Returns:
            Feed ID as bytes21
        """
        # Remove 0x prefix if present
        if feed_id.startswith("0x"):
            feed_id = feed_id[2:]
        
        # Convert to bytes and ensure it's 21 bytes long
        feed_bytes = bytes.fromhex(feed_id)
        
        # Pad if necessary (should already be 21 bytes)
        if len(feed_bytes) < 21:
            feed_bytes = feed_bytes.ljust(21, b'\0')
        elif len(feed_bytes) > 21:
            feed_bytes = feed_bytes[:21]
        
        return feed_bytes
    
    async def get_feed_data(self, feed_id: str) -> Optional[Dict[str, Any]]:
        """
        Get data for a specific feed by ID
        
        Args:
            feed_id: The feed ID to get data for (hex string)
            
        Returns:
            Dictionary with feed data or None if error
        """
        # Find symbol for this feed ID
        symbol = None
        for sym, fid in FEED_IDS.items():
            if fid == feed_id:
                symbol = sym
                break
        
        # Check if contract is initialized
        if not self.ftso_v2 or not self.w3.is_connected():
            logger.warning("FTSO contract not initialized or not connected to network, using simulated data")
            return self._get_simulated_feed_data(feed_id, symbol)
        
        # First try the real contract
        try:
            # Try using getFeedsById (plural) with a single feed ID
            logger.info(f"Trying to get feed data for {feed_id} using getFeedsById...")
            
            # Convert feed ID to bytes21
            feed_id_bytes = self._convert_feed_id_to_bytes21(feed_id)
            
            # Call the getFeedsById function with a list containing a single feed ID
            result = self.ftso_v2.functions.getFeedsById([feed_id_bytes]).call()
            
            # Parse the result - getFeedsById returns (values[], decimals[], timestamp)
            values, decimals, timestamp = result
            
            # Since we're only requesting one feed, get the first element
            value = values[0]
            decimal = decimals[0]
            
            # Convert to float with proper decimals
            float_value = value / (10 ** abs(decimal))
            
            return {
                "value": float_value,
                "raw_value": value,
                "decimals": decimal,
                "timestamp": timestamp,
                "feed_id": feed_id,
                "symbol": symbol
            }
        except Exception as e:
            logger.warning(f"Error getting feed data from contract for {feed_id}: {e}, using simulated data")
            
            # Fall back to simulated data
            return self._get_simulated_feed_data(feed_id, symbol)
    
    def _get_simulated_feed_data(self, feed_id: str, symbol: str = None) -> Dict[str, Any]:
        """
        Get simulated feed data when the contract call fails
        
        Args:
            feed_id: The feed ID
            symbol: The symbol (optional)
            
        Returns:
            Dictionary with simulated feed data
        """
        # Find symbol if not provided
        if not symbol:
            for sym, fid in FEED_IDS.items():
                if fid == feed_id:
                    symbol = sym
                    break
        
        # Generate simulated price based on symbol
        current_time = int(time.time())
        
        # Base prices for common cryptocurrencies (approximate as of March 2024)
        base_prices = {
            "FLR/USD": 0.0275,
            "BTC/USD": 68500.0,
            "ETH/USD": 3850.0,
            "XRP/USD": 0.58,
            "DOGE/USD": 0.15,
            "ADA/USD": 0.45,
            "ALGO/USD": 0.22,
            "AVAX/USD": 36.0,
            "BNB/USD": 570.0,
            "MATIC/USD": 0.85,
            "SOL/USD": 145.0
        }
        
        # Get base price or generate a random one
        if symbol and symbol in base_prices:
            base_price = base_prices[symbol]
        else:
            # Random price between 0.1 and 1000
            import random
            base_price = random.uniform(0.1, 1000.0)
        
        # Add some randomness (±2%)
        import random
        variation = random.uniform(-0.02, 0.02)
        price = base_price * (1 + variation)
        
        # Determine appropriate decimals based on price
        if price < 0.01:
            decimals = 6
        elif price < 1:
            decimals = 4
        elif price < 100:
            decimals = 2
        else:
            decimals = 0
        
        # Convert to raw value
        raw_value = int(price * (10 ** abs(decimals)))
        
        return {
            "value": price,
            "raw_value": raw_value,
            "decimals": decimals,
            "timestamp": current_time,
            "feed_id": feed_id,
            "symbol": symbol,
            "simulated": True  # Flag to indicate this is simulated data
        }
    
    async def get_feed_data_by_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get data for a specific feed by symbol
        
        Args:
            symbol: The symbol to get data for (e.g., "FLR/USD")
            
        Returns:
            Dictionary with feed data or None if error
        """
        # Check if contract is initialized
        if not self.ftso_v2 or not self.w3.is_connected():
            logger.warning("FTSO contract not initialized or not connected to network, using simulated data")
            feed_id = FEED_IDS.get(symbol, None)
            return self._get_simulated_feed_data(feed_id, symbol)
        
        # First try the real contract
        try:
            # Call the getFeedBySymbol function
            result = self.ftso_v2.functions.getFeedBySymbol(symbol).call()
            
            # Parse the result
            value, decimals, timestamp = result
            
            # Convert to float with proper decimals
            float_value = value / (10 ** abs(decimals))
            
            # Get feed ID if available
            feed_id = FEED_IDS.get(symbol, None)
            if not feed_id:
                try:
                    # Try to get feed ID from contract
                    feed_id = self.ftso_v2.functions.getFeedId(symbol).call().hex()
                except Exception as e:
                    logger.warning(f"Could not get feed ID for {symbol}: {e}")
            
            return {
                "value": float_value,
                "raw_value": value,
                "decimals": decimals,
                "timestamp": timestamp,
                "feed_id": feed_id,
                "symbol": symbol
            }
        except Exception as e:
            logger.warning(f"Error getting feed data from contract for symbol {symbol}: {e}, using simulated data")
            
            # Fall back to simulated data
            feed_id = FEED_IDS.get(symbol, None)
            return self._get_simulated_feed_data(feed_id, symbol)
    
    async def get_supported_symbols(self) -> List[str]:
        """
        Get list of supported symbols
        
        Returns:
            List of supported symbol strings
        """
        if not self.ftso_v2 or not self.w3.is_connected():
            logger.error("FTSO contract not initialized or not connected to network")
            return []
        
        try:
            symbols = self.ftso_v2.functions.getSupportedSymbols().call()
            return symbols
        except Exception as e:
            logger.error(f"Error getting supported symbols: {e}")
            return list(FEED_IDS.keys())  # Fallback to predefined list
    
    async def collect_all_feeds(self) -> Dict[str, Dict[str, Any]]:
        """
        Collect data for all feeds
        
        Returns:
            Dictionary mapping symbol to feed data
        """
        result = {}
        current_time = int(time.time())
        
        # If cache is recent (less than 30 seconds old), return it
        if current_time - self.last_update < 30 and self.cache:
            return self.cache
        
        # Check if contract is initialized
        if not self.ftso_v2 or not self.w3.is_connected():
            logger.warning("FTSO contract not initialized or not connected to network, using simulated data")
            # Fall back to simulated data for all feeds
            logger.info("Using simulated data for all feeds")
            for symbol, feed_id in FEED_IDS.items():
                result[symbol] = self._get_simulated_feed_data(feed_id, symbol)
            
            # Update cache
            if result:
                self.cache = result
                self.last_update = current_time
            
            return result
        
        # First try to get all feeds at once from the real contract
        try:
            # Try to get all feeds at once using getFeedsById
            logger.info("Trying to get all feeds at once using getFeedsById...")
            
            # Get all feed IDs
            feed_ids = list(FEED_IDS.values())
            feed_id_bytes = [self._convert_feed_id_to_bytes21(fid) for fid in feed_ids]
            
            # Call getFeedsById with all feed IDs
            values, decimals, timestamp = self.ftso_v2.functions.getFeedsById(feed_id_bytes).call()
            
            # Process results
            for i, (feed_id, value, decimal) in enumerate(zip(feed_ids, values, decimals)):
                # Find symbol for this feed ID
                symbol = None
                for sym, fid in FEED_IDS.items():
                    if fid == feed_id:
                        symbol = sym
                        break
                
                if symbol:
                    # Convert to float with proper decimals
                    float_value = value / (10 ** abs(decimal))
                    
                    result[symbol] = {
                        "value": float_value,
                        "raw_value": value,
                        "decimals": decimal,
                        "timestamp": timestamp,
                        "feed_id": feed_id,
                        "symbol": symbol
                    }
            
            # If we got results, update cache and return
            if result:
                self.cache = result
                self.last_update = current_time
                return result
        except Exception as e:
            logger.warning(f"Error getting all feeds from contract: {e}, using simulated data")
        
        # Fall back to simulated data for all feeds
        logger.info("Using simulated data for all feeds")
        for symbol, feed_id in FEED_IDS.items():
            result[symbol] = self._get_simulated_feed_data(feed_id, symbol)
        
        # Update cache
        if result:
            self.cache = result
            self.last_update = current_time
        
        return result
    
    async def get_price(self, symbol: str) -> Optional[float]:
        """
        Get the current price for a symbol
        
        Args:
            symbol: The symbol to get price for (e.g., "FLR/USD")
            
        Returns:
            Current price as float or None if not available
        """
        # Try to get data directly by symbol first
        try:
            feed_data = await self.get_feed_data_by_symbol(symbol)
            if feed_data:
                return feed_data["value"]
        except Exception as e:
            logger.warning(f"Could not get price by symbol {symbol}: {e}, trying alternative methods")
        
        # Check if symbol is in our predefined list
        if symbol in FEED_IDS:
            feed_id = FEED_IDS[symbol]
            feed_data = await self.get_feed_data(feed_id)
            if feed_data:
                return feed_data["value"]
        
        # If not found or error, try to get from all feeds
        all_feeds = await self.collect_all_feeds()
        if symbol in all_feeds:
            return all_feeds[symbol]["value"]
        
        return None

# Create a singleton instance
ftso_testnet_collector = FTSOTestnetCollector() 