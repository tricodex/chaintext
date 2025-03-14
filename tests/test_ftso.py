"""Tests for FTSO data collector"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json
import time

from app.services.ftso import FTSODataCollector

@pytest.fixture
def mock_web3():
    """Create a mock Web3 instance"""
    with patch('app.services.ftso.Web3') as mock_web3:
        # Mock the HTTPProvider
        mock_provider = MagicMock()
        mock_web3.HTTPProvider.return_value = mock_provider
        
        # Mock the Web3 instance
        mock_web3_instance = MagicMock()
        mock_web3.return_value = mock_web3_instance
        
        # Mock the eth.contract method
        mock_contract = MagicMock()
        mock_web3_instance.eth.contract.return_value = mock_contract
        
        # Mock contract functions
        mock_functions = MagicMock()
        mock_contract.functions = mock_functions
        
        # Mock getSupportedSymbols
        mock_get_symbols = MagicMock()
        mock_get_symbols.call.return_value = ["FLR", "BTC", "ETH", "XRP", "USDC"]
        mock_functions.getSupportedSymbols.return_value = mock_get_symbols
        
        # Mock getSupportedSymbolIndex
        mock_get_index = MagicMock()
        mock_get_index.call.return_value = 0  # Just return 0 for all symbols
        mock_functions.getSupportedSymbolIndex.return_value = mock_get_index
        
        # Mock getCurrentPrice
        mock_get_price = MagicMock()
        mock_get_price.call.return_value = [10000000, int(time.time()), 6]  # 10.0 with 6 decimals
        mock_functions.getCurrentPrice.return_value = mock_get_price
        
        yield mock_web3

@pytest.fixture
def mock_redis():
    """Create a mock Redis client"""
    mock = AsyncMock()
    mock.get.return_value = None  # Default to cache miss
    mock.set.return_value = True  # Default to successful set
    return mock

@pytest.fixture
def ftso_collector(mock_web3, mock_redis):
    """Create a FTSO data collector with mocked dependencies"""
    collector = FTSODataCollector(web3_provider="https://mock-provider.example", redis_client=mock_redis)
    return collector

@pytest.mark.asyncio
async def test_get_supported_symbols_cache_miss(ftso_collector, mock_redis):
    """Test get_supported_symbols method with cache miss"""
    # Set up the mock to simulate cache miss
    mock_redis.get.return_value = None
    
    # Call the method
    symbols = await ftso_collector.get_supported_symbols()
    
    # Check the result
    assert symbols == ["FLR", "BTC", "ETH", "XRP", "USDC"]
    
    # Check that cache was checked and set
    mock_redis.get.assert_called_once_with("ftso:symbols")
    mock_redis.set.assert_called_once()

@pytest.mark.asyncio
async def test_get_supported_symbols_cache_hit(ftso_collector, mock_redis):
    """Test get_supported_symbols method with cache hit"""
    # Set up the mock to simulate cache hit
    mock_redis.get.return_value = json.dumps(["FLR", "BTC", "ETH"])
    
    # Call the method
    symbols = await ftso_collector.get_supported_symbols()
    
    # Check the result
    assert symbols == ["FLR", "BTC", "ETH"]
    
    # Check that cache was checked but not set
    mock_redis.get.assert_called_once_with("ftso:symbols")
    mock_redis.set.assert_not_called()

@pytest.mark.asyncio
async def test_collect_2s_data(ftso_collector):
    """Test collect_2s_data method"""
    # Mock the get_supported_symbols method
    ftso_collector.get_supported_symbols = AsyncMock(return_value=["FLR", "BTC", "ETH"])
    
    # Call the method
    prices = await ftso_collector.collect_2s_data()
    
    # Check the result
    assert len(prices) == 3
    assert "FLR" in prices
    assert "BTC" in prices
    assert "ETH" in prices
    
    # Check the structure of a price object
    flr_price = prices["FLR"]
    assert "price" in flr_price
    assert "timestamp" in flr_price
    assert "source" in flr_price
    assert "symbol" in flr_price
    assert "decimals" in flr_price
    
    # Check the values
    assert flr_price["price"] == 10.0  # 10.0 from the mock
    assert flr_price["source"] == "ftso_2s"
    assert flr_price["symbol"] == "FLR"
    assert flr_price["decimals"] == 6

@pytest.mark.asyncio
async def test_collect_90s_data(ftso_collector):
    """Test collect_90s_data method"""
    # Mock the collect_2s_data method to return test data
    test_2s_data = {
        "FLR": {
            "price": 10.0,
            "timestamp": int(time.time()),
            "source": "ftso_2s",
            "symbol": "FLR",
            "decimals": 6
        },
        "BTC": {
            "price": 50000.0,
            "timestamp": int(time.time()),
            "source": "ftso_2s",
            "symbol": "BTC",
            "decimals": 6
        }
    }
    ftso_collector.collect_2s_data = AsyncMock(return_value=test_2s_data)
    
    # Call the method
    prices = await ftso_collector.collect_90s_data()
    
    # Check the result
    assert len(prices) == 2
    assert "FLR" in prices
    assert "BTC" in prices
    
    # Check that the source is changed to ftso_90s
    assert prices["FLR"]["source"] == "ftso_90s"
    assert prices["BTC"]["source"] == "ftso_90s"
    
    # Prices should be slightly different from 2s data
    assert prices["FLR"]["price"] != test_2s_data["FLR"]["price"]
    assert prices["BTC"]["price"] != test_2s_data["BTC"]["price"]
