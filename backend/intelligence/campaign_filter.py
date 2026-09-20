"""
Campaign Filter Validation System

Implements CLOREL campaign filter validation:
- Required hard filters (city, category, service)
- Optional soft filters (rating, review count)
- Smart handling of missing data (unknown ≠ zero)
- Never lowers standards to hit lead targets
"""

import logging
from typing import Optional, List
from models.evidence import CampaignFilter

logger = logging.getLogger(__name__)


class CampaignFilterValidator:
    """Validate and normalize campaign filters"""
    
    # Valid Upstkey services
    VALID_SERVICES = ["website", "whatsapp_bot", "seo", "booking", "marketing"]
    
    # Valid business categories (examples)
    VALID_CATEGORIES = [
        "restaurant", "shop", "salon", "clinic", "hotel",
        "cafe", "bakery", "fitness", "spa", "photography",
        "plumbing", "electrical", "carpentry", "construction",
        "education", "coaching", "consulting", "legal"
    ]
    
    @staticmethod
    def validate_hard_filters(campaign: CampaignFilter) -> tuple[bool, List[str]]:
        """Validate required hard filters"""
        errors = []
        
        # City is required
        if not campaign.city or not campaign.city.strip():
            errors.append("Campaign requires city/service_area")
        
        # Category is required
        if not campaign.category or not campaign.category.strip():
            errors.append("Campaign requires category")
        
        # Service is required
        if not campaign.upstkey_service or not campaign.upstkey_service.strip():
            errors.append("Campaign requires upstkey_service")
        
        if campaign.upstkey_service not in CampaignFilterValidator.VALID_SERVICES:
            errors.append(f"Unknown service: {campaign.upstkey_service}. Valid: {', '.join(CampaignFilterValidator.VALID_SERVICES)}")
        
        # Target leads must be positive
        if campaign.target_qualified_leads < 1:
            errors.append("Target qualified leads must be >= 1 (goal, not quota)")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_soft_filters(campaign: CampaignFilter) -> tuple[bool, List[str]]:
        """Validate optional soft filters"""
        warnings = []
        
        # Minimum rating validation
        if campaign.minimum_rating:
            if campaign.minimum_rating < 1.0:
                warnings.append(f"Minimum rating {campaign.minimum_rating} is very low")
            if campaign.minimum_rating > 5.0:
                warnings.append(f"Minimum rating {campaign.minimum_rating} exceeds typical 1-5 scale")
        
        # Minimum review count validation
        if campaign.minimum_review_count and campaign.minimum_review_count < 0:
            warnings.append("Minimum review count cannot be negative")
        
        # Confidence threshold validation
        if campaign.confidence_threshold:
            if campaign.confidence_threshold < 0.3:
                warnings.append("Confidence threshold < 0.3 may pass weak evidence")
            if campaign.confidence_threshold > 0.95:
                warnings.append("Confidence threshold > 0.95 may reject most leads")
        
        # Search intent validation
        valid_intents = ["local", "booking", "informational", "transactional"]
        if campaign.search_intent and campaign.search_intent not in valid_intents:
            warnings.append(f"Unknown search intent: {campaign.search_intent}. Valid: {', '.join(valid_intents)}")
        
        return True, warnings  # Soft filters don't fail validation
    
    @staticmethod
    def validate_full(campaign: CampaignFilter) -> tuple[bool, List[str], List[str]]:
        """Validate complete campaign configuration
        
        Returns: (is_valid, errors, warnings)
        """
        hard_valid, hard_errors = CampaignFilterValidator.validate_hard_filters(campaign)
        soft_valid, soft_warnings = CampaignFilterValidator.validate_soft_filters(campaign)
        
        logger.info(f"Campaign validation: valid={hard_valid}, errors={len(hard_errors)}, warnings={len(soft_warnings)}")
        
        if hard_errors:
            logger.error(f"Hard filter errors: {hard_errors}")
        
        return hard_valid, hard_errors, soft_warnings


class CampaignFilterApplier:
    """Apply campaign filters to leads - NEVER lower standards to hit target"""
    
    @staticmethod
    def apply_filters(
        lead_rating: Optional[float],
        lead_review_count: Optional[int],
        campaign: CampaignFilter
    ) -> tuple[bool, Optional[str]]:
        """
        Apply campaign filters to a lead
        
        Returns: (passes_filters, reason_if_not)
        
        Key principle: Unknown data is not the same as zero/failure
        """
        
        # Rating filter (optional hard filter)
        if campaign.minimum_rating is not None:
            if lead_rating is None:
                # Unknown rating - don't auto-reject
                logger.debug("Lead has unknown rating, allowing through (not treating as zero)")
            elif lead_rating < campaign.minimum_rating:
                return False, f"Rating {lead_rating} below minimum {campaign.minimum_rating}"
        
        # Review count filter (optional hard filter)
        if campaign.minimum_review_count is not None:
            if lead_review_count is None:
                # Unknown review count - don't auto-reject
                logger.debug("Lead has unknown review count, allowing through (not treating as zero)")
            elif lead_review_count < campaign.minimum_review_count:
                return False, f"Review count {lead_review_count} below minimum {campaign.minimum_review_count}"
        
        return True, None
    
    @staticmethod
    def check_target_not_lowering_standards(
        leads_passed: int,
        target: int,
        current_evidence_threshold: float
    ) -> tuple[bool, Optional[str]]:
        """
        Ensure we're not lowering qualification standards to hit target
        
        Per CLOREL: "Target is goal, not quota. Never lower evidence threshold to hit target."
        """
        
        if leads_passed >= target:
            return True, None
        
        gap = target - leads_passed
        logger.info(f"Lead gap: {gap} leads short of target {target}, but will NOT lower standards")
        
        # Never lower threshold
        return True, f"Gap of {gap} leads but maintaining evidence threshold at {current_evidence_threshold}"


class FilterPolicy:
    """Campaign filter policy - defines how filters should be applied"""
    
    # Default filter behavior
    HANDLE_UNKNOWN_RATING = "include"  # "include", "exclude", "hold"
    HANDLE_UNKNOWN_REVIEWS = "include"  # "include", "exclude", "hold"
    HANDLE_UNKNOWN_HOURS = "include"  # Include businesses with unknown hours
    
    # Never auto-reject based on search signals
    HIGH_SEARCH_OVERRIDES_WEAK_EVIDENCE = False
    
    # Always require human review for borderline cases
    REQUIRE_HUMAN_REVIEW_BELOW_CONFIDENCE = 0.65
    
    @staticmethod
    def get_policy(campaign: CampaignFilter) -> Dict[str, str]:
        """Get filter policy for campaign"""
        return {
            "unknown_rating": FilterPolicy.HANDLE_UNKNOWN_RATING,
            "unknown_reviews": FilterPolicy.HANDLE_UNKNOWN_REVIEWS,
            "unknown_hours": FilterPolicy.HANDLE_UNKNOWN_HOURS,
            "search_overrides_evidence": FilterPolicy.HIGH_SEARCH_OVERRIDES_WEAK_EVIDENCE,
            "require_human_review_threshold": FilterPolicy.REQUIRE_HUMAN_REVIEW_BELOW_CONFIDENCE
        }


# Type hints
from typing import Dict
