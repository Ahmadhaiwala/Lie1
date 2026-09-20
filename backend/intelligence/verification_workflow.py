"""
CLOREL Verification Workflow - LangGraph Implementation

Implements the complete verification flow:
1. Campaign Guard - Validate campaign/service configuration
2. Discover Businesses - Fetch candidate businesses
3. Normalize & Validate - Deduplicate and validate identity
4. Digital Presence Check - Verify website/booking/social
5. Business Context - Capture hours/reviews
6. Service Fit Assessment - Map evidence to service
7. Verification Gate - Apply deterministic rules
8. Persist & Present - Save results with audit trail
9. Human Review - Final approval/rejection
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum

from models.evidence import (
    Evidence, EvidenceType, FactOrAssumption, Route, VerificationResult,
    GateResult, VerificationGate, WebsiteStatus, DigitalPresenceCheck,
    CampaignFilter, AuditLog
)
from models.business import Business

logger = logging.getLogger(__name__)


class WorkflowState:
    """State object passed through LangGraph workflow"""
    def __init__(self):
        self.campaign_id: Optional[str] = None
        self.campaign: Optional[CampaignFilter] = None
        self.service: Optional[str] = None
        
        # Business data
        self.candidates: List[Business] = []
        self.current_business: Optional[Business] = None
        self.normalized_business: Optional[Business] = None
        
        # Evidence collection
        self.evidence_list: List[Evidence] = []
        self.digital_presence: Optional[DigitalPresenceCheck] = None
        
        # Verification results
        self.verification_result: Optional[VerificationResult] = None
        self.route: Optional[Route] = None
        self.route_reason: str = ""
        
        # Audit
        self.errors: List[str] = []
        self.warnings: List[str] = []


class CampaignGuard:
    """Node 1: Validate campaign and hard filters"""
    
    @staticmethod
    def validate(state: WorkflowState) -> WorkflowState:
        """Validate campaign configuration"""
        logger.info(f"Campaign Guard: Validating campaign {state.campaign_id}")
        
        if not state.campaign:
            state.errors.append("Campaign not provided")
            return state
        
        campaign = state.campaign
        
        # Hard validations
        if not campaign.city:
            state.errors.append("Campaign missing required field: city")
        
        if not campaign.category:
            state.errors.append("Campaign missing required field: category")
        
        if not campaign.upstkey_service:
            state.errors.append("Campaign missing required field: upstkey_service")
        
        # Soft validations
        if campaign.minimum_rating and campaign.minimum_rating < 1.0:
            state.warnings.append("Minimum rating < 1.0 may be too lenient")
        
        if campaign.target_qualified_leads < 1:
            state.errors.append("Target qualified leads must be > 0")
        
        if state.errors:
            logger.error(f"Campaign Guard failed: {state.errors}")
            raise ValueError(f"Campaign validation failed: {'; '.join(state.errors)}")
        
        logger.info("Campaign Guard: Validation passed")
        return state


class DiscoverBusinesses:
    """Node 2: Fetch candidate businesses from discovery provider"""
    
    @staticmethod
    def discover(state: WorkflowState, provider_mock: Optional[List[Business]] = None) -> WorkflowState:
        """Fetch candidates from discovery provider with retry logic"""
        logger.info(f"Discover: Fetching businesses for {state.campaign.city}, {state.campaign.category}")
        
        try:
            # In real implementation, call SerpAPI or Google Places
            # For now, use mock or provided data
            if provider_mock:
                state.candidates = provider_mock
            else:
                state.candidates = []  # Would call real provider here
            
            logger.info(f"Discover: Found {len(state.candidates)} candidates")
            
        except Exception as e:
            state.errors.append(f"Discovery provider error: {str(e)}")
            logger.error(f"Discover failed: {str(e)}")
            raise
        
        return state


class NormalizeValidate:
    """Node 3: Deduplicate and validate identity"""
    
    @staticmethod
    def normalize(state: WorkflowState) -> WorkflowState:
        """Deduplicate and validate business identity"""
        logger.info(f"NormalizeValidate: Processing {len(state.candidates)} candidates")
        
        validated = []
        
        for business in state.candidates:
            # Check for duplicates (simplified)
            is_duplicate = any(
                v.name.lower() == business.name.lower() and
                v.locations and business.locations and
                v.locations[0].city == business.locations[0].city
                for v in validated
            )
            
            if is_duplicate:
                logger.warning(f"Duplicate detected: {business.name}")
                continue
            
            # Validate identity fields
            if not business.name:
                state.warnings.append(f"Business missing name")
                continue
            
            if not business.locations or not business.locations[0].city:
                state.warnings.append(f"Business {business.name} missing location")
                continue
            
            # Category validation
            if state.campaign.category.lower() not in (business.industry or "").lower():
                logger.debug(f"Category mismatch: {business.industry} vs {state.campaign.category}")
                # Don't skip - let service fit assessor decide
            
            # Add identity evidence
            evidence = Evidence(
                claim=f"Business identity verified: {business.name} in {business.locations[0].city}",
                fact_vs_assumption=FactOrAssumption.FACT,
                evidence_type=EvidenceType.IDENTITY,
                source="discovery_provider",
                source_id=business.source_id,
                confidence=0.95 if business.source_id else 0.7,
                business_id=business.id
            )
            state.evidence_list.append(evidence)
            
            validated.append(business)
        
        state.candidates = validated
        logger.info(f"NormalizeValidate: {len(validated)} businesses passed validation")
        return state


class DigitalPresenceChecker:
    """Node 4: Check website and digital presence"""
    
    @staticmethod
    def check(state: WorkflowState) -> WorkflowState:
        """Check website status and alternative digital channels"""
        
        if not state.current_business:
            return state
        
        business = state.current_business
        logger.info(f"DigitalPresenceChecker: Checking {business.name}")
        
        check_result = DigitalPresenceCheck()
        
        # Check website status
        if not business.contact.website:
            check_result.website_status = WebsiteStatus.URL_MISSING
            check_result.crawl_attempted = False
            
            evidence = Evidence(
                claim="No website URL found in business listing",
                fact_vs_assumption=FactOrAssumption.FACT,
                evidence_type=EvidenceType.DIGITAL_PRESENCE,
                source="listing_validation",
                confidence=1.0,
                business_id=business.id,
                reason_for_uncertainty="URL missing from data source"
            )
            state.evidence_list.append(evidence)
            
            # Check for alternatives
            if business.contact.social_media:
                check_result.has_social = True
                evidence = Evidence(
                    claim=f"Alternative digital presence: {len(business.contact.social_media)} social profiles",
                    fact_vs_assumption=FactOrAssumption.FACT,
                    evidence_type=EvidenceType.DIGITAL_PRESENCE,
                    source="business_listing",
                    confidence=0.8,
                    business_id=business.id
                )
                state.evidence_list.append(evidence)
        else:
            check_result.website_status = WebsiteStatus.ACTIVE
            check_result.website_url = str(business.contact.website)
            check_result.crawl_attempted = True
            
            # In real implementation, would crawl here
            # For now, mark as active with confidence
            evidence = Evidence(
                claim="Website is active and accessible",
                fact_vs_assumption=FactOrAssumption.FACT,
                evidence_type=EvidenceType.DIGITAL_PRESENCE,
                source="url_validation",
                confidence=0.85,
                business_id=business.id
            )
            state.evidence_list.append(evidence)
        
        state.digital_presence = check_result
        logger.info(f"DigitalPresenceChecker: Status = {check_result.website_status}")
        return state


class BusinessContext:
    """Node 5: Capture business context (hours, reviews, rating)"""
    
    @staticmethod
    def enrich(state: WorkflowState) -> WorkflowState:
        """Add business context evidence"""
        
        if not state.current_business:
            return state
        
        business = state.current_business
        logger.info(f"BusinessContext: Enriching {business.name}")
        
        # Check rating if available
        if hasattr(business, 'rating') and business.rating:
            rating = business.rating
            confidence = 0.9 if rating >= state.campaign.minimum_rating if state.campaign.minimum_rating else True else 0.5
            
            evidence = Evidence(
                claim=f"Business has rating of {rating}",
                fact_vs_assumption=FactOrAssumption.FACT,
                evidence_type=EvidenceType.BUSINESS_CONTEXT,
                source="google_maps",
                confidence=confidence,
                business_id=business.id
            )
            state.evidence_list.append(evidence)
        
        return state


class ServiceFitAssessor:
    """Node 6: Map evidence to service fit"""
    
    @staticmethod
    def assess(state: WorkflowState) -> WorkflowState:
        """Assess whether Upstkey service fits this business"""
        
        if not state.current_business or not state.campaign:
            return state
        
        business = state.current_business
        service = state.campaign.upstkey_service
        
        logger.info(f"ServiceFitAssessor: Assessing {service} fit for {business.name}")
        
        # Simple heuristic - in real implementation would be more sophisticated
        fit_score = 0.0
        rationale = []
        
        if service == "website":
            # Website service fits if business lacks website
            if state.digital_presence and state.digital_presence.website_status == WebsiteStatus.URL_MISSING:
                fit_score = 0.85
                rationale.append("Business missing website")
            elif state.digital_presence and state.digital_presence.has_booking:
                fit_score = 0.4
                rationale.append("Already has booking/order channel")
            else:
                fit_score = 0.5
                rationale.append("Website status unclear")
        
        elif service == "booking":
            # Booking service fits if business handles transactions
            if hasattr(business, 'industry') and any(x in (business.industry or "").lower() for x in ['restaurant', 'salon', 'clinic']):
                fit_score = 0.8
                rationale.append("Industry amenable to booking")
            else:
                fit_score = 0.4
                rationale.append("Industry may not need booking")
        
        evidence = Evidence(
            claim=f"{service.title()} service fit score: {fit_score:.2f}. Rationale: {'; '.join(rationale)}",
            fact_vs_assumption=FactOrAssumption.ASSUMPTION,  # This is assessment/assumption
            evidence_type=EvidenceType.SERVICE_FIT,
            source="service_fit_assessment",
            confidence=fit_score,
            business_id=business.id
        )
        state.evidence_list.append(evidence)
        
        logger.info(f"ServiceFitAssessor: Fit score = {fit_score}")
        return state


class VerificationGateNode:
    """Node 7: Apply verification gates"""
    
    @staticmethod
    def verify(state: WorkflowState) -> WorkflowState:
        """Apply deterministic verification gates"""
        
        logger.info("VerificationGateNode: Applying gates")
        
        gate_results = []
        
        # Identity Gate
        identity_evidence = [e for e in state.evidence_list if e.evidence_type == EvidenceType.IDENTITY]
        identity_passed = len(identity_evidence) > 0 and any(e.confidence > 0.7 for e in identity_evidence)
        gate_results.append(GateResult(
            gate=VerificationGate.IDENTITY,
            passed=identity_passed,
            score=max([e.confidence for e in identity_evidence]) if identity_evidence else 0.0,
            reason="Identity validated through business listing" if identity_passed else "Identity validation failed"
        ))
        
        # Digital Gate
        digital_evidence = [e for e in state.evidence_list if e.evidence_type == EvidenceType.DIGITAL_PRESENCE]
        digital_passed = len(digital_evidence) > 0  # Passed if we checked, regardless of result
        gate_results.append(GateResult(
            gate=VerificationGate.DIGITAL,
            passed=digital_passed,
            score=max([e.confidence for e in digital_evidence]) if digital_evidence else 0.0,
            reason="Digital presence checked" if digital_passed else "Digital presence not checked"
        ))
        
        # Service Fit Gate
        service_evidence = [e for e in state.evidence_list if e.evidence_type == EvidenceType.SERVICE_FIT]
        service_passed = len(service_evidence) > 0 and any(e.confidence > 0.5 for e in service_evidence)
        gate_results.append(GateResult(
            gate=VerificationGate.SERVICE_FIT,
            passed=service_passed,
            score=max([e.confidence for e in service_evidence]) if service_evidence else 0.0,
            reason="Service fit plausible" if service_passed else "Service fit unclear"
        ))
        
        # Confidence Gate
        avg_confidence = sum(e.confidence for e in state.evidence_list) / len(state.evidence_list) if state.evidence_list else 0.0
        threshold = state.campaign.confidence_threshold or 0.6
        confidence_passed = avg_confidence >= threshold
        gate_results.append(GateResult(
            gate=VerificationGate.CONFIDENCE,
            passed=confidence_passed,
            score=avg_confidence,
            reason=f"Average confidence {avg_confidence:.2f} {'exceeds' if confidence_passed else 'below'} threshold {threshold}"
        ))
        
        # Determine route based on gates
        all_passed = all(g.passed for g in gate_results)
        
        if all_passed:
            state.route = Route.SALES_REVIEW
            state.route_reason = "All verification gates passed - ready for sales review"
        elif identity_passed and digital_passed:
            state.route = Route.FUTURE_OPPORTUNITY
            state.route_reason = "Identity and digital verified but service fit unclear"
        elif not confidence_passed:
            state.route = Route.HOLD_UNCERTAIN
            state.route_reason = f"Confidence too low ({avg_confidence:.2f}). Needs follow-up."
        else:
            state.route = Route.HOLD_UNCERTAIN
            state.route_reason = "Insufficient evidence. Gates not passed."
        
        # Build verification result
        state.verification_result = VerificationResult(
            route=state.route,
            routing_reason=state.route_reason,
            gate_results=gate_results,
            all_evidence=state.evidence_list,
            evidence_count=len(state.evidence_list),
            overall_confidence=avg_confidence
        )
        
        logger.info(f"VerificationGateNode: Route = {state.route}, Confidence = {avg_confidence:.2f}")
        return state


class PersistAndPresent:
    """Node 8: Save results with audit trail"""
    
    @staticmethod
    def persist(state: WorkflowState) -> WorkflowState:
        """Save verification results and create audit log"""
        
        logger.info(f"PersistAndPresent: Saving verification result, route={state.route}")
        
        if not state.verification_result or not state.current_business:
            state.errors.append("Missing verification result or business")
            return state
        
        # In real implementation, would save to database here
        # For now, just log
        state.verification_result.lead_id = state.current_business.id
        state.verification_result.campaign_id = state.campaign_id
        
        # Create audit log
        audit = AuditLog(
            lead_id=state.current_business.id,
            campaign_id=state.campaign_id,
            action="verified",
            actor="clorel_system",
            details={
                "route": state.route.value,
                "reason": state.route_reason,
                "evidence_count": len(state.evidence_list),
                "confidence": state.verification_result.overall_confidence
            }
        )
        
        logger.info(f"PersistAndPresent: Audit log created for {state.current_business.name}")
        return state


class HumanReview:
    """Node 9: Human reviewer approval/rejection"""
    
    @staticmethod
    def review(state: WorkflowState, reviewer_id: str, decision: str, notes: Optional[str] = None) -> WorkflowState:
        """Record human reviewer decision"""
        
        logger.info(f"HumanReview: {reviewer_id} reviewing lead {state.current_business.id if state.current_business else 'unknown'}")
        
        if not state.verification_result:
            state.errors.append("No verification result to review")
            return state
        
        # Record review
        state.verification_result.reviewed_by = reviewer_id
        state.verification_result.review_decision = decision
        state.verification_result.review_timestamp = datetime.utcnow()
        state.verification_result.review_notes = notes
        
        # Create audit log for review
        audit = AuditLog(
            lead_id=state.current_business.id if state.current_business else "",
            campaign_id=state.campaign_id,
            action="reviewed",
            actor=reviewer_id,
            details={
                "previous_route": state.route.value if state.route else None,
                "decision": decision,
                "notes": notes
            }
        )
        
        logger.info(f"HumanReview: Decision recorded - {decision}")
        return state


# Workflow orchestration helpers
def create_workflow_state() -> WorkflowState:
    """Create initial workflow state"""
    return WorkflowState()


def run_verification_workflow(
    campaign: CampaignFilter,
    candidates: List[Business],
    reviewer_id: Optional[str] = None
) -> List[VerificationResult]:
    """Run complete verification workflow for campaign"""
    
    results = []
    
    for business in candidates:
        state = create_workflow_state()
        state.campaign = campaign
        state.campaign_id = campaign.campaign_id
        state.current_business = business
        
        try:
            # Run through workflow nodes
            CampaignGuard.validate(state)
            DigitalPresenceChecker.check(state)
            BusinessContext.enrich(state)
            ServiceFitAssessor.assess(state)
            VerificationGateNode.verify(state)
            PersistAndPresent.persist(state)
            
            if reviewer_id:
                HumanReview.review(state, reviewer_id, "pending")
            
            results.append(state.verification_result)
            
        except Exception as e:
            logger.error(f"Workflow failed for {business.name}: {str(e)}")
            continue
    
    return results
