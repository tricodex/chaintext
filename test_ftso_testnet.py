#!/usr/bin/env python3
"""
Test script for FTSO data access on Flare Testnet (Coston 2)
"""

import os
import json
import asyncio
import time
from dotenv import load_dotenv
from loguru import logger
import pandas as pd
from tabulate import tabulate as tabulate_func

# Import our FTSO testnet collector
from app.services.ftso_testnet import ftso_testnet_collector, FEED_IDS

# Load environment variables
load_dotenv()

# Configure logging
logger.remove()
logger.add(lambda msg: print(msg, end=""), colorize=True, level="INFO")

async def test_connection():
    """Test connection to Coston 2 testnet"""
    logger.info("Testing connection to Coston 2 testnet...")
    
    if ftso_testnet_collector.w3.is_connected():
        chain_id = ftso_testnet_collector.w3.eth.chain_id
        latest_block = ftso_testnet_collector.w3.eth.block_number
        logger.info(f"✅ Connected to Coston 2 testnet")
        logger.info(f"  Chain ID: {chain_id}")
        logger.info(f"  Latest block: {latest_block}")
        return True
    else:
        logger.error(f"❌ Failed to connect to Coston 2 testnet")
        return False

async def test_registry():
    """Test contract registry access"""
    logger.info("Testing contract registry access...")
    
    if not ftso_testnet_collector.registry:
        logger.error("❌ Contract registry not initialized")
        return False
    
    try:
        # Try to get FTSO address from registry
        ftso_address = ftso_testnet_collector.registry.functions.getContractAddressByName("FtsoV2").call()
        logger.info(f"✅ Got FTSO V2 address from registry: {ftso_address}")
        
        # Try to get all contract names
        try:
            all_contracts = ftso_testnet_collector.registry.functions.getAllContractNames().call()
            logger.info(f"✅ Available contracts in registry: {', '.join(all_contracts)}")
        except Exception as e:
            logger.warning(f"⚠️ Could not get all contract names: {e}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error accessing contract registry: {e}")
        return False

async def test_ftso_contract():
    """Test FTSO contract access"""
    logger.info("Testing FTSO contract access...")
    
    if not ftso_testnet_collector.ftso_v2:
        logger.error("❌ FTSO contract not initialized")
        return False
    
    try:
        # Try to get supported symbols
        symbols = await ftso_testnet_collector.get_supported_symbols()
        if symbols:
            logger.info(f"✅ Got {len(symbols)} supported symbols")
            logger.info(f"  First 5 symbols: {', '.join(symbols[:5])}")
        else:
            logger.warning("⚠️ No supported symbols returned, using predefined list")
            symbols = list(FEED_IDS.keys())
            logger.info(f"  Using {len(symbols)} predefined symbols: {', '.join(symbols[:5])}...")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error accessing FTSO contract: {e}")
        return False

async def test_feed_data():
    """Test getting feed data"""
    logger.info("Testing feed data access...")
    
    # Test a few common symbols
    test_symbols = ["FLR/USD", "BTC/USD", "ETH/USD"]
    results = []
    
    for symbol in test_symbols:
        try:
            logger.info(f"Getting data for {symbol}...")
            
            # Try to get data by symbol first
            logger.info(f"Trying to get data by symbol directly...")
            feed_data = await ftso_testnet_collector.get_feed_data_by_symbol(symbol)
            
            if feed_data:
                logger.info(f"✅ Got data for {symbol} by symbol")
                logger.info(f"  Value: {feed_data['value']}")
                logger.info(f"  Timestamp: {feed_data['timestamp']} ({time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(feed_data['timestamp']))})")
                
                results.append({
                    "Symbol": symbol,
                    "Price": feed_data["value"],
                    "Decimals": feed_data["decimals"],
                    "Timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(feed_data["timestamp"])),
                    "Method": "By Symbol"
                })
                
                # Continue to next symbol if we got data
                continue
            else:
                logger.warning(f"⚠️ Could not get data for {symbol} by symbol, trying by feed ID...")
            
            # Fall back to feed ID if available
            if symbol in FEED_IDS:
                feed_id = FEED_IDS[symbol]
                logger.info(f"Getting data for {symbol} (Feed ID: {feed_id})...")
                
                feed_data = await ftso_testnet_collector.get_feed_data(feed_id)
                if feed_data:
                    logger.info(f"✅ Got data for {symbol} by feed ID")
                    logger.info(f"  Value: {feed_data['value']}")
                    logger.info(f"  Timestamp: {feed_data['timestamp']} ({time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(feed_data['timestamp']))})")
                    
                    results.append({
                        "Symbol": symbol,
                        "Price": feed_data["value"],
                        "Decimals": feed_data["decimals"],
                        "Timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(feed_data["timestamp"])),
                        "Method": "By Feed ID"
                    })
                else:
                    logger.error(f"❌ Failed to get data for {symbol}")
            else:
                logger.warning(f"⚠️ No feed ID defined for {symbol}")
        except Exception as e:
            logger.error(f"❌ Error getting data for {symbol}: {e}")
    
    return results

async def test_all_feeds():
    """Test getting all feed data"""
    logger.info("Testing collection of all feeds...")
    
    try:
        all_feeds = await ftso_testnet_collector.collect_all_feeds()
        if all_feeds:
            logger.info(f"✅ Got data for {len(all_feeds)} feeds")
            
            # Convert to DataFrame for nice display
            results = []
            for symbol, data in all_feeds.items():
                method = "By Symbol" if data.get("symbol") else "By Feed ID"
                results.append({
                    "Symbol": symbol,
                    "Price": data["value"],
                    "Decimals": data["decimals"],
                    "Timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data["timestamp"])),
                    "Method": method
                })
            
            return results
        else:
            logger.error("❌ Failed to get any feed data")
            return []
    except Exception as e:
        logger.error(f"❌ Error collecting all feeds: {e}")
        return []

async def main():
    """Main test function"""
    logger.info("Starting FTSO testnet data access test...")
    
    # Test connection
    connected = await test_connection()
    if not connected:
        logger.error("❌ Cannot proceed without connection to Coston 2 testnet")
        return
    
    # Test registry
    registry_ok = await test_registry()
    
    # Test FTSO contract
    ftso_ok = await test_ftso_contract()
    
    # Test feed data
    feed_results = await test_feed_data()
    
    # Test all feeds
    all_feed_results = await test_all_feeds()
    
    # Display results in a table
    if feed_results:
        logger.info("\nFeed Data Results:")
        df = pd.DataFrame(feed_results)
        print(tabulate_func(df, headers="keys", tablefmt="pretty", showindex=False))
    
    if all_feed_results:
        logger.info("\nAll Feeds Results:")
        df = pd.DataFrame(all_feed_results)
        print(tabulate_func(df, headers="keys", tablefmt="pretty", showindex=False))
    
    logger.info("\nFTSO testnet data access test completed")
    
    # Summary
    logger.info("\nTest Summary:")
    logger.info(f"Connection to Coston 2: {'✅ Success' if connected else '❌ Failed'}")
    logger.info(f"Contract Registry Access: {'✅ Success' if registry_ok else '❌ Failed'}")
    logger.info(f"FTSO Contract Access: {'✅ Success' if ftso_ok else '❌ Failed'}")
    logger.info(f"Feed Data Access: {'✅ Success' if feed_results else '❌ Failed'}")
    logger.info(f"All Feeds Collection: {'✅ Success' if all_feed_results else '❌ Failed'}")

if __name__ == "__main__":
    # Install required packages if not already installed
    try:
        import pandas
        import tabulate
    except ImportError:
        import subprocess
        import sys
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "tabulate"])
        print("Packages installed successfully")
    
    # Run the test
    asyncio.run(main()) 