# CLOREL Quick Start Guide

## What is CLOREL?

CLOREL is an **evidence-based B2B lead qualification system** that replaces simple scoring with a rigorous validation pipeline.

**Core Principle:** "Website Not Found ≠ Rejected Lead"

**Goal:** 10 evidence-supported prospects > 100 speculative leads

---

## Installation

CLOREL is already integrated into the intelligence module. No additional installation needed.

```python
from intelligence.clorel_qualifier import ClorelQualifier
```

---

## Quick Example

```python
from intelligence.clorel_qualifier import ClorelQualifier, LeadRouting

# Initialize
qualifier = ClorelQualifier()

# Campaign config
campaign = {
    "service": "website",
    "location": "Ahmedabad",
    "radius_km": 10.0,
    "minimum_rating": 4.0,
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
    "contact_phone": ["+91 1234567890"],
}

# Qualify
lead = await qualifier.qualify(lead_data, campaign)

# Check result
if lead.routing == LeadRouting.SALES_REVIEW:
    print(f"✓ {lead.business_name} is sales-ready!")
    print(f"  Confidence: {lead.confidence:.0%}")
    print(f"  Service fit: {lead.service_fit_score:.1f}/10")
```

---

## Key Concepts

### 1. Hard vs Soft Filters

**Hard Filters** (must pass):
- Geographic location + radius
- Minimum rating
- Target business category

**Soft Signals** (inform opportunity):
- Website presence/quality
- Social media activity
- Search intent patterns

### 2. Routing Decisions

- **SALES_REVIEW**: High confidence, ready for sales
- **HOLD**: Valid but needs more evidence
- **RETRY**: Technical failure (e.g., crawl failed)
- **REJECT**: Failed validation

### 3. Evidence Tracking

Always separate:
- **Evidence**: Observed facts
- **Assumptions**: Inferences

```python
# Evidence
lead.evidence = [
    "No website found in Google Business Profile",
    "Business has 600 reviews with 4.5 rating",
]

# Assumptions (kept separate!)
lead.assumptions = [
    "Website could capture more direct orders",
]
```

---

## Integration with Workflows

### Enable CLOREL

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

report = await workflow.run()
```

### Disable CLOREL (use legacy)

```python
workflow = LeadWorkflow(
    use_clorel=False,  # Use old score-based system
)
```

---

## Understanding Scores

### Online Presence Score (0-10)

Measures **complete** digital footprint:
- Website (3 pts)
- Social media (3 pts)
- Google Business (2 pts)
- Booking/ordering systems (2 pts)
- Third-party platforms (variable)

**Example:** No website but has Instagram + Facebook + Google = 5.5/10

### Service Fit Score (0-10)

Measures opportunity strength:
- 8-10: Strong evidence of need
- 5-7: Moderate opportunity
- 0-4: Limited or no fit

### Confidence (0-1)

Measures evidence reliability:
- 0.75+: High confidence
- 0.50-0.75: Moderate
- <0.50: Low confidence

---

## Common Patterns

### Pattern 1: Missing Website + High Activity

```python
# Input
website_status = "missing"
rating = 4.5
review_count = 600
search_intent = "ordering"

# Result
→ routing = "sales_review"
→ service_fit_score = 8.5/10
→ confidence = 0.82

# Why: Strong transactional demand with no digital channel
```

### Pattern 2: Crawl Failed

```python
# Input
website_status = "crawl_failed"

# Result
→ routing = "retry"

# Why: Technical failure, not a business signal
# NEVER treat as "missing"!
```

### Pattern 3: Outside Radius

```python
# Input
campaign_radius = 10.0
business_distance = 15.5

# Result
→ routing = "reject"

# Why: Hard geographic constraint failed
# Strong soft signals cannot override
```

---

## Testing

Run the demo:

```bash
cd backend
python examples/clorel_usage.py
```

Output shows 6 example leads with:
- Detailed qualification results
- Evidence lists
- Routing decisions
- Summary statistics

---

## Troubleshooting

### Problem: All leads rejected

**Solution:** Check campaign constraints
```python
# Too strict?
campaign = {
    "radius_km": 5.0,      # Maybe increase?
    "minimum_rating": 4.5,  # Maybe lower?
}
```

### Problem: Low confidence scores

**Solution:** Enrich lead data
- Add contact information
- Include location coordinates
- Capture operational signals

### Problem: Many HOLD leads

**Solution:** Improve evidence collection
- Add more discovery sources
- Implement retry logic for failures
- Enrich with additional data

---

## Migration Checklist

Switching from legacy to CLOREL:

- [ ] Update workflow initialization: `use_clorel=True`
- [ ] Update campaign config with hard constraints
- [ ] Test with sample leads
- [ ] Review routing distribution
- [ ] Adjust thresholds if needed
- [ ] Update downstream systems to handle routing

---

## Next Steps

1. **Read full guide:** `CLOREL_IMPLEMENTATION.md`
2. **Run examples:** `python examples/clorel_usage.py`
3. **Enable in workflows:** Set `use_clorel=True`
4. **Monitor results:** Check routing distribution
5. **Iterate:** Adjust campaign constraints based on results

---

## Key Takeaways

✓ CLOREL separates hard constraints from soft signals  
✓ Missing websites trigger verification, not rejection  
✓ Evidence must support all pain points  
✓ Technical failures are preserved for retry  
✓ Quality > quantity: 10 solid leads > 100 maybes  

**Remember:** If evidence is weak, route to HOLD. Don't manufacture confidence.
