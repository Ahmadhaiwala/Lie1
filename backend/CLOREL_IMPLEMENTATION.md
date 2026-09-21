# CLOREL Implementation Guide

## Overview

CLOREL is an **evidence-based B2B lead discovery, verification, and qualification agent** that implements a rigorous pipeline for identifying high-quality sales prospects.

### Core Principle

**"Website Not Found ≠ Rejected Lead"**

A missing website is a SIGNAL that triggers verification and opportunity assessment, not an automatic rejection.

### Goal

**10 evidence-supported prospects > 100 speculative leads**

Quality over quantity. Every lead must be backed by concrete evidence, not LLM speculation.

---

## Architecture

### Pipeline Stages

```
1. Geographic Validation (HARD)
   ↓
2. Business Identity Validation
   ↓
3. Hard Filter Validation (HARD)
   ↓
4. Digital Presence Verification
   ↓
5. Search Intent Analysis
   ↓
6. Demand & Business Signal Analysis
   ↓
7. Service-Fit Assessment
   ↓
8. Evidence Confidence Assessment
   ↓
9. Verification Gate → Routing
```

### Routing Decisions

- **SALES_REVIEW**: High confidence, ready for sales team
- **HOLD**: Valid but insufficient evidence
- **RETRY**: Technical failure (e.g., crawl_failed)
- **REJECT**: Failed hard filters or not a real business

---

## Hard vs Soft Constraints

### Hard Filters (Absolute)

These MUST pass for a lead to qualify:

- **Geographic boundary**: location + radius
- **Target business category**: must match campaign
- **Minimum rating**: if specified in campaign
- **Country constraint**: if specified

**Hard filters cannot be overridden by strong soft signals.**

### Soft Signals (Informational)

These inform opportunity strength but don't determine eligibility:

- Website missing/quality
- Social media presence
- Search intent patterns
- Review frequency
- Booking/ordering systems
- Third-party platforms

---

## Evidence Tracking

### Evidence vs Assumptions

**NEVER mix these!**

**Evidence** (observed facts):
```python
evidence = [
    "Google Business Profile exists",
    "Business has 4.6 rating from 327 reviews",
    "No website listed in profile",
    "Instagram account active with 1.2K followers",
]
```

**Assumptions** (inferences):
```python
assumptions = [
    "Direct ordering could reduce platform dependence",
    "Website could capture more direct bookings",
]
```

---

## Website Status Handling

### Critical: Crawl Failure ≠ Missing

```python
# ✓ CORRECT
if website_status == "crawl_failed":
    routing = "retry"  # Technical issue, not a business signal

# ✗ INCORRECT
if website_status == "crawl_failed":
    website_status = "missing"  # NEVER do this!
```

### Website Status Values

- **active**: Website exists and was successfully crawled
- **missing**: No website URL found (verified absence)
- **crawl_failed**: Technical failure prevented verification
- **unverified**: Status unknown

---

## Service-Fit Assessment

### Example: Restaurant with Missing Website

**Input:**
```python
business = "Royal Spice Restaurant"
website_status = "missing"
rating = 4.5
reviews = 600
search_intent = "ordering"
third_party_platforms = []
```

**Analysis:**
```python
# Evidence
✓ Business is operational (600 reviews, 4.5 rating)
✓ Customers have transactional intent (ordering)
✓ No direct ordering channel found
✓ No third-party platforms identified

# Service Fit Score: 8.5/10
# Reason: Strong ordering demand with no digital channel
```

**Output:**
```python
routing = "sales_review"
pain_points = [
    "Customers seek online ordering but no website exists",
    "No direct digital ordering channel found",
]
```

### Example: Restaurant with Uber Eats

**Input:**
```python
business = "Tasty Bites"
website_status = "missing"
third_party_platforms = ["Uber Eats", "DoorDash"]
```

**Analysis:**
```python
# Evidence
✓ Business has ordering channels via third-party platforms
✓ Platform dependence identified

# Service Fit Score: 6.5/10
# Reason: Has ordering, but opportunity for direct channel
```

**Output:**
```python
routing = "hold" or "sales_review"  # Depends on other factors
pain_points = [
    "Relies on third-party platforms: Uber Eats, DoorDash",
]
assumptions = [
    "Direct ordering website could reduce platform fees",
]
```

---

## Scoring System

### Online Presence Score (0-10)

**Not just website!** Measures complete digital footprint:

```python
score = 0.0

# Website (3 points)
if digital_presence.website:
    score += 3.0

# Social media (3 points)
if digital_presence.instagram:
    score += 1.5
if digital_presence.facebook:
    score += 1.5

# Google presence (2 points)
if digital_presence.google_business:
    score += 2.0

# Booking/ordering (2 points)
if digital_presence.booking_system:
    score += 1.0
if digital_presence.ordering_system:
    score += 1.0

# Third-party platforms (variable)
score += min(len(platforms) * 0.5, 2.0)
```

**Example:**
- Restaurant with NO website but active Instagram, Facebook, Google Business, and Uber Eats
- Score: 0 (website) + 1.5 (IG) + 1.5 (FB) + 2.0 (Google) + 0.5 (Uber) = **5.5/10**

### Service Fit Score (0-10)

Measures opportunity strength for the requested service:

```python
score = 5.0  # Baseline neutral

# Website service
if website_missing and high_digital_intent:
    score += 3.0  # Strong opportunity

if has_third_party_platforms:
    score += 1.0  # Opportunity to own channel

if high_customer_activity:
    score += 1.0  # Business worth targeting

# Penalties
if website_active:
    score -= 2.0  # Already has solution
```

### Confidence Score (0-1)

Measures evidence reliability:

```python
confidence = 0.0

# Business identity (0.25)
if business_name_verified:
    confidence += 0.15
if address_present:
    confidence += 0.10

# Contact info (0.25)
if has_email_or_phone_or_website:
    confidence += 0.25

# Location verification (0.20)
if lat_lng_present:
    confidence += 0.15
if distance_calculated:
    confidence += 0.05

# Evidence depth (0.30)
if evidence_count >= 5:
    confidence += 0.30
elif evidence_count >= 3:
    confidence += 0.20
elif evidence_count >= 1:
    confidence += 0.10
```

---

## Usage

### Basic Usage

```python
from intelligence.clorel_qualifier import ClorelQualifier

# Initialize
qualifier = ClorelQualifier(llm_client=None)  # LLM optional

# Campaign configuration
campaign = {
    "service": "website",
    "target_categories": ["restaurant", "cafe"],
    "location": "Ahmedabad",
    "radius_km": 10.0,
    "minimum_rating": 4.0,
    "country": "India",
}

# Lead data
lead_data = {
    "id": "lead-001",
    "business_name": "Royal Spice Restaurant",
    "website": None,
    "website_status": "missing",
    "city": "Ahmedabad",
    "distance_km": 2.4,
    "rating": 4.5,
    "review_count": 600,
    # ... more fields
}

# Qualify
qualified_lead = await qualifier.qualify(lead_data, campaign)

# Check routing
if qualified_lead.routing == LeadRouting.SALES_REVIEW:
    print("✓ Ready for sales!")
    print(f"Confidence: {qualified_lead.confidence:.0%}")
    print(f"Service fit: {qualified_lead.service_fit_score:.1f}/10")
```

### Batch Qualification

```python
# Qualify multiple leads
leads_data = [lead1, lead2, lead3, ...]
qualified_leads = await qualifier.qualify_batch(leads_data, campaign)

# Leads are sorted by routing + confidence
for lead in qualified_leads:
    print(f"{lead.business_name}: {lead.routing.value}")
```

### Integration with Workflows

```python
from automation.workflows import LeadWorkflow

workflow = LeadWorkflow(
    use_clorel=True,  # Enable CLOREL
    campaign={
        "service": "website",
        "location": "Ahmedabad",
        "radius_km": 10.0,
        "minimum_rating": 4.0,
    },
)

# Run discovery + qualification
report = await workflow.run()

# Results filtered by routing
print(f"Sales-ready leads: {report['summary']['high_priority']}")
```

---

## Output Format

### ClorelLead Structure

```json
{
  "id": "lead-001",
  "business_name": "Royal Spice Restaurant",
  "contact_person": null,
  "service_needed": "website",
  "source_url": "https://maps.google.com/...",
  "discovery_source": "google_maps",
  "website": null,
  "contact_email": [],
  "contact_phone": ["+91 94267 68480"],
  
  "location": {
    "address": "123 Main St, Ahmedabad",
    "city": "Ahmedabad",
    "state": "Gujarat",
    "country": "India",
    "distance_km": 2.4,
    "latitude": 23.0436,
    "longitude": 72.5704,
    "location_confidence": 0.8
  },
  
  "industry": "Indian Restaurant",
  "website_status": "missing",
  
  "digital_presence": {
    "website": false,
    "instagram": false,
    "facebook": false,
    "google_business": true,
    "booking_system": false,
    "ordering_system": false,
    "third_party_platforms": []
  },
  
  "search_intent": {
    "primary": "ordering",
    "secondary": ["local_discovery", "reservation"],
    "strength": 0.7
  },
  
  "demand_signals": {
    "rating": 4.5,
    "review_count": 600,
    "recent_activity": "high",
    "opening_hours_verified": true
  },
  
  "pain_points": [
    "Customers seek online ordering but no website exists",
    "No direct digital ordering channel found"
  ],
  
  "evidence": [
    "Geographic constraint satisfied",
    "Business identity verified: Royal Spice Restaurant",
    "Hard filters passed",
    "Website status: missing",
    "Online presence score: 3.5/10",
    "Primary search intent: ordering",
    "Rating: 4.5/5",
    "Reviews: 600",
    "High customer activity: 600 reviews"
  ],
  
  "assumptions": [],
  
  "qualification_score": 0.75,
  "online_presence_score": 3.5,
  "service_fit_score": 8.5,
  "confidence": 0.82,
  
  "routing": "sales_review",
  "filter_priority": "high",
  "filter_justification": "High-confidence lead with strong evidence",
  "filter_reasoning": "Royal Spice Restaurant is a Indian Restaurant business located 2.4km from search center with no website found and high customer activity (600 reviews). Strong service fit (8.5/10) with high-confidence evidence (82%).",
  "filter_recommended": ["website", "seo"],
  "review_reasons": [
    "High confidence with strong service fit",
    "Confidence: 0.82, Service fit: 8.5/10"
  ],
  
  "outreach_sent": false
}
```

---

## Best Practices

### 1. Never Invent Pain Points

**BAD:**
```python
pain_points = [
    "Restaurant loses customers",  # No evidence
    "Needs better SEO",  # Generic assumption
]
```

**GOOD:**
```python
pain_points = [
    "No website listed in Google Business Profile",  # Observed fact
    "Customers search for menu but no online menu found",  # Evidence-backed
]
```

### 2. Separate Assumptions

**BAD:**
```python
evidence = [
    "No website found",
    "Direct ordering could reduce platform fees",  # This is assumption!
]
```

**GOOD:**
```python
evidence = [
    "No website found in Google Business Profile",
    "Business uses Uber Eats for ordering",
]
assumptions = [
    "Direct ordering could reduce platform fees",
]
```

### 3. Preserve Technical Failures

**BAD:**
```python
if crawl_failed:
    website_status = "missing"  # Lost information!
    routing = "hold"
```

**GOOD:**
```python
if website_status == "crawl_failed":
    routing = "retry"  # Preserve failure signal
    review_reasons = ["Website crawl failed - needs retry"]
```

### 4. Geographic Constraints are HARD

**BAD:**
```python
# Strong business but outside radius
if business_looks_amazing:
    ignore_distance = True  # NEVER!
```

**GOOD:**
```python
# Geographic constraint must pass first
if distance > campaign_radius:
    routing = "reject"
    reason = f"Outside {campaign_radius}km radius"
    return  # Stop pipeline immediately
```

---

## Testing

Run the example script:

```bash
cd backend
python examples/clorel_usage.py
```

Expected output:
- 6 example leads processed
- Routing decisions explained
- Evidence listed for each
- Summary statistics

---

## Migration from Legacy System

### Old (Score-Based)

```python
# Simple qualification score
if lead.qualification_score >= 0.5:
    qualified_leads.append(lead)
```

### New (CLOREL Evidence-Based)

```python
# Multi-factor evidence-based routing
qualified_lead = await clorel_qualifier.qualify(lead_data, campaign)

if qualified_lead.routing == LeadRouting.SALES_REVIEW:
    # High confidence + strong service fit + verified evidence
    sales_ready_leads.append(qualified_lead)
elif qualified_lead.routing == LeadRouting.HOLD:
    # Valid but needs more evidence
    hold_leads.append(qualified_lead)
```

### Enable CLOREL in Workflows

```python
workflow = LeadWorkflow(
    use_clorel=True,  # Enable new system
    campaign={...},
)
```

To use legacy system:
```python
workflow = LeadWorkflow(
    use_clorel=False,  # Use old score-based system
)
```

---

## Troubleshooting

### All leads rejected

**Check:**
- Geographic constraints (radius too small?)
- Minimum rating too high?
- Target categories too restrictive?

### Low confidence scores

**Check:**
- Evidence list populated?
- Contact information present?
- Location data available?

### Too many HOLD leads

**Possible causes:**
- Insufficient evidence from discovery
- Website crawl failures
- Missing operational signals

**Solutions:**
- Improve discovery data quality
- Add retry logic for crawl failures
- Enrich with additional data sources

---

## Key Differences from Legacy System

| Aspect | Legacy | CLOREL |
|--------|--------|--------|
| **Qualification** | Single score | Multi-factor routing |
| **Website missing** | Often rejected | Triggers verification |
| **Evidence** | Mixed with assumptions | Strictly separated |
| **Geographic** | Soft filter | Hard constraint |
| **Digital presence** | Website-only | Multi-channel assessment |
| **Pain points** | LLM-generated | Evidence-backed only |
| **Technical failures** | Treated as missing | Routed to retry |
| **Confidence** | N/A | Explicit reliability score |

---

## Summary

CLOREL transforms lead qualification from a simple scoring system into a rigorous evidence-based pipeline that:

✓ Separates hard constraints from soft signals  
✓ Preserves technical failures for retry  
✓ Tracks evidence separately from assumptions  
✓ Assesses complete digital footprint, not just website  
✓ Routes based on confidence + service fit + evidence depth  

**Result: 10 high-quality prospects with real opportunities, not 100 speculative leads.**
