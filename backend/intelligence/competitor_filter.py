"""
competitor_filter.py
--------------------
Strict B2B competitor detection and filtering.

Core Rule: Only recommend businesses that are POTENTIAL CUSTOMERS, not competitors.

A business is a COMPETITOR if it:
  - Sells the same or similar service
  - Provides the requested solution to other customers
  - Advertises or develops the service being offered

Examples:
  Target: website → Web agency = REJECT
  Target: seo → SEO agency = REJECT
  Target: whatsapp_bot → WhatsApp automation company = REJECT

Key Principle: "needs the service" ≠ "sells the service"
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class CompetitorAnalysis:
    """Result of competitor filtering analysis."""
    is_competitor: bool
    confidence: float  # 0.0 - 1.0
    rejection_reason: str = ""
    evidence: List[str] = None
    
    def __post_init__(self):
        if self.evidence is None:
            self.evidence = []
    
    def to_dict(self) -> dict:
        return {
            "is_competitor": self.is_competitor,
            "confidence": self.confidence,
            "rejection_reason": self.rejection_reason,
            "evidence": self.evidence,
        }


# ---------------------------------------------------------------------------
# Competitor Filter
# ---------------------------------------------------------------------------

class CompetitorFilter:
    """
    Detects and rejects competitor businesses.
    
    A business is a competitor if it SELLS/PROVIDES the service being offered,
    not just USES it.
    
    Usage:
        filter = CompetitorFilter()
        result = filter.analyze(
            business_data=business_data,
            target_service="website",
        )
        
        if result.is_competitor:
            # REJECT this lead
            pass
    """
    
    # Service-specific competitor patterns
    COMPETITOR_PATTERNS = {
        "website": {
            "business_types": [
                "web development", "web design", "website design",
                "web agency", "digital agency", "web studio",
                "web developer", "web designer", "website developer",
                "website builder", "web solutions", "web services",
                "software development", "software agency",
                "IT services", "IT company", "tech company",
                "freelance web", "wordpress developer", "wix designer",
            ],
            "keywords": [
                "we build websites", "we create websites", "we design websites",
                "website development services", "website design services",
                "web development company", "web design company",
                "custom website", "responsive website", "website packages",
                "portfolio", "our clients", "case studies",
                "web solutions for", "websites for businesses",
            ],
            "domain_patterns": [
                r"web.*dev", r"web.*design", r"web.*studio", r"web.*agency",
                r"digital.*agency", r"design.*studio", r"creative.*agency",
                r".*solutions", r".*tech", r".*soft",
            ],
        },
        "seo": {
            "business_types": [
                "seo agency", "seo company", "seo services",
                "digital marketing", "marketing agency", "marketing company",
                "seo consultant", "seo expert", "seo specialist",
                "search marketing", "online marketing",
                "internet marketing", "growth marketing",
            ],
            "keywords": [
                "seo services", "search engine optimization services",
                "we do seo", "seo packages", "seo pricing",
                "rank higher", "page 1 guarantee", "seo audit",
                "keyword research services", "link building services",
                "our seo clients", "seo case studies",
                "digital marketing services", "marketing solutions",
            ],
            "domain_patterns": [
                r"seo.*", r".*seo", r".*marketing", r"marketing.*",
                r"digital.*agency", r"growth.*", r"optimize.*",
            ],
        },
        "whatsapp_bot": {
            "business_types": [
                "whatsapp automation", "chatbot development",
                "whatsapp bot", "chatbot agency", "bot development",
                "whatsapp api", "messaging automation",
                "conversational ai", "ai chatbot",
                "automation agency", "automation services",
            ],
            "keywords": [
                "whatsapp bot services", "whatsapp automation services",
                "we build chatbots", "chatbot solutions",
                "whatsapp business api", "chatbot development",
                "automation services", "bot development services",
                "messaging solutions", "conversational ai solutions",
            ],
            "domain_patterns": [
                r".*bot.*", r".*chat.*", r"automation.*", r".*automation",
                r"whatsapp.*", r".*ai", r"ai.*",
            ],
        },
        "ai_automation": {
            "business_types": [
                "ai automation", "ai agency", "ai consulting",
                "automation agency", "automation company",
                "ai solutions", "ai services", "ai integration",
                "rpa", "robotic process automation",
                "workflow automation", "business automation",
            ],
            "keywords": [
                "ai automation services", "automation services",
                "we automate", "automation solutions",
                "ai consulting", "ai implementation",
                "workflow automation services", "business process automation",
                "ai integration services", "automation consulting",
            ],
            "domain_patterns": [
                r".*ai.*", r"ai.*", r"automation.*", r".*automation",
                r".*automate", r"workflow.*", r".*rpa",
            ],
        },
    }
    
    # Generic competitor indicators (apply to all services)
    GENERIC_COMPETITOR_INDICATORS = [
        "agency", "consulting", "consultant", "services",
        "solutions", "development", "developer",
        "we build", "we create", "we design", "we develop",
        "we help businesses", "we help companies",
        "our clients", "our portfolio", "case studies",
        "packages", "pricing", "get a quote",
        "hire us", "contact us for", "book a consultation",
        "free consultation", "free quote",
    ]
    
    def __init__(self, llm_client=None):
        """
        Initialize competitor filter.
        
        Args:
            llm_client: Optional LLM for advanced analysis
        """
        self.llm = llm_client
    
    def analyze(
        self,
        business_data: dict,
        target_service: str,
    ) -> CompetitorAnalysis:
        """
        Analyze if a business is a competitor.
        
        Args:
            business_data: Business information including name, industry, website, etc.
            target_service: Service being offered (website, seo, whatsapp_bot, etc.)
        
        Returns:
            CompetitorAnalysis with is_competitor flag and evidence
        """
        evidence = []
        confidence = 0.0
        
        # Normalize service name (handle both "whatsapp_bot" and "whatsapp bot")
        service = target_service.lower().replace("_", " ").replace("-", " ").strip()
        service_key = target_service.lower().replace(" ", "_").replace("-", "_").strip()
        
        # Get service-specific patterns
        patterns = self.COMPETITOR_PATTERNS.get(service_key, {})
        
        if not patterns:
            logger.warning(f"No competitor patterns defined for service: {service}")
            # Use generic detection only
            patterns = {
                "business_types": [],
                "keywords": [],
                "domain_patterns": [],
            }
        
        # Collect all text to analyze
        business_name = business_data.get("business_name", "").lower()
        industry = business_data.get("industry", "").lower()
        raw_snippet = business_data.get("raw_snippet", "").lower()
        website = (business_data.get("website") or "").lower()
        source_url = (business_data.get("source_url") or "").lower()
        pain_points = " ".join(business_data.get("pain_points", [])).lower()
        
        combined_text = f"{business_name} {industry} {raw_snippet} {pain_points}"
        
        # Check 1: Business type match
        for biz_type in patterns.get("business_types", []):
            if biz_type in industry or biz_type in business_name:
                evidence.append(f"Business type matches competitor pattern: '{biz_type}'")
                confidence += 0.3
        
        # Check 2: Keyword match in content
        keyword_matches = 0
        for keyword in patterns.get("keywords", []):
            if keyword in combined_text:
                evidence.append(f"Competitor keyword found: '{keyword}'")
                keyword_matches += 1
                confidence += 0.15
        
        # Cap keyword contribution
        if keyword_matches > 0:
            confidence = min(confidence, 0.8)
        
        # Check 3: Domain pattern match
        all_urls = f"{website} {source_url}"
        for pattern_str in patterns.get("domain_patterns", []):
            pattern = re.compile(pattern_str, re.IGNORECASE)
            if pattern.search(all_urls):
                evidence.append(f"URL matches competitor pattern: '{pattern_str}'")
                confidence += 0.2
        
        # Check 4: Generic competitor indicators
        generic_count = 0
        for indicator in self.GENERIC_COMPETITOR_INDICATORS[:10]:  # Limit to avoid over-matching
            if indicator in combined_text:
                generic_count += 1
        
        if generic_count >= 3:
            evidence.append(f"Multiple generic competitor indicators found: {generic_count}")
            confidence += 0.25
        
        # Check 5: Service name in business context
        # e.g., "SEO" in business name when target is SEO
        service_keywords = service.split()
        service_in_name = any(kw in business_name for kw in service_keywords if len(kw) > 2)
        service_in_industry = any(kw in industry for kw in service_keywords if len(kw) > 2)
        
        if service_in_name and generic_count >= 2:
            evidence.append(f"Service '{service}' appears in business name with service indicators")
            confidence += 0.30
        
        if service_in_industry and any(ind in industry for ind in ["agency", "consultant", "consulting"]):
            evidence.append(f"Service '{service}' in industry with service provider indicators")
            confidence += 0.30
        
        # Clamp confidence
        confidence = min(confidence, 1.0)
        
        # Determine if competitor
        COMPETITOR_THRESHOLD = 0.5
        is_competitor = confidence >= COMPETITOR_THRESHOLD
        
        # Build rejection reason
        rejection_reason = ""
        if is_competitor:
            if evidence:
                top_evidence = evidence[0]
                rejection_reason = f"Competitor detected: {top_evidence}"
            else:
                rejection_reason = "Business appears to provide the same service"
        
        return CompetitorAnalysis(
            is_competitor=is_competitor,
            confidence=round(confidence, 2),
            rejection_reason=rejection_reason,
            evidence=evidence,
        )
    
    async def analyze_with_llm(
        self,
        business_data: dict,
        target_service: str,
    ) -> CompetitorAnalysis:
        """
        Analyze using LLM for more accurate detection.
        
        Falls back to rule-based analysis if LLM unavailable.
        """
        if not self.llm:
            return self.analyze(business_data, target_service)
        
        # Get rule-based analysis first
        rule_based = self.analyze(business_data, target_service)
        
        # If rule-based is very confident, skip LLM
        if rule_based.confidence >= 0.8:
            return rule_based
        
        # Build LLM prompt
        system_prompt = """You are a strict B2B lead filter.

Your ONLY job is to determine: Is this business a COMPETITOR or a POTENTIAL CUSTOMER?

A business is a COMPETITOR if it SELLS/PROVIDES the target service to other customers.
A business is a POTENTIAL CUSTOMER if it NEEDS/USES the service for itself.

Examples:
- Target: website → Web development agency = COMPETITOR
- Target: website → Local restaurant with no website = CUSTOMER
- Target: SEO → SEO agency = COMPETITOR  
- Target: SEO → Dentist with poor search ranking = CUSTOMER

Return JSON:
{
  "is_competitor": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}"""
        
        user_prompt = f"""Target service: {target_service}

Business information:
- Name: {business_data.get('business_name', 'Unknown')}
- Industry: {business_data.get('industry', 'Unknown')}
- Website: {business_data.get('website', 'None')}
- Description: {business_data.get('raw_snippet', 'N/A')[:500]}

Is this business a competitor or potential customer?"""
        
        try:
            import json
            response = await self.llm.complete(
                prompt=user_prompt,
                system_prompt=system_prompt,
                json_mode=True,
                max_tokens=256,
            )
            
            result = json.loads(response)
            
            # Combine with rule-based analysis
            llm_is_competitor = result.get("is_competitor", False)
            llm_confidence = float(result.get("confidence", 0.0))
            llm_reasoning = result.get("reasoning", "")
            
            # If both agree, use higher confidence
            if llm_is_competitor == rule_based.is_competitor:
                final_confidence = max(llm_confidence, rule_based.confidence)
                evidence = rule_based.evidence + [f"LLM analysis: {llm_reasoning}"]
            else:
                # Disagreement - use LLM if more confident
                if llm_confidence > rule_based.confidence:
                    final_confidence = llm_confidence
                    evidence = [f"LLM analysis: {llm_reasoning}"] + rule_based.evidence
                    llm_is_competitor = llm_is_competitor
                else:
                    final_confidence = rule_based.confidence
                    evidence = rule_based.evidence
                    llm_is_competitor = rule_based.is_competitor
            
            return CompetitorAnalysis(
                is_competitor=llm_is_competitor,
                confidence=round(final_confidence, 2),
                rejection_reason=f"Competitor: {llm_reasoning}" if llm_is_competitor else "",
                evidence=evidence,
            )
            
        except Exception as exc:
            logger.warning(f"LLM competitor analysis failed: {exc}")
            return rule_based
    
    def batch_analyze(
        self,
        businesses: List[dict],
        target_service: str,
    ) -> List[CompetitorAnalysis]:
        """
        Analyze multiple businesses for competitor status.
        
        Returns:
            List of CompetitorAnalysis results
        """
        results = []
        for business in businesses:
            result = self.analyze(business, target_service)
            results.append(result)
        return results
    
    def filter_competitors(
        self,
        businesses: List[dict],
        target_service: str,
    ) -> tuple[List[dict], List[dict]]:
        """
        Filter out competitors from a list of businesses.
        
        Returns:
            (non_competitors, competitors) tuple
        """
        non_competitors = []
        competitors = []
        
        for business in businesses:
            analysis = self.analyze(business, target_service)
            
            if analysis.is_competitor:
                # Add competitor analysis to business data
                business["competitor_analysis"] = analysis.to_dict()
                competitors.append(business)
            else:
                non_competitors.append(business)
        
        logger.info(
            f"Filtered {len(businesses)} businesses: "
            f"{len(non_competitors)} customers, {len(competitors)} competitors"
        )
        
        return non_competitors, competitors


# ---------------------------------------------------------------------------
# Quick Validation Functions
# ---------------------------------------------------------------------------

def is_competitor(business_data: dict, target_service: str) -> bool:
    """
    Quick check if business is a competitor.
    
    Args:
        business_data: Business information
        target_service: Service being offered
    
    Returns:
        True if competitor, False if potential customer
    """
    filter = CompetitorFilter()
    result = filter.analyze(business_data, target_service)
    return result.is_competitor


def filter_out_competitors(businesses: List[dict], target_service: str) -> List[dict]:
    """
    Remove competitors from business list.
    
    Args:
        businesses: List of business data dicts
        target_service: Service being offered
    
    Returns:
        List of non-competitor businesses only
    """
    filter = CompetitorFilter()
    non_competitors, _ = filter.filter_competitors(businesses, target_service)
    return non_competitors
