import math
import time
from typing import Dict, List, Optional
from loguru import logger

from app.core.config import settings

class TrustScoreCalculator:
    """Calculator for determining the trustworthiness of information"""
    
    def __init__(self):
        """Initialize the trust score calculator with source reliability map"""
        self.source_reliability_map = settings.SOURCE_RELIABILITY
        logger.debug(f"Initialized TrustScoreCalculator with sources: {self.source_reliability_map}")
    
    def calculate_trust_score(self, information: Dict) -> float:
        """Calculate a composite trust score for a piece of information"""
        try:
            # Base score starts at 0.5 (neutral)
            base_score = 0.5
            
            # Recency factor (1.0 for very recent, scaling down for older information)
            recency_factor = self._calculate_recency_factor(information.get('timestamp', 0))
            
            # Source reliability (pre-configured trusted sources have higher weights)
            source_reliability = self._get_source_reliability(information.get('source', ''))
            
            # Cross-verification factor
            cross_verification = self._calculate_cross_verification(
                information.get('content', ''),
                information.get('cross_verifications', 0)
            )
            
            # On-chain verification bonus
            onchain_bonus = 0.2 if information.get('onchain_verified', False) else 0.0
            
            # Calculate composite score (weighted average)
            score = (
                base_score * 0.1 +            # Base weight
                recency_factor * 0.3 +        # Recency is important
                source_reliability * 0.2 +    # Source reliability
                cross_verification * 0.2 +    # Cross-verification
                onchain_bonus * 0.2           # On-chain verification bonus
            )
            
            # Normalize to 0-1 range
            return min(max(score, 0.0), 1.0)
        except Exception as e:
            logger.error(f"Error calculating trust score: {e}")
            return 0.5  # Default to neutral score on error
    
    def _calculate_recency_factor(self, timestamp: int) -> float:
        """Calculate how recent the information is"""
        now = time.time()
        
        # If timestamp is in the future or invalid, use current time
        if timestamp <= 0 or timestamp > now:
            return 1.0
            
        age_in_days = (now - timestamp) / (60 * 60 * 24)
        
        # Exponential decay function
        # 1.0 for very recent, down to ~0.1 after 30 days
        return math.exp(-0.1 * age_in_days)
    
    def _get_source_reliability(self, source: str) -> float:
        """Get pre-configured reliability score for a source"""
        return self.source_reliability_map.get(source, 0.3)  # Default for unknown sources
    
    def _calculate_cross_verification(self, content: str, verification_count: int = 0) -> float:
        """Check how many sources confirm this information"""
        # If we have a direct count of verifications, use that
        if verification_count > 0:
            confirmation_count = verification_count
        else:
            # Otherwise, we would implement content-based verification
            # This is a placeholder for actual implementation
            confirmation_count = 1  # Default to 1 (self-confirmation)
        
        # Sigmoid function to score based on confirmation count
        # 0.0 for 0 confirmations, ~0.5 for 1, ~0.76 for 2, ~0.88 for 3, approaching 1.0
        return 2.0 / (1.0 + math.exp(-0.5 * confirmation_count)) - 1.0
        
    def get_trust_factor_breakdown(self, information: Dict) -> Dict:
        """Get a breakdown of trust factors for an information piece"""
        recency_factor = self._calculate_recency_factor(information.get('timestamp', 0))
        source_reliability = self._get_source_reliability(information.get('source', ''))
        cross_verification = self._calculate_cross_verification(
            information.get('content', ''),
            information.get('cross_verifications', 0)
        )
        onchain_bonus = 0.2 if information.get('onchain_verified', False) else 0.0
        
        return {
            "recency": recency_factor,
            "source_reliability": source_reliability,
            "cross_verification": cross_verification,
            "onchain_verification": onchain_bonus,
            "overall_score": self.calculate_trust_score(information)
        }
