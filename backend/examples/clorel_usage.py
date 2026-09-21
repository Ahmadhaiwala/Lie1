"""
CLOREL Usage Example
--------------------
Demonstrates how to use the CLOREL evidence-based qualification framework.

Key Principles:
  1. "Website Not Found ≠ Rejected Lead"
  2. Hard filters (location, rating) are absolute
  3. Soft signals (digital presence) inform opportunity assessment
  4. Evidence must support pain points
  5. Route based on confidence + service fit

Usage:
    python examples/clorel_usage.py
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from intelligence.clorel_qualifier import ClorelQualifier, LeadRouting
from llm.llm_client import LLMClient
from llm.llm_config import LLMConfig


# ---------------------------------------------------------------------------
# Example Campaign Configuration
# ---------------------------------------------------------------------------

CAMPAIGN_WEBSITE_AHMEDABAD = {
    "service": "website",
    "target_categories": ["restaurant", "cafe", "italian restaurant", "asian restaurant"],
    "location": "Ahmedabad",
    "radius_km": 10.0,
    "minimum_rating": 4.0,
    "country": "India",
}


# ---------------------------------------------------------------------------
# Example Lead Data
# ---------------------------------------------------------------------------

# Example 1: Restaurant with NO website but high activity
LEAD_MISSING_WEBSITE = {
    "id": "lead-001",
    "business_name": "Royal Spice Restaurant",
    "source_url": "https://maps.google.com/...",
    "website": None,
    "website_status": "missing",
    "contact_email": [],
    "contact_phone": ["+91 94267 68480"],
    "address": "123 Main Street, Ahmedabad",
    "city": "Ahmedabad",
    "state": "Gujarat",
    "country": "India",
    "industry": "Indian Restaurant",
    "rating": 4.5,
    "review_count": 600,
    "distance_km": 2.4,
    "latitude": 23.0436,
    "longitude": 72.5704,
    "pain_points": ["No website found in Google Business Profile"],
    "raw_snippet": "Royal Spice Restaurant. Popular Indian restaurant. Open daily 11am-11pm. +91 94267 68480",
    "discovered_at": "2026-09-21T10:00:00",
}

# Example 2: Restaurant with website crawl failure (NOT missing!)
LEAD_CRAWL_FAILED = {
    "id": "lead-002",
    "business_name": "Bella Italia Trattoria",
    "source_url": "https://bellaitalia.example.com",
    "website": "https://bellaitalia.example.com",
    "website_status": "crawl_failed",
    "contact_email": ["info@bellaitalia.example.com"],
    "contact_phone": ["+91 79 1234 5678"],
    "address": "456 Restaurant Row, Ahmedabad",
    "city": "Ahmedabad",
    "state": "Gujarat",
    "country": "India",
    "industry": "Italian Restaurant",
    "rating": 4.7,
    "review_count": 320,
    "distance_km": 3.2,
    "latitude": 23.0500,
    "longitude": 72.5800,
    "pain_points": [],
    "raw_snippet": "Bella Italia Trattoria. Authentic Italian cuisine. Website: bellaitalia.example.com",
    "discovered_at": "2026-09-21T10:05:00",
}

# Example 3: Outside geographic boundary (should REJECT)
LEAD_OUTSIDE_RADIUS = {
    "id": "lead-003",
    "business_name": "Mumbai Masala House",
    "source_url": "https://maps.google.com/...",
    "website": None,
    "website_status": "missing",
    "contact_email": [],
    "contact_phone": ["+91 22 1234 5678"],
    "address": "789 Mumbai Street, Mumbai",
    "city": "Mumbai",
    "state": "Maharashtra",
    "country": "India",
    "industry": "Indian Restaurant",
    "rating": 4.8,
    "review_count": 1200,
    "distance_km": 450.0,  # Way outside radius!
    "latitude": 19.0760,
    "longitude": 72.8777,
    "pain_points": ["No website found"],
    "raw_snippet": "Mumbai Masala House. Award-winning restaurant.",
    "discovered_at": "2026-09-21T10:10:00",
}

# Example 4: Rating below minimum (should REJECT)
LEAD_LOW_RATING = {
    "id": "lead-004",
    "business_name": "Quick Bites Cafe",
    "source_url": "https://maps.google.com/...",
    "website": None,
    "website_status": "missing",
    "contact_email": [],
    "contact_phone": ["+91 94267 11111"],
    "address": "321 Cafe Street, Ahmedabad",
    "city": "Ahmedabad",
    "state": "Gujarat",
    "country": "India",
    "industry": "Cafe",
    "rating": 3.5,  # Below minimum 4.0
    "review_count": 45,
    "distance_km": 1.8,
    "latitude": 23.0400,
    "longitude": 72.5700,
    "pain_points": ["No website"],
    "raw_snippet": "Quick Bites Cafe. Fast service.",
    "discovered_at": "2026-09-21T10:15:00",
}

# Example 5: Not a real business (article)
LEAD_NOT_A_BUSINESS = {
    "id": "lead-005",
    "business_name": "How to Start a Restaurant in Ahmedabad",
    "source_url": "https://medium.com/restaurant-guide",
    "website": None,
    "website_status": "unverified",
    "contact_email": [],
    "contact_phone": [],
    "address": "",
    "city": "Ahmedabad",
    "state": "Gujarat",
    "country": "India",
    "industry": "article",
    "rating": None,
    "review_count": None,
    "distance_km": None,
    "latitude": None,
    "longitude": None,
    "pain_points": [],
    "raw_snippet": "Article about starting restaurants...",
    "discovered_at": "2026-09-21T10:20:00",
}

# Example 6: Strong digital presence but missing direct ordering
LEAD_STRONG_PRESENCE = {
    "id": "lead-006",
    "business_name": "Fusion Kitchen",
    "source_url": "https://fusionkitchen.example.com",
    "website": "https://fusionkitchen.example.com",
    "website_status": "active",
    "contact_email": ["hello@fusionkitchen.example.com"],
    "contact_phone": ["+91 79 9999 8888"],
    "address": "555 Modern Plaza, Ahmedabad",
    "city": "Ahmedabad",
    "state": "Gujarat",
    "country": "India",
    "industry": "Asian Fusion Restaurant",
    "rating": 4.6,
    "review_count": 890,
    "distance_km": 4.5,
    "latitude": 23.0600,
    "longitude": 72.5600,
    "pain_points": ["Customers search for online ordering but no system found"],
    "raw_snippet": "Fusion Kitchen. Modern Asian fusion. Instagram: @fusionkitchen. Facebook: FusionKitchenAhmedabad. High customer engagement on social media.",
    "discovered_at": "2026-09-21T10:25:00",
}


# ---------------------------------------------------------------------------
# Main Demo
# ---------------------------------------------------------------------------

async def demo_clorel():
    """Run CLOREL qualification on example leads."""
    
    print("=" * 80)
    print("CLOREL Evidence-Based Qualification Demo")
    print("=" * 80)
    print()
    
    # Initialize qualifier
    # Note: LLM is optional - deterministic rules handle most validation
    qualifier = ClorelQualifier(llm_client=None)
    
    # Example leads
    leads = [
        LEAD_MISSING_WEBSITE,
        LEAD_CRAWL_FAILED,
        LEAD_OUTSIDE_RADIUS,
        LEAD_LOW_RATING,
        LEAD_NOT_A_BUSINESS,
        LEAD_STRONG_PRESENCE,
    ]
    
    # Qualify each lead
    for i, lead_data in enumerate(leads, 1):
        print(f"\n{'─' * 80}")
        print(f"Lead {i}/{len(leads)}: {lead_data['business_name']}")
        print(f"{'─' * 80}")
        
        # Run qualification
        qualified_lead = await qualifier.qualify(lead_data, CAMPAIGN_WEBSITE_AHMEDABAD)
        
        # Display results
        print(f"\n✓ BUSINESS: {qualified_lead.business_name}")
        print(f"  Industry: {qualified_lead.industry}")
        print(f"  Location: {qualified_lead.location.city}, {qualified_lead.location.distance_km}km")
        print(f"\n✓ WEBSITE STATUS: {qualified_lead.website_status.value}")
        print(f"  Online Presence Score: {qualified_lead.online_presence_score:.1f}/10")
        print(f"  Service Fit Score: {qualified_lead.service_fit_score:.1f}/10")
        print(f"  Confidence: {qualified_lead.confidence:.0%}")
        
        print(f"\n✓ DIGITAL PRESENCE:")
        dp = qualified_lead.digital_presence
        print(f"  Website: {'✓' if dp.website else '✗'}")
        print(f"  Instagram: {'✓' if dp.instagram else '✗'}")
        print(f"  Facebook: {'✓' if dp.facebook else '✗'}")
        print(f"  Google Business: {'✓' if dp.google_business else '✗'}")
        if dp.third_party_platforms:
            print(f"  Platforms: {', '.join(dp.third_party_platforms)}")
        
        print(f"\n✓ SEARCH INTENT:")
        print(f"  Primary: {qualified_lead.search_intent.primary.value}")
        print(f"  Strength: {qualified_lead.search_intent.strength:.0%}")
        
        if qualified_lead.pain_points:
            print(f"\n✓ PAIN POINTS (evidence-backed):")
            for pp in qualified_lead.pain_points:
                print(f"  • {pp}")
        
        if qualified_lead.evidence:
            print(f"\n✓ EVIDENCE ({len(qualified_lead.evidence)} items):")
            for ev in qualified_lead.evidence[:5]:  # Show first 5
                print(f"  • {ev}")
            if len(qualified_lead.evidence) > 5:
                print(f"  ... and {len(qualified_lead.evidence) - 5} more")
        
        print(f"\n✓ ROUTING: {qualified_lead.routing.value.upper()}")
        print(f"  Priority: {qualified_lead.filter_priority}")
        print(f"  Justification: {qualified_lead.filter_justification}")
        
        if qualified_lead.review_reasons:
            print(f"\n✓ REVIEW REASONS:")
            for reason in qualified_lead.review_reasons:
                print(f"  • {reason}")
        
        print()
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    qualified_batch = await qualifier.qualify_batch(leads, CAMPAIGN_WEBSITE_AHMEDABAD)
    
    routing_counts = {
        LeadRouting.SALES_REVIEW: 0,
        LeadRouting.HOLD: 0,
        LeadRouting.RETRY: 0,
        LeadRouting.REJECT: 0,
    }
    
    for lead in qualified_batch:
        routing_counts[lead.routing] += 1
    
    print(f"\nTotal Leads: {len(leads)}")
    print(f"  → SALES_REVIEW: {routing_counts[LeadRouting.SALES_REVIEW]} (ready for sales)")
    print(f"  → HOLD: {routing_counts[LeadRouting.HOLD]} (needs more evidence)")
    print(f"  → RETRY: {routing_counts[LeadRouting.RETRY]} (technical failure)")
    print(f"  → REJECT: {routing_counts[LeadRouting.REJECT]} (failed validation)")
    
    print("\n✓ CLOREL Principle: 'Website Not Found ≠ Rejected Lead'")
    print("  Missing websites trigger verification, not automatic rejection.")
    print("  Goal: 10 evidence-supported prospects > 100 speculative leads")
    print()


if __name__ == "__main__":
    asyncio.run(demo_clorel())
