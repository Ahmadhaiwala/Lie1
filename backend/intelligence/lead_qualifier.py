"""
lead_qualifier.py
-----------------
Converts an Opportunity + business metadata into a rich, context-aware Lead.

Input  : Opportunity + business info dict
Output : Lead dataclass

README reference: Section 8 — Lead Qualification
  A lead should contain research context, not just (Business + email).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .opportunity_engine import Opportunity


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

class QualificationTier(str, Enum):
    """How strong/promising this lead is."""
    HOT  = "hot"   # confidence >= 0.75
    WARM = "warm"  # confidence >= 0.5
    COLD = "cold"  # confidence <  0.5


@dataclass
class BusinessInfo:
    name: str
    website: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None


@dataclass
class Lead:
    """A fully qualified sales lead with research context."""
    business: BusinessInfo
    opportunity: Opportunity
    tier: QualificationTier
    summary: str                         # 1-sentence human-readable summary
    action_items: List[str] = field(default_factory=list)
    disqualified: bool = False
    disqualification_reason: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "business": {
                "name": self.business.name,
                "website": self.business.website,
                "phone": self.business.phone,
                "email": self.business.email,
                "address": self.business.address,
                "category": self.business.category,
            },
            "opportunity": self.opportunity.to_dict(),
            "tier": self.tier.value,
            "summary": self.summary,
            "action_items": self.action_items,
            "disqualified": self.disqualified,
            "disqualification_reason": self.disqualification_reason,
        }


# ---------------------------------------------------------------------------
# Qualifier
# ---------------------------------------------------------------------------

class LeadQualifier:
    """
    Qualifies an Opportunity into a Lead with tier, summary, and action items.

    Usage
    -----
    >>> qualifier = LeadQualifier()
    >>> lead = qualifier.qualify(
    ...     opportunity=opportunity,
    ...     business_info=business_info,
    ... )
    """

    # Confidence thresholds for tier assignment
    HOT_THRESHOLD  = 0.75
    WARM_THRESHOLD = 0.50

    def qualify(
        self,
        opportunity: Opportunity,
        business_info: Optional[BusinessInfo] = None,
    ) -> Lead:
        """
        Convert an Opportunity into a qualified Lead.

        Parameters
        ----------
        opportunity : Opportunity
            Detected opportunity from OpportunityEngine.
        business_info : BusinessInfo, optional
            Additional contact/metadata for the business.

        Returns
        -------
        Lead
        """
        if business_info is None:
            business_info = BusinessInfo(
                name=opportunity.business_name,
                website=opportunity.business_website,
            )

        tier = self._assign_tier(opportunity.confidence)
        summary = self._build_summary(opportunity, tier)
        action_items = self._recommended_actions(opportunity, tier)

        # Disqualify if too many blocking signals
        blocking_count = len(opportunity.blocking_evidence)
        disqualified = blocking_count >= 3
        disq_reason = (
            f"Too many negative signals ({blocking_count}) — "
            "business likely already has the solution."
        ) if disqualified else None

        return Lead(
            business=business_info,
            opportunity=opportunity,
            tier=tier,
            summary=summary,
            action_items=action_items,
            disqualified=disqualified,
            disqualification_reason=disq_reason,
        )

    def qualify_batch(
        self,
        opportunities: List[Opportunity],
        business_lookup: Optional[dict] = None,
    ) -> List[Lead]:
        """
        Qualify multiple opportunities into leads.

        Parameters
        ----------
        opportunities : List[Opportunity]
        business_lookup : dict, optional
            Maps business_website → BusinessInfo for enrichment.

        Returns
        -------
        List[Lead]
            Sorted from highest to lowest confidence, disqualified leads last.
        """
        business_lookup = business_lookup or {}
        leads: List[Lead] = []

        for opp in opportunities:
            biz_info = business_lookup.get(opp.business_website)
            lead = self.qualify(opp, biz_info)
            leads.append(lead)

        # Sort: active leads first, then by confidence descending
        leads.sort(key=lambda l: (l.disqualified, -l.opportunity.confidence))
        return leads

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _assign_tier(self, confidence: float) -> QualificationTier:
        if confidence >= self.HOT_THRESHOLD:
            return QualificationTier.HOT
        if confidence >= self.WARM_THRESHOLD:
            return QualificationTier.WARM
        return QualificationTier.COLD

    def _build_summary(self, opp: Opportunity, tier: QualificationTier) -> str:
        tier_label = {
            QualificationTier.HOT: "🔥 HOT LEAD",
            QualificationTier.WARM: "♨️  WARM LEAD",
            QualificationTier.COLD: "❄️  COLD LEAD",
        }[tier]

        return (
            f"{tier_label} — {opp.business_name} appears to need "
            f"'{opp.service}'. Confidence: {opp.confidence:.0%}. "
            f"{opp.reason}"
        )

    def _recommended_actions(
        self, opp: Opportunity, tier: QualificationTier
    ) -> List[str]:
        """Return a list of suggested next steps for the sales rep."""
        actions: List[str] = []

        if tier == QualificationTier.HOT:
            actions.append("Prioritize for immediate outreach")
            actions.append("Draft personalized message referencing evidence")
        elif tier == QualificationTier.WARM:
            actions.append("Schedule outreach within 48 hours")
            actions.append("Review evidence before contacting")
        else:
            actions.append("Monitor — revisit if signals strengthen")

        if opp.blocking_evidence:
            actions.append(
                f"Verify {len(opp.blocking_evidence)} negative signal(s) "
                "before contacting — solution may already exist"
            )

        actions.append(f"Visit {opp.business_website} to verify research manually")
        return actions
