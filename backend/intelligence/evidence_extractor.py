"""
evidence_extractor.py
---------------------
Extracts structured evidence from raw crawled page content.

Input  : Raw page text (from Crawl4AI) + ResearchPlan signals
Output : List[Evidence]  — each item is an observed fact + its source URL

Key principle (from README section 4):
  Store FACTS, not inferences.
  ✓ "No 'Order Online' button found on menu page"
  ✗ "Restaurant needs an ordering system"
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from .research_planner import ResearchPlan


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Evidence:
    """A single observed finding from a crawled page."""
    finding: str
    source_url: str
    signal_type: str          # "positive" | "negative" | "neutral"
    matched_signal: str = ""  # which signal keyword triggered this
    page_section: str = ""    # e.g. "contact", "menu", "header"

    def to_dict(self) -> dict:
        return {
            "finding": self.finding,
            "source_url": self.source_url,
            "signal_type": self.signal_type,
            "matched_signal": self.matched_signal,
            "page_section": self.page_section,
        }


# ---------------------------------------------------------------------------
# Extractor
# ---------------------------------------------------------------------------

class EvidenceExtractor:
    """
    Scans crawled page text for signals defined in a ResearchPlan and
    returns a list of Evidence objects.

    Usage
    -----
    >>> extractor = EvidenceExtractor()
    >>> evidence_list = extractor.extract(
    ...     page_text="Call us to book your appointment. WhatsApp: +1234",
    ...     source_url="https://example.com/contact",
    ...     plan=research_plan,
    ... )
    """

    def extract(
        self,
        page_text: str,
        source_url: str,
        plan: ResearchPlan,
        page_section: str = "",
    ) -> List[Evidence]:
        """
        Extract evidence from a single page.

        Parameters
        ----------
        page_text : str
            Clean text content of the crawled page.
        source_url : str
            URL where the content was found.
        plan : ResearchPlan
            Research plan containing signals and negative_signals.
        page_section : str, optional
            Human-readable section label (e.g. "contact", "menu").

        Returns
        -------
        List[Evidence]
        """
        if not page_text:
            return []

        text_lower = page_text.lower()
        evidence: List[Evidence] = []

        # --- Positive signals (things we WANT to find = potential problem) ---
        for signal in plan.signals:
            if signal.lower() in text_lower:
                snippet = self._extract_snippet(page_text, signal)
                evidence.append(Evidence(
                    finding=f'"{signal}" detected on page — {snippet}',
                    source_url=source_url,
                    signal_type="positive",
                    matched_signal=signal,
                    page_section=page_section,
                ))

        # --- Negative signals (business ALREADY has the solution) ---
        for signal in plan.negative_signals:
            if signal.lower() in text_lower:
                snippet = self._extract_snippet(page_text, signal)
                evidence.append(Evidence(
                    finding=f'"{signal}" found — solution may already exist. {snippet}',
                    source_url=source_url,
                    signal_type="negative",
                    matched_signal=signal,
                    page_section=page_section,
                ))

        # --- Structural observations (always useful) ---
        evidence.extend(self._structural_observations(page_text, source_url, page_section))

        return evidence

    def extract_from_pages(
        self,
        pages: List[dict],
        plan: ResearchPlan,
    ) -> List[Evidence]:
        """
        Extract evidence from multiple crawled pages.

        Parameters
        ----------
        pages : List[dict]
            Each dict must have keys: 'text' (str) and 'url' (str).
            Optional key: 'section' (str).

        Returns
        -------
        List[Evidence]
        """
        all_evidence: List[Evidence] = []
        for page in pages:
            text = page.get("text", "")
            url = page.get("url", "")
            section = page.get("section", self._url_to_section(url))
            all_evidence.extend(self.extract(text, url, plan, section))
        return all_evidence

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_snippet(self, text: str, keyword: str, context_chars: int = 80) -> str:
        """Return a short snippet around the keyword."""
        idx = text.lower().find(keyword.lower())
        if idx == -1:
            return ""
        start = max(0, idx - context_chars // 2)
        end = min(len(text), idx + len(keyword) + context_chars // 2)
        snippet = text[start:end].strip().replace("\n", " ")
        return f'[…{snippet}…]'

    def _structural_observations(
        self,
        text: str,
        source_url: str,
        page_section: str,
    ) -> List[Evidence]:
        """Detect standard structural signals (forms, phone numbers, etc.)."""
        observations: List[Evidence] = []
        text_lower = text.lower()

        checks = [
            (r"<form|contact form|inquiry form", "Contact/inquiry form detected on page"),
            (r"\+?\d[\d\s\-]{7,}\d", "Phone number found on page"),
            (r"whatsapp", "WhatsApp contact method found"),
            (r"mailto:", "Email address found via mailto link"),
            (r"book\s+now|book\s+online|schedule\s+online", "Online booking CTA found"),
            (r"order\s+online|place\s+order|add\s+to\s+cart", "Online ordering CTA found"),
        ]

        for pattern, label in checks:
            if re.search(pattern, text_lower):
                observations.append(Evidence(
                    finding=label,
                    source_url=source_url,
                    signal_type="neutral",
                    matched_signal=pattern,
                    page_section=page_section,
                ))

        return observations

    @staticmethod
    def _url_to_section(url: str) -> str:
        """Derive a section label from the URL path."""
        path = url.rstrip("/").split("/")[-1]
        return path if path else "homepage"
