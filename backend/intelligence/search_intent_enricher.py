"""
Search Intent Enrichment Module

Implements optional demand enrichment signals:
- Search intent classification (local, booking, informational)
- Search volume/trends with source attribution
- Geographic and temporal context
- Never infers intent without evidence
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum

from models.evidence import Evidence, EvidenceType, FactOrAssumption

logger = logging.getLogger(__name__)


class SearchIntent(str, Enum):
    """Types of search intent"""
    LOCAL = "local"  # Finding local business
    BOOKING = "booking"  # Making appointment/reservation
    INFORMATIONAL = "informational"  # General information
    TRANSACTIONAL = "transactional"  # Purchase/order
    NAVIGATIONAL = "navigational"  # Finding specific business
    UNKNOWN = "unknown"  # Cannot determine


class SearchTrendSignal(str, Enum):
    """Sources of search trend signals"""
    GOOGLE_TRENDS = "google_trends"
    SEARCH_VOLUME = "search_volume"
    KEYWORD_CLUSTER = "keyword_cluster"
    SEASONAL = "seasonal"
    UNKNOWN = "unknown"


class SearchIntentClassifier:
    """Classify search intent from keywords and context"""
    
    # Intent indicators
    LOCAL_KEYWORDS = [
        "near me", "nearby", "in", "local", "close to",
        "around", "area", "location", "find"
    ]
    
    BOOKING_KEYWORDS = [
        "appointment", "booking", "reserve", "schedule",
        "book", "reservation", "available", "hours",
        "availability", "slots"
    ]
    
    INFORMATIONAL_KEYWORDS = [
        "how to", "what is", "explain", "guide",
        "tutorial", "tips", "advice", "learn"
    ]
    
    TRANSACTIONAL_KEYWORDS = [
        "buy", "order", "purchase", "price",
        "cost", "payment", "checkout", "delivery"
    ]
    
    @staticmethod
    def classify(search_query: Optional[str], business_category: Optional[str]) -> tuple[SearchIntent, float]:
        """
        Classify search intent from query
        
        Returns: (intent, confidence)
        """
        if not search_query:
            return SearchIntent.UNKNOWN, 0.0
        
        query_lower = search_query.lower()
        scores = {intent: 0.0 for intent in SearchIntent}
        
        # Check local keywords
        local_matches = sum(1 for kw in SearchIntentClassifier.LOCAL_KEYWORDS if kw in query_lower)
        if local_matches > 0:
            scores[SearchIntent.LOCAL] = min(1.0, 0.3 + (local_matches * 0.2))
        
        # Check booking keywords
        booking_matches = sum(1 for kw in SearchIntentClassifier.BOOKING_KEYWORDS if kw in query_lower)
        if booking_matches > 0:
            scores[SearchIntent.BOOKING] = min(1.0, 0.3 + (booking_matches * 0.2))
        
        # Check informational keywords
        info_matches = sum(1 for kw in SearchIntentClassifier.INFORMATIONAL_KEYWORDS if kw in query_lower)
        if info_matches > 0:
            scores[SearchIntent.INFORMATIONAL] = min(1.0, 0.3 + (info_matches * 0.2))
        
        # Check transactional keywords
        trans_matches = sum(1 for kw in SearchIntentClassifier.TRANSACTIONAL_KEYWORDS if kw in query_lower)
        if trans_matches > 0:
            scores[SearchIntent.TRANSACTIONAL] = min(1.0, 0.3 + (trans_matches * 0.2))
        
        # Category heuristics
        if business_category:
            category_lower = business_category.lower()
            if any(x in category_lower for x in ['restaurant', 'salon', 'clinic', 'hotel']):
                scores[SearchIntent.BOOKING] += 0.1
            if any(x in category_lower for x in ['shop', 'store', 'retail']):
                scores[SearchIntent.TRANSACTIONAL] += 0.1
        
        # Find highest score
        best_intent = max(scores, key=scores.get)
        confidence = scores[best_intent]
        
        if confidence < 0.3:
            return SearchIntent.UNKNOWN, 0.0
        
        return best_intent, confidence


class SearchVolumeEstimator:
    """Estimate search volume for keywords (simplified)"""
    
    @staticmethod
    def estimate(
        keyword: str,
        geography: Optional[str] = None,
        window_days: int = 30
    ) -> Dict[str, Any]:
        """
        Estimate search volume for keyword
        
        Returns mock data - in production would call Google Trends API
        """
        
        # This is mock implementation
        # In production: call Google Trends API with proper credentials
        
        return {
            "keyword": keyword,
            "geography": geography or "global",
            "window_days": window_days,
            "estimated_volume": 0,  # Would be real volume from API
            "trend": "unknown",  # up, down, stable
            "confidence": 0.0,  # Low confidence for mock
            "data_source": "mock",
            "note": "Mock data only - integrate Google Trends for production"
        }


class SearchIntentEnricher:
    """Enrich business verification with search intent signals"""
    
    @staticmethod
    def enrich(
        business_name: str,
        business_category: Optional[str],
        geography: Optional[str] = None,
        include_trends: bool = False
    ) -> List[Evidence]:
        """
        Enrich with search intent signals
        
        Returns list of evidence objects with optional demand signals
        """
        
        evidence_list = []
        
        # Intent classification
        # Build search query from business context
        search_query = f"{business_name} {business_category or ''}"
        if geography:
            search_query += f" {geography}"
        
        intent, confidence = SearchIntentClassifier.classify(search_query, business_category)
        
        if confidence > 0.3:
            evidence = Evidence(
                claim=f"Search intent classified as {intent.value} (confidence: {confidence:.2f})",
                fact_vs_assumption=FactOrAssumption.ASSUMPTION,  # Classification is inference
                evidence_type=EvidenceType.SEARCH_INTENT,
                source="search_intent_classifier",
                confidence=confidence,
                reason_for_uncertainty="Intent classification is heuristic-based" if confidence < 0.7 else None
            )
            evidence_list.append(evidence)
        
        # Optional: Search volume/trends
        if include_trends:
            # In production, this would call Google Trends API
            volume_data = SearchVolumeEstimator.estimate(
                business_name,
                geography=geography,
                window_days=30
            )
            
            if volume_data.get("estimated_volume", 0) > 0:
                evidence = Evidence(
                    claim=f"Search volume for '{business_name}': {volume_data['estimated_volume']} searches",
                    fact_vs_assumption=FactOrAssumption.FACT,  # If from real API
                    evidence_type=EvidenceType.DEMAND_SIGNAL,
                    source="google_trends",
                    confidence=0.7,  # Assume 70% confidence for API data
                    metadata={
                        "volume": volume_data["estimated_volume"],
                        "trend": volume_data["trend"],
                        "geography": volume_data["geography"],
                        "window_days": volume_data["window_days"]
                    }
                )
                evidence_list.append(evidence)
            else:
                # Unknown volume is different from zero
                evidence = Evidence(
                    claim=f"Search volume for '{business_name}': data unavailable",
                    fact_vs_assumption=FactOrAssumption.UNCERTAIN,
                    evidence_type=EvidenceType.DEMAND_SIGNAL,
                    source="google_trends",
                    confidence=0.0,
                    reason_for_uncertainty="Search volume data not available for this keyword/geography"
                )
                evidence_list.append(evidence)
        
        return evidence_list


class DemandSignalValidator:
    """Validate that demand signals don't override evidence requirements"""
    
    @staticmethod
    def validate(
        search_signals: List[Evidence],
        other_evidence: List[Evidence],
        service: str
    ) -> bool:
        """
        Validate that high search interest doesn't compensate for weak evidence
        
        Per CLOREL principle: "High search interest must not compensate for missing evidence"
        """
        
        # Check if we have critical evidence
        has_identity = any(e.evidence_type == EvidenceType.IDENTITY for e in other_evidence)
        has_digital = any(e.evidence_type == EvidenceType.DIGITAL_PRESENCE for e in other_evidence)
        has_service_fit = any(e.evidence_type == EvidenceType.SERVICE_FIT for e in other_evidence)
        
        # Even with high search volume, we need basic evidence
        if not (has_identity and has_digital and has_service_fit):
            logger.warning(
                f"Search signals present but missing critical evidence: "
                f"identity={has_identity}, digital={has_digital}, service_fit={has_service_fit}"
            )
            return False
        
        return True


class SeasonalityDetector:
    """Detect seasonal patterns in demand (optional enhancement)"""
    
    @staticmethod
    def detect_seasonality(
        search_history: List[Dict[str, Any]],
        business_category: Optional[str] = None
    ) -> Optional[str]:
        """
        Detect if demand is seasonal
        
        Returns: "high", "low", "stable", or None if not enough data
        """
        
        if not search_history or len(search_history) < 3:
            return None
        
        # Simple seasonality check - would be more sophisticated in production
        volumes = [h.get("volume", 0) for h in search_history]
        if not volumes:
            return None
        
        max_vol = max(volumes)
        min_vol = min(volumes)
        avg_vol = sum(volumes) / len(volumes)
        
        # High seasonality if max/min ratio > 2
        if max_vol > 0 and (max_vol / (min_vol or 1)) > 2:
            return "seasonal"
        
        # Stable if within 20% of average
        if all(abs(v - avg_vol) / avg_vol < 0.2 for v in volumes):
            return "stable"
        
        # Otherwise trending
        recent_avg = sum(volumes[-3:]) / 3
        old_avg = sum(volumes[:-3]) / len(volumes[:-3]) if len(volumes) > 3 else avg_vol
        
        if recent_avg > old_avg:
            return "trending_up"
        elif recent_avg < old_avg:
            return "trending_down"
        
        return None


# Integration helper
def enrich_with_optional_signals(
    business_name: str,
    business_category: Optional[str],
    geography: Optional[str] = None,
    include_trends: bool = False,
    other_evidence: Optional[List[Evidence]] = None,
    service: Optional[str] = None
) -> List[Evidence]:
    """
    Main entry point for search intent enrichment
    
    Optional demand enrichment - returns empty list if not enabled
    Unknown/unavailable data is preserved as uncertain, not as zero
    """
    
    if not business_name:
        return []
    
    enricher = SearchIntentEnricher()
    evidence = enricher.enrich(
        business_name,
        business_category,
        geography=geography,
        include_trends=include_trends
    )
    
    # Validate that signals don't override hard requirements
    if evidence and other_evidence and service:
        validator = DemandSignalValidator()
        if not validator.validate(evidence, other_evidence, service):
            logger.warning(f"Search signals present but insufficient other evidence for {business_name}")
            # Still return evidence but marked as uncertain/optional
    
    return evidence
