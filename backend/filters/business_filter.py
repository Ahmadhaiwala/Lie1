"""
filters/business_filter.py
--------------------------
Core LLM-powered business filter.

Evaluates every scraped lead on TWO axes:

  1. Online Presence Quality
     Does the business have a modern, functional digital footprint?
     Looks at: website quality, social media, SEO signals, contact methods.

  2. Business Model Suitability
     Would this business meaningfully benefit from our services
     (website dev / WhatsApp bot / SEO)?
     Filters OUT: traditional food stalls, cash-only vendors, purely physical
     micro-businesses with no digital upside.

Output — FilterPriority:
  HIGH     → Clear need + clear benefit + reachable → pursue immediately
  MEDIUM   → Potential need but uncertain fit or limited signals → worth a try
  DISCARD  → No digital need / wrong business type / unreachable

Each result includes:
  - priority          : HIGH | MEDIUM | DISCARD
  - online_score      : 0–10  (online presence quality)
  - suitability_score : 0–10  (how much they'd benefit from digital services)
  - justification     : 1-sentence decision rationale (shown in UI)
  - reasoning         : full paragraph breakdown (shown on expand)
  - recommended_services : list of services that would help this specific biz
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from llm.llm_client import LLMClient
from llm.llm_config import LLMConfig
from filters.filter_rules import rule_based_discard

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums & Data classes
# ---------------------------------------------------------------------------

class FilterPriority(str, Enum):
    HIGH    = "high"
    MEDIUM  = "medium"
    DISCARD = "discard"


@dataclass
class FilterResult:
    """Result of evaluating one business through the filter."""
    priority:             FilterPriority
    online_score:         float          # 0–10: quality of current online presence
    suitability_score:    float          # 0–10: how much digital services would help
    justification:        str            # short 1-sentence shown in UI card
    reasoning:            str            # full paragraph for expanded view
    recommended_services: List[str]      # e.g. ["website", "seo"]
    rule_discarded:       bool = False   # True if rejected by rule engine (no LLM used)

    def to_dict(self) -> dict:
        return {
            "priority":             self.priority,
            "online_score":         self.online_score,
            "suitability_score":    self.suitability_score,
            "justification":        self.justification,
            "reasoning":            self.reasoning,
            "recommended_services": self.recommended_services,
            "rule_discarded":       self.rule_discarded,
        }


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

FILTER_SYSTEM_PROMPT = """You are a senior business development analyst at a digital services agency.

Your task is to evaluate scraped business data and decide:
1. How good or bad is this business's current online presence? (score 0-10)
2. How much would this business benefit from digital services like SEO, a professional
   website, or a WhatsApp chatbot? (score 0-10)
3. What is the final priority classification?

PRIORITY RULES:
  HIGH    → online_score <= 5  AND  suitability_score >= 7
            Clear deficiency in digital presence + clear benefit from services.
            Examples: clinic with no website, restaurant with only a FB page,
            law firm on page 5 of Google.

  MEDIUM  → online_score 4-7  OR  suitability_score 5-7
            Some digital presence but room to improve, OR uncertain fit.
            Examples: business with a basic website but no SEO, startup
            with a site but no lead capture.

  DISCARD → business does NOT need digital services, OR the content is spam/
            junk / unrelated, OR it's a traditional offline micro-business
            (street food stall, roadside vendor, daily-wage labour, etc.) that
            has no meaningful digital upside.
            Examples: chai stall, thela/rehri vendor, shoe cobbler, subsistence farm.

ONLINE PRESENCE scoring guide:
  0-2  : No web presence at all (social media only or nothing)
  3-4  : Has website but very outdated / broken / no mobile support
  5-6  : Basic functional website, poor SEO, weak social
  7-8  : Decent website, some SEO, active social
  9-10 : Strong online presence, good rankings, active across channels

SUITABILITY scoring guide:
  0-3  : No digital upside (offline-only business model)
  4-6  : Could benefit moderately
  7-10 : Strong candidate — digital services would directly drive revenue

Return ONLY valid JSON — no markdown, no explanation outside the JSON:
{
  "online_score": <float 0-10>,
  "suitability_score": <float 0-10>,
  "priority": "high" | "medium" | "discard",
  "justification": "<one clear sentence explaining the decision>",
  "reasoning": "<2-3 sentences: what signals you saw, why you chose this priority>",
  "recommended_services": ["website" | "seo" | "whatsapp_bot"]
}"""


def _build_filter_prompt(
    business_name: str,
    service_needed: str,
    pain_points: List[str],
    content: str,
    source_url: str,
    website: Optional[str],
    qualification_score: float,
) -> str:
    pain_str = ", ".join(pain_points[:5]) if pain_points else "none identified"
    return f"""Evaluate this scraped business for digital service potential:

BUSINESS NAME   : {business_name}
SOURCE URL      : {source_url}
DETECTED WEBSITE: {website or "none found"}
SERVICE FLAGGED : {service_needed.replace("_", " ")}
PAIN POINTS     : {pain_str}
QUALIFICATION   : {qualification_score:.2f} / 1.0

SCRAPED CONTENT (first 4000 chars):
{content[:4000]}

Evaluate the online presence quality AND business model suitability.
Return ONLY valid JSON as specified."""


# ---------------------------------------------------------------------------
# Main Filter Class
# ---------------------------------------------------------------------------

class BusinessFilter:
    """
    Evaluates a batch of leads through two stages:

    Stage 1 – Rule engine  (fast, no LLM)
        Instantly discards obvious non-candidates (food stalls, cash-only, etc.)

    Stage 2 – LLM evaluation  (for everything that passes Stage 1)
        Deep analysis of online presence + business model suitability.
        Returns FilterPriority + detailed justification.

    Usage
    -----
    filter = BusinessFilter()
    results = await filter.evaluate_batch(leads)
    # returns dict: lead_id → FilterResult
    """

    # Score thresholds for LLM-assigned priority override
    # (these are fallbacks if LLM returns an ambiguous priority)
    HIGH_SUITABILITY_MIN    = 7.0
    HIGH_ONLINE_MAX         = 5.0
    MEDIUM_SUITABILITY_MIN  = 5.0

    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm or LLMClient(LLMConfig.from_env())

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def evaluate(
        self,
        business_name: str,
        service_needed: str,
        pain_points: List[str],
        content: str,
        source_url: str,
        website: Optional[str] = None,
        qualification_score: float = 0.5,
        industry: str = "",
    ) -> FilterResult:
        """
        Evaluate a single business.

        Returns FilterResult with priority, scores, and justification.
        """

        # ── Stage 1: Rule-based fast discard ─────────────────────────────
        should_discard, discard_reason = rule_based_discard(
            business_name, content, industry
        )
        if should_discard:
            logger.info("[FILTER] Rule-discard: %s — %s", business_name, discard_reason)
            return FilterResult(
                priority             = FilterPriority.DISCARD,
                online_score         = 0.0,
                suitability_score    = 0.0,
                justification        = discard_reason,
                reasoning            = (
                    f"Automatically discarded by rule engine. {discard_reason} "
                    "No LLM evaluation needed."
                ),
                recommended_services = [],
                rule_discarded       = True,
            )

        # ── Stage 2: LLM deep evaluation ─────────────────────────────────
        prompt = _build_filter_prompt(
            business_name, service_needed, pain_points,
            content, source_url, website, qualification_score,
        )

        try:
            raw = await self.llm.complete(
                prompt=prompt,
                system_prompt=FILTER_SYSTEM_PROMPT,
                json_mode=True,
                max_tokens=512,
                temperature=0.3,   # low temp — we want consistent decisions
            )
            data = json.loads(raw)
        except Exception as exc:
            logger.warning("[FILTER] LLM error for %s: %s — defaulting to MEDIUM", business_name, exc)
            # Graceful degradation: return MEDIUM so lead isn't lost
            return FilterResult(
                priority             = FilterPriority.MEDIUM,
                online_score         = 5.0,
                suitability_score    = 5.0,
                justification        = "Filter evaluation unavailable — defaulted to Medium Priority.",
                reasoning            = f"LLM evaluation failed: {exc}",
                recommended_services = [service_needed],
                rule_discarded       = False,
            )

        # Parse LLM response
        online_score      = float(data.get("online_score",      5.0))
        suitability_score = float(data.get("suitability_score", 5.0))
        raw_priority      = str(data.get("priority", "medium")).lower().strip()
        justification     = str(data.get("justification", ""))
        reasoning         = str(data.get("reasoning", ""))
        rec_services      = data.get("recommended_services", [service_needed])

        # Map string → enum (with sanity fallback)
        priority_map = {
            "high":    FilterPriority.HIGH,
            "medium":  FilterPriority.MEDIUM,
            "discard": FilterPriority.DISCARD,
        }
        priority = priority_map.get(raw_priority, FilterPriority.MEDIUM)

        # Override LLM priority with score-based rules if they conflict strongly
        if priority != FilterPriority.DISCARD:
            if (suitability_score >= self.HIGH_SUITABILITY_MIN and
                    online_score <= self.HIGH_ONLINE_MAX):
                priority = FilterPriority.HIGH
            elif suitability_score < self.MEDIUM_SUITABILITY_MIN:
                priority = FilterPriority.DISCARD

        logger.info(
            "[FILTER] %s → %s (online=%.1f, suit=%.1f)",
            business_name, priority.value, online_score, suitability_score,
        )

        return FilterResult(
            priority             = priority,
            online_score         = round(online_score, 1),
            suitability_score    = round(suitability_score, 1),
            justification        = justification,
            reasoning            = reasoning,
            recommended_services = rec_services if isinstance(rec_services, list) else [service_needed],
            rule_discarded       = False,
        )

    async def evaluate_batch(
        self,
        leads: list,   # List[Lead] — avoid circular import by using list
        concurrency: int = 5,
    ) -> dict:          # lead_id → FilterResult
        """
        Evaluate a list of Lead objects in parallel (bounded concurrency).

        Parameters
        ----------
        leads       : List[Lead]
        concurrency : max parallel LLM calls (default 5)

        Returns
        -------
        dict mapping lead.id → FilterResult
        """
        semaphore = asyncio.Semaphore(concurrency)
        results: dict = {}

        async def _eval(lead):
            async with semaphore:
                result = await self.evaluate(
                    business_name       = lead.business_name,
                    service_needed      = lead.service_needed,
                    pain_points         = lead.pain_points,
                    content             = lead.raw_snippet or "",
                    source_url          = lead.source_url,
                    website             = lead.website,
                    qualification_score = lead.qualification_score,
                )
                results[lead.id] = result

        await asyncio.gather(*[_eval(lead) for lead in leads])
        return results

    def apply_to_leads(self, leads: list, filter_results: dict) -> list:
        """
        Stamp FilterResult fields onto each Lead in-place.
        Removes DISCARD leads from the list.

        Returns the filtered list (HIGH + MEDIUM only), sorted:
            HIGH first, then MEDIUM; within each group sort by qualification_score desc.
        """
        kept = []
        discarded = 0

        for lead in leads:
            result = filter_results.get(lead.id)
            if result is None:
                # No result for this lead — keep as MEDIUM
                lead.filter_priority      = FilterPriority.MEDIUM
                lead.filter_justification = "Not evaluated."
                lead.filter_reasoning     = ""
                kept.append(lead)
                continue

            # Stamp onto lead dataclass
            lead.filter_priority           = result.priority
            lead.filter_justification      = result.justification
            lead.filter_reasoning          = result.reasoning
            lead.filter_online_score       = result.online_score
            lead.filter_suitability_score  = result.suitability_score
            lead.filter_recommended        = result.recommended_services

            if result.priority == FilterPriority.DISCARD:
                discarded += 1
                logger.info("[FILTER] Discarded: %s — %s", lead.business_name, result.justification)
            else:
                kept.append(lead)

        logger.info(
            "[FILTER] Batch complete: %d kept (%d high, %d medium), %d discarded",
            len(kept),
            sum(1 for l in kept if getattr(l, "filter_priority", None) == FilterPriority.HIGH),
            sum(1 for l in kept if getattr(l, "filter_priority", None) == FilterPriority.MEDIUM),
            discarded,
        )

        # Sort: HIGH first, then MEDIUM; within tier by qualification_score desc
        priority_order = {FilterPriority.HIGH: 0, FilterPriority.MEDIUM: 1}
        kept.sort(
            key=lambda l: (
                priority_order.get(getattr(l, "filter_priority", FilterPriority.MEDIUM), 1),
                -l.qualification_score,
            )
        )
        return kept
