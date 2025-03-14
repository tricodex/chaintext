"""Tests for Trust Score Calculator"""
import pytest
import time
from app.services.trust import TrustScoreCalculator


@pytest.fixture
def trust_calculator():
    """Fixture for TrustScoreCalculator"""
    return TrustScoreCalculator()


def test_calculate_trust_score_basic(trust_calculator):
    """Test basic trust score calculation"""
    # Create a test information piece
    info = {
        "source": "flare_docs",
        "timestamp": int(time.time()),
        "content": "Test content",
        "onchain_verified": False
    }
    
    # Calculate trust score
    score = trust_calculator.calculate_trust_score(info)
    
    # Score should be between 0 and 1
    assert 0 <= score <= 1
    
    # For a recent doc with no verification, should be around 0.7
    assert 0.6 <= score <= 0.8


def test_calculate_trust_score_sources(trust_calculator):
    """Test trust scores for different sources"""
    base_info = {
        "timestamp": int(time.time()),
        "content": "Test content",
        "onchain_verified": False
    }
    
    # Test various sources
    sources = [
        ("ftso_2s", 0.8, 0.95),  # Source, min expected, max expected
        ("flare_docs", 0.6, 0.8),
        ("twitter_community", 0.4, 0.6)
    ]
    
    for source, min_expected, max_expected in sources:
        info = {**base_info, "source": source}
        score = trust_calculator.calculate_trust_score(info)
        assert min_expected <= score <= max_expected, f"Score for {source} should be between {min_expected} and {max_expected}, got {score}"


def test_calculate_trust_score_recency(trust_calculator):
    """Test trust score recency factor"""
    now = int(time.time())
    
    # Recent information (now)
    recent_info = {
        "source": "flare_docs",
        "timestamp": now,
        "content": "Recent content",
        "onchain_verified": False
    }
    
    # Old information (30 days ago)
    old_info = {
        "source": "flare_docs",
        "timestamp": now - (30 * 24 * 60 * 60),
        "content": "Old content",
        "onchain_verified": False
    }
    
    recent_score = trust_calculator.calculate_trust_score(recent_info)
    old_score = trust_calculator.calculate_trust_score(old_info)
    
    # Recent information should have higher score
    assert recent_score > old_score
    # Old information should have significantly lower score
    assert recent_score - old_score > 0.1


def test_calculate_trust_score_onchain(trust_calculator):
    """Test on-chain verification impact"""
    base_info = {
        "source": "flare_docs",
        "timestamp": int(time.time()),
        "content": "Test content"
    }
    
    # Without on-chain verification
    unverified_info = {**base_info, "onchain_verified": False}
    
    # With on-chain verification
    verified_info = {**base_info, "onchain_verified": True}
    
    unverified_score = trust_calculator.calculate_trust_score(unverified_info)
    verified_score = trust_calculator.calculate_trust_score(verified_info)
    
    # On-chain verification should increase score
    assert verified_score > unverified_score
    # The difference should be around the bonus value (0.2 * weight)
    assert 0.03 <= verified_score - unverified_score <= 0.06


def test_trust_factor_breakdown(trust_calculator):
    """Test trust factor breakdown"""
    info = {
        "source": "flare_docs",
        "timestamp": int(time.time()),
        "content": "Test content",
        "onchain_verified": True,
        "cross_verifications": 2
    }
    
    factors = trust_calculator.get_trust_factor_breakdown(info)
    
    # Check that all factors are present
    assert "recency" in factors
    assert "source_reliability" in factors
    assert "cross_verification" in factors
    assert "onchain_verification" in factors
    assert "overall_score" in factors
    
    # Check that all factors are between 0 and 1
    for factor, value in factors.items():
        assert 0 <= value <= 1, f"Factor {factor} should be between 0 and 1, got {value}"
    
    # Check that overall score matches direct calculation
    direct_score = trust_calculator.calculate_trust_score(info)
    assert factors["overall_score"] == direct_score


def test_edge_cases(trust_calculator):
    """Test edge cases for trust score calculation"""
    # Empty information
    empty_info = {}
    empty_score = trust_calculator.calculate_trust_score(empty_info)
    assert 0 <= empty_score <= 1, "Empty info should return a valid score"
    
    # Future timestamp
    future_info = {
        "source": "flare_docs",
        "timestamp": int(time.time()) + 86400,  # 1 day in the future
        "content": "Future content"
    }
    future_score = trust_calculator.calculate_trust_score(future_info)
    assert 0 <= future_score <= 1, "Future timestamp should return a valid score"
    
    # Invalid source
    invalid_source_info = {
        "source": "invalid_source",
        "timestamp": int(time.time()),
        "content": "Invalid source content"
    }
    invalid_source_score = trust_calculator.calculate_trust_score(invalid_source_info)
    assert 0 <= invalid_source_score <= 1, "Invalid source should return a valid score"
