"""
opportunity_engine.py
---------------------
Combines evidence + service profile signals to detect sales opportunities.

Input  : List[Evidence] + ResearchPlan
Output : Optional[Opportunity]

README reference: Section 7 — Opportunity Detection
  Business Information + Website Evidence + Service Profile + Research Signals
  → Potential Opportunity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .evidence_extractor import Evidence
from .research_planner import ResearchPlan


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Opportunity:
    """A detected sales opportunity for a specific business."""
    business_name: str
    business_website: str
    service: str                    # e.g. "online_booking_system"
    reason: str                     # human-readable explanation
    confidence: float               # 0.0 – 1.0
    supporting_evidence: List[Evidence] = field(default_factory=list)
    blocking_evidence: List[Evidence] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "business_name": self.business_name,
            "business_website": self.business_website,
            "potential_opportunity": self.service,
            "reason": self.reason,
            "confidence": self.confidence,
            "supporting_evidence": [e.to_dict() for e in self.supporting_evidence],
            "blocking_evidence": [e.to_dict() for e in self.blocking_evidence],
        }


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class OpportunityEngine:
    """
    Scores evidence to determine whether a business is a good sales target.

    Scoring logic
    -------------
    +0.3 per positive signal found (business has the problem / need)
    -0.4 per negative signal found (business already has the solution)
    Clamped to [0.0, 1.0]

    Usage
    -----
    >>> engine = OpportunityEngine()
    >>> opportunity = engine.detect(
    ...     business_name="ABC Gym",
    ...     business_website="https://example.com",
    ...     evidence_list=evidence_list,
    ...     plan=research_plan,
    ... )
    """

    # Minimum confidence required to surface an opportunity
    CONFIDENCE_THRESHOLD: float = 0.4

    def detect(
        self,
        business_name: str,
        business_website: str,
        evidence_list: List[Evidence],
        plan: ResearchPlan,
    ) -> Optional[Opportunity]:
        """
        Detect a sales opportunity from evidence.

        Parameters
        ----------
        business_name : str
        business_website : str
        evidence_list : List[Evidence]
            All evidence extracted from the business's website.
        plan : ResearchPlan
            The research plan used during crawling.

        Returns
        -------
        Optional[Opportunity]
            None if confidence is below CONFIDENCE_THRESHOLD.
        """
        positive = [e for e in evidence_list if e.signal_type == "positive"]
        negative = [e for e in evidence_list if e.signal_type == "negative"]

        confidence = self._score(positive, negative)

        if confidence < self.CONFIDENCE_THRESHOLD:
            return None

        reason = self._build_reason(positive, negative, plan.target_service)

        return Opportunity(
            business_name=business_name,
            business_website=business_website,
            service=plan.target_service,
            reason=reason,
            confidence=round(confidence, 2),
            supporting_evidence=positive,
            blocking_evidence=negative,
        )

    def detect_batch(
        self,
        businesses: List[dict],
        plan: ResearchPlan,
    ) -> List[Opportunity]:
        """
        Detect opportunities for multiple businesses.

        Parameters
        ----------
        businesses : List[dict]
            Each dict must have:
              - 'name' (str)
              - 'website' (str)
              - 'evidence' (List[Evidence])

        Returns
        -------
        List[Opportunity]
            Only businesses that meet the confidence threshold.
        """
        opportunities: List[Opportunity] = []
        for biz in businesses:
            opp = self.detect(
                business_name=biz.get("name", ""),
                business_website=biz.get("website", ""),
                evidence_list=biz.get("evidence", []),
                plan=plan,
            )
            if opp:
                opportunities.append(opp)
        return opportunities

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _score(
        self,
        positive: List[Evidence],
        negative: List[Evidence],
    ) -> float:
        """
        Compute opportunity confidence score.

        Positive signals raise the score; negative signals lower it.
        """
        score = 0.5  # neutral baseline

        # Positive signals: business NEEDS the solution
        positive_boost = min(len(positive) * 0.15, 0.4)
        score += positive_boost

        # Negative signals: business ALREADY has the solution
        negative_penalty = len(negative) * 0.3
        score -= negative_penalty

        return max(0.0, min(score, 1.0))

    def _build_reason(
        self,
        positive: List[Evidence],
        negative: List[Evidence],
        service: str,
    ) -> str:
        """Build a human-readable reason string."""
        if not positive:
            return f"No strong signals found for {service}."

        findings = [e.finding for e in positive[:3]]  # top 3 findings
        reason = f"Opportunity detected for '{service}': " + "; ".join(findings)

        if negative:
            reason += f" (Note: {len(negative)} potential blocking signal(s) also found)"

        return reason
