"""API models for ChainContext"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import time


class QueryRequest(BaseModel):
    """Request model for querying ChainContext"""
    query: str = Field(..., description="The user's query")
    user_id: Optional[str] = Field(None, description="Optional user identifier")


class SourceInfo(BaseModel):
    """Information about a source used in a response"""
    text: str = Field(..., description="Text content from the source")
    source: str = Field(..., description="Source identifier (e.g., ftso_2s, flare_docs)")
    source_type: str = Field(..., description="Human-readable source type")
    trust_score: float = Field(..., description="Trust score for this source (0-1)")
    url: Optional[str] = Field(None, description="URL of the source, if available")
    timestamp: Optional[int] = Field(None, description="Timestamp of the source")


class AttestationInfo(BaseModel):
    """Information about the attestation for a response"""
    quote: Optional[str] = Field(None, description="TPM quote")
    data_hash: str = Field(..., description="Hash of the query, context, and response")
    signature: Optional[str] = Field(None, description="Signature of the data hash")
    timestamp: int = Field(..., description="Timestamp of the attestation")
    nonce: Optional[str] = Field(None, description="Nonce used for the attestation")
    simulated: bool = Field(False, description="Whether this is a simulated attestation")


class QueryResponse(BaseModel):
    """Response model for a ChainContext query"""
    query_id: str = Field(..., description="Unique identifier for the query")
    query: str = Field(..., description="The original query")
    answer: str = Field(..., description="The generated answer")
    confidence: float = Field(..., description="Confidence in the answer (0-1)")
    reasoning: Optional[str] = Field(None, description="Reasoning behind the answer")
    sources: List[SourceInfo] = Field(default_factory=list, description="Sources used for the answer")
    attestation: AttestationInfo = Field(..., description="Attestation information")
    processing_time: Optional[float] = Field(None, description="Time taken to process the query in seconds")
    error: Optional[str] = Field(None, description="Error message, if any")


class VerifyRequest(BaseModel):
    """Request model for verifying an attestation"""
    attestation: Dict[str, Any] = Field(..., description="Attestation object to verify")


class VerifyResponse(BaseModel):
    """Response model for attestation verification"""
    verified: bool = Field(..., description="Whether the attestation was verified")
    simulated: bool = Field(False, description="Whether this is a simulated verification")
    timestamp: int = Field(default_factory=lambda: int(time.time()), description="Timestamp of verification")
    transaction_hash: Optional[str] = Field(None, description="Hash of the verification transaction")
    error: Optional[str] = Field(None, description="Error message, if verification failed")


class TrustScoreRequest(BaseModel):
    """Request model for calculating a trust score"""
    information: Dict[str, Any] = Field(..., description="Information to calculate trust score for")


class TrustFactorInfo(BaseModel):
    """Information about a trust factor"""
    description: str = Field(..., description="Description of the trust factor")
    weight: float = Field(..., description="Weight of the factor in the trust score")


class TrustFactorsResponse(BaseModel):
    """Response model for trust factors information"""
    factors: Dict[str, TrustFactorInfo] = Field(..., description="Trust factors and their weights")
    source_reliability: Dict[str, float] = Field(..., description="Reliability scores for different sources")


class TrustScoreResponse(BaseModel):
    """Response model for trust score calculation"""
    trust_score: float = Field(..., description="Calculated trust score (0-1)")
    factors: Dict[str, float] = Field(..., description="Breakdown of trust factors")


class FTSOPriceInfo(BaseModel):
    """Information about a FTSO price feed"""
    price: float = Field(..., description="Price value")
    timestamp: int = Field(..., description="Timestamp of the price")
    source: str = Field(..., description="Source of the price (e.g., ftso_2s)")
    symbol: str = Field(..., description="Symbol (e.g., FLR, BTC)")
    decimals: int = Field(..., description="Decimals for the price")


class FTSODataResponse(BaseModel):
    """Response model for FTSO data"""
    data: Dict[str, FTSOPriceInfo] = Field(..., description="FTSO price data by symbol")
    timestamp: int = Field(default_factory=lambda: int(time.time()), description="Timestamp of the response")


class FTSOSymbolsResponse(BaseModel):
    """Response model for FTSO symbols"""
    symbols: List[str] = Field(..., description="List of supported FTSO symbols")
    count: int = Field(..., description="Number of symbols")
    timestamp: int = Field(default_factory=lambda: int(time.time()), description="Timestamp of the response")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Status of the service (ok/error)")
    version: str = Field(..., description="Version of the service")
    timestamp: int = Field(default_factory=lambda: int(time.time()), description="Timestamp of the response")
