"""
filters/filter_rules.py
-----------------------
Rule-based pre-screening BEFORE the LLM is called.

Purpose: fast, deterministic rejection of business types that will NEVER
need digital services (SEO / website / chatbot), so we don't waste LLM
tokens on them.

Two kinds of rules
------------------
1. HARD_DISCARD_CATEGORIES  – business categories that are inherently
   offline / cash-only / local physical-only.
   Examples: street food stalls, roadside vendors, small tea shops.

2. HARD_DISCARD_KEYWORDS    – individual words or phrases that appear in
   the scraped content / business name and signal no digital need.

One function is exported:
    rule_based_discard(business_name, content, industry) -> (bool, str)
    Returns (should_discard, reason)
"""

from __future__ import annotations
from typing import Tuple
import re

# ---------------------------------------------------------------------------
# Hard-discard business categories
# (case-insensitive substring match on the detected industry / description)
# ---------------------------------------------------------------------------
HARD_DISCARD_CATEGORIES: list[str] = [
    # Traditional food & street vendors
    "street food",
    "food stall",
    "food cart",
    "food truck",       # trucks can sometimes use digital — but low ROI, discard
    "roadside stall",
    "roadside vendor",
    "mobile vendor",
    "hawker",
    "tea stall",
    "chai stall",
    "dhaba",            # roadside eatery (South Asia)
    "thela",            # push-cart vendor (Urdu/Hindi)
    "rehri",            # street cart

    # Pure physical / cash-only services with no meaningful digital upside
    "shoe repair",
    "shoe shining",
    "cobbler",
    "laundry wala",
    "dhobi",            # traditional washerman
    "barber stall",
    "roadside barber",

    # Agriculture / informal labour
    "subsistence farm",
    "small farm",
    "farm labour",
    "daily wage",
    "daily wager",

    # Religious / non-commercial
    "mosque",
    "masjid",
    "temple trust",
    "church charity",
    "non-profit shrine",
]

# ---------------------------------------------------------------------------
# Hard-discard keywords
# (case-insensitive whole-word match in business name OR scraped content)
# ---------------------------------------------------------------------------
HARD_DISCARD_KEYWORDS: list[str] = [
    # Explicit offline / no-internet signals
    "no internet",
    "cash only",
    "no card",
    "walk-in only",
    "no delivery",
    "no online",
    "no website needed",
    "we don't use internet",

    # Spam / junk content
    "lorem ipsum",
    "under construction",       # but NOT "website under construction" — that's a lead!
    "coming soon",              # ambiguous; handled carefully below
    "parked domain",
    "domain for sale",
    "buy this domain",
    "this domain is for sale",
]

# ---------------------------------------------------------------------------
# Keywords that SHOULD NOT trigger discard even if matched above
# (whitelist overrides)
# ---------------------------------------------------------------------------
WHITELIST_OVERRIDES: list[str] = [
    "website under construction",   # has a website, just building it
    "coming soon website",
    "new website coming soon",
]

# ---------------------------------------------------------------------------
# Industry / business types that almost always NEED digital services
# (used to prevent false positives when category heuristics fire)
# ---------------------------------------------------------------------------
ALWAYS_DIGITAL_CATEGORIES: list[str] = [
    "clinic",
    "hospital",
    "dentist",
    "lawyer",
    "law firm",
    "accountant",
    "architect",
    "real estate",
    "property",
    "school",
    "academy",
    "coaching",
    "tuition",
    "gym",
    "fitness",
    "restaurant",
    "cafe",
    "hotel",
    "salon",
    "spa",
    "boutique",
    "pharmacy",
    "software",
    "tech",
    "startup",
    "ecommerce",
    "online store",
    "digital",
    "agency",
    "consultancy",
    "freelancer",
    "photographer",
    "videographer",
    "studio",
]


def _contains(text: str, keywords: list[str]) -> Tuple[bool, str]:
    """Return (True, matched_keyword) if any keyword found in text."""
    lower = text.lower()
    for kw in keywords:
        if kw.lower() in lower:
            return True, kw
    return False, ""


def _word_match(text: str, keywords: list[str]) -> Tuple[bool, str]:
    """Whole-word regex match. Returns (matched, keyword)."""
    lower = text.lower()
    for kw in keywords:
        pattern = r"\b" + re.escape(kw.lower()) + r"\b"
        if re.search(pattern, lower):
            return True, kw
    return False, ""


def rule_based_discard(
    business_name: str,
    content: str,
    industry: str = "",
) -> Tuple[bool, str]:
    """
    Fast rule-based pre-screen.

    Parameters
    ----------
    business_name : str   Name of the business.
    content       : str   Scraped page text (markdown / cleaned HTML).
    industry      : str   Detected industry / category if available.

    Returns
    -------
    (should_discard: bool, reason: str)
        should_discard=True  → skip LLM, mark as DISCARD immediately.
        should_discard=False → pass to LLM for deeper evaluation.
    """
    combined = f"{business_name} {industry} {content[:3000]}".lower()

    # 1. Whitelist override — if any whitelist phrase present, never discard
    matched_white, _ = _contains(combined, WHITELIST_OVERRIDES)
    if matched_white:
        return False, ""

    # 2. Always-digital category — skip discard checks
    matched_digital, _ = _contains(combined, ALWAYS_DIGITAL_CATEGORIES)
    if matched_digital:
        return False, ""

    # 3. Hard-discard category check
    matched_cat, cat_kw = _contains(combined, HARD_DISCARD_CATEGORIES)
    if matched_cat:
        return True, (
            f"Business category '{cat_kw}' is a traditional offline business "
            "that does not benefit from digital services."
        )

    # 4. Hard-discard keyword check (whole-word on name + content)
    matched_kw, kw = _word_match(combined, HARD_DISCARD_KEYWORDS)
    if matched_kw:
        return True, (
            f"Content contains disqualifying signal: '{kw}'. "
            "Business appears to be cash-only or explicitly offline."
        )

    return False, ""
