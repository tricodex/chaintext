from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import time
import hashlib
from loguru import logger

from app.services.rag import ChainContextRAG, EmbeddingService
from app.services.trust import TrustScoreCalculator
from app.services.tee import TEEAttestationGenerator, OnChainVerifier
from app.services.ftso import FTSODataCollector
from app.core.db import mongodb, redis, qdrant_client
from app.services.ftso_testnet import ftso_testnet_collector, FEED_IDS

router = APIRouter()

# Models
class QueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = None

class VerifyRequest(BaseModel):
    attestation: Dict[str, Any]

class TrustScoreRequest(BaseModel):
    information: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: int

# Services
trust_calculator = TrustScoreCalculator()
tee_attestation = TEEAttestationGenerator()
embedding_service = EmbeddingService()
rag_service = ChainContextRAG(embedding_service, trust_calculator, tee_attestation)
on_chain_verifier = OnChainVerifier()
ftso_collector = FTSODataCollector()

# Dependency to ensure db clients are set
async def get_rag_service():
    if not hasattr(get_rag_service, "initialized"):
        await rag_service.set_db_clients(mongodb, qdrant_client, redis)
        await embedding_service.set_redis_client(redis)
        await ftso_collector.set_redis_client(redis)
        get_rag_service.initialized = True
    return rag_service

# Routes
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    from app.core.config import settings
    
    return {
        "status": "ok",
        "version": settings.VERSION,
        "timestamp": int(time.time())
    }

@router.post("/query")
async def query(
    request: QueryRequest, 
    background_tasks: BackgroundTasks,
    rag_service: ChainContextRAG = Depends(get_rag_service)
):
    """Submit a query to ChainContext"""
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    query_id = hashlib.md5(f"{request.query}-{time.time()}".encode()).hexdigest()
    logger.info(f"Received query: {request.query} (ID: {query_id})")
    
    # Check if Gemini is available
    from app.core.genai import gemini_client
    if not hasattr(gemini_client, 'available') or not gemini_client.available:
        logger.warning("Gemini API is not available, returning error response")
        return {
            "query_id": query_id,
            "query": request.query,
            "answer": "I'm currently unable to process your query because the Gemini API is not available. Please ensure you have set up the GEMINI_API_KEY in your .env file.",
            "confidence": 0.0,
            "sources": [],
            "attestation": {
                "simulated": True,
                "timestamp": int(time.time()),
                "data_hash": hashlib.md5(request.query.encode()).hexdigest()
            },
            "error": "Gemini API not available"
        }
    
    result = await rag_service.answer_query(request.query, request.user_id)
    
    # Add FTSO data collection to background tasks
    # This ensures we're constantly updating our data store
    try:
        background_tasks.add_task(ftso_collector.collect_2s_data)
    except Exception as e:
        logger.warning(f"Failed to add FTSO data collection to background tasks: {e}")
    
    return result

@router.post("/verify")
async def verify(request: VerifyRequest):
    """Verify an attestation on-chain"""
    if not request.attestation:
        raise HTTPException(status_code=400, detail="Attestation cannot be empty")
    
    verification_result = await on_chain_verifier.verify_attestation(request.attestation)
    return verification_result

@router.post("/calculate-trust")
async def calculate_trust(request: TrustScoreRequest):
    """Calculate trust score for a piece of information"""
    if not request.information:
        raise HTTPException(status_code=400, detail="Information cannot be empty")
    
    score = trust_calculator.calculate_trust_score(request.information)
    factors = trust_calculator.get_trust_factor_breakdown(request.information)
    
    return {
        "trust_score": score,
        "factors": factors
    }

@router.get("/trust-factors")
async def get_trust_factors():
    """Get information about trust factors"""
    return {
        "factors": {
            "recency": {
                "description": "How recent the information is",
                "weight": 0.3
            },
            "source_reliability": {
                "description": "Pre-configured reliability of the source",
                "weight": 0.2
            },
            "cross_verification": {
                "description": "How many sources confirm this information",
                "weight": 0.2
            },
            "onchain_verification": {
                "description": "Whether the information is verifiable on-chain",
                "weight": 0.2
            },
            "base": {
                "description": "Base score for all information",
                "weight": 0.1
            }
        },
        "source_reliability": trust_calculator.source_reliability_map
    }

@router.get("/ftso/data")
async def get_ftso_data(symbol: Optional[str] = None):
    """Get FTSO price data"""
    try:
        data_2s = await ftso_collector.collect_2s_data()
        
        if symbol:
            if symbol in data_2s:
                return {
                    "symbol": symbol,
                    "data": data_2s[symbol]
                }
            else:
                raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        return {
            "data": data_2s,
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"Error getting FTSO data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ftso/symbols")
async def get_ftso_symbols():
    """Get supported FTSO symbols"""
    try:
        symbols = await ftso_collector.get_supported_symbols()
        return {
            "symbols": symbols,
            "count": len(symbols),
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"Error getting FTSO symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ftso/testnet/data")
async def get_ftso_testnet_data(symbol: Optional[str] = None):
    """Get FTSO data from Coston 2 testnet"""
    try:
        if symbol:
            # Get data for a specific symbol
            if symbol in FEED_IDS:
                feed_id = FEED_IDS[symbol]
                feed_data = await ftso_testnet_collector.get_feed_data(feed_id)
                
                if feed_data:
                    return {
                        "symbol": symbol,
                        "data": feed_data,
                        "timestamp": int(time.time())
                    }
                else:
                    raise HTTPException(status_code=404, detail=f"Data for symbol {symbol} not found")
            else:
                raise HTTPException(status_code=404, detail=f"Symbol {symbol} not supported")
        
        # Get data for all symbols
        all_feeds = await ftso_testnet_collector.collect_all_feeds()
        
        return {
            "data": all_feeds,
            "count": len(all_feeds),
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"Error getting FTSO testnet data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ftso/testnet/data/{symbol}")
async def get_ftso_testnet_data_by_symbol(symbol: str):
    """Get FTSO data for a specific symbol from Coston 2 testnet"""
    try:
        # URL encoding might change the format, so normalize it
        # If the symbol doesn't contain a slash, try to find a matching symbol
        if '/' not in symbol:
            for known_symbol in FEED_IDS.keys():
                if symbol in known_symbol.split('/')[0]:
                    symbol = known_symbol
                    break
        
        logger.info(f"Getting data for symbol: {symbol}")
        
        if symbol in FEED_IDS:
            feed_id = FEED_IDS[symbol]
            feed_data = await ftso_testnet_collector.get_feed_data(feed_id)
            
            if feed_data:
                return {
                    "symbol": symbol,
                    "data": feed_data,
                    "timestamp": int(time.time())
                }
            else:
                raise HTTPException(status_code=404, detail=f"Data for symbol {symbol} not found")
        else:
            # Try to get from all feeds
            all_feeds = await ftso_testnet_collector.collect_all_feeds()
            for feed_symbol, feed_data in all_feeds.items():
                if symbol in feed_symbol:
                    return {
                        "symbol": feed_symbol,
                        "data": feed_data,
                        "timestamp": int(time.time())
                    }
            
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not supported")
    except Exception as e:
        logger.error(f"Error getting FTSO testnet data for symbol {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ftso/testnet/symbols")
async def get_ftso_testnet_symbols():
    """Get supported FTSO symbols from Coston 2 testnet"""
    try:
        # First try to get from the contract
        symbols = await ftso_testnet_collector.get_supported_symbols()
        
        # If that fails, use our predefined list
        if not symbols:
            symbols = list(ftso_testnet_collector.FEED_IDS.keys())
        
        return {
            "symbols": symbols,
            "count": len(symbols),
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"Error getting FTSO testnet symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ftso/testnet/price/{symbol}")
async def get_ftso_testnet_price(symbol: str):
    """Get current price for a symbol from Coston 2 testnet"""
    try:
        # URL encoding might change the format, so normalize it
        # If the symbol doesn't contain a slash, try to find a matching symbol
        if '/' not in symbol:
            for known_symbol in FEED_IDS.keys():
                if symbol in known_symbol.split('/')[0]:
                    symbol = known_symbol
                    break
        
        logger.info(f"Getting price for symbol: {symbol}")
        price = await ftso_testnet_collector.get_price(symbol)
        
        if price is not None:
            return {
                "symbol": symbol,
                "price": price,
                "timestamp": int(time.time())
            }
        else:
            # Try to get from all feeds
            all_feeds = await ftso_testnet_collector.collect_all_feeds()
            for feed_symbol, feed_data in all_feeds.items():
                if symbol in feed_symbol:
                    return {
                        "symbol": feed_symbol,
                        "price": feed_data["value"],
                        "timestamp": int(time.time())
                    }
            
            raise HTTPException(status_code=404, detail=f"Price for symbol {symbol} not found")
    except Exception as e:
        logger.error(f"Error getting FTSO testnet price: {e}")
        raise HTTPException(status_code=500, detail=str(e))
