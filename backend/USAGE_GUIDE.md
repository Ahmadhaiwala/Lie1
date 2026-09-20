# Lead Generation System - Usage Guide

## Quick Start

### Run Lead Generation

```python
import asyncio
from automation.workflows import LeadWorkflow

async def main():
    # Initialize workflow
    workflow = LeadWorkflow(
        min_score=0.6,  # Only keep leads with score >= 0.6
        output_dir="leads_output"
    )
    
    # Run full pipeline (all services)
    report = await workflow.run()
    
    # Check results
    print(f"Total leads found: {report['summary']['filtered_leads']}")
    print(f"High priority: {report['summary']['high_priority']}")
    print(f"Medium priority: {report['summary']['medium_priority']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Run Specific Service

```python
# Run only for WhatsApp bot leads
report = await workflow.run(service="whatsapp_bot")

# Run only for website leads
report = await workflow.run(service="website")

# Run only for SEO leads
report = await workflow.run(service="seo")
```

### Use Custom Search Queries

```python
# Target specific locations or industries
custom_queries = [
    "restaurants in Chicago directory contact",
    "dental clinics Los Angeles website phone",
    "law firms Boston contact information",
]

workflow = LeadWorkflow(
    search_queries=custom_queries,
    min_score=0.6
)

report = await workflow.run()
```

---

## Understanding Output

### Lead Structure

Each lead contains:

```json
{
  "id": "uuid",
  "business_name": "Actual Business Name",  // ✅ Specific business
  "source_url": "https://business-website.com",
  "service_needed": "website|whatsapp_bot|seo",
  
  "contact_email": ["contact@business.com"],
  "contact_phone": ["+1-555-1234"],
  "website": "https://business-website.com",
  
  "location": "Chicago, IL",
  "industry": "Restaurant",
  
  "pain_points": [
    "Website only shows phone number - no online ordering",
    "Last updated in 2016 with broken images"
  ],
  
  "qualification_score": 0.75,  // 0.0 - 1.0
  
  "filter_priority": "high|medium|low",
  "filter_online_score": 5.0,  // 0-10
  "filter_suitability_score": 8.0,  // 0-10
  "filter_recommended": ["website", "whatsapp_bot"]
}
```

### Priority Levels

- **HIGH**: Strong evidence + clear need + good contact info → Reach out immediately
- **MEDIUM**: Good potential + some evidence → Worth contacting
- **LOW**: Weak signals → Monitor or skip

---

## What Makes a Valid Lead?

### ✅ Valid Leads

1. **Specific Business with Location**
   ```json
   {
     "business_name": "Mario's Pizza Chicago",
     "location": "Chicago, IL",
     "website": "https://mariospizzachicago.com",
     "pain_points": ["No online ordering option found"]
   }
   ```

2. **Clear Service Need with Evidence**
   ```json
   {
     "business_name": "Sunset Dental Clinic",
     "pain_points": [
       "Website instructs patients to call for appointments",
       "No online booking system detected"
     ]
   }
   ```

3. **Contactable Business**
   ```json
   {
     "business_name": "Green Leaf Spa",
     "website": "https://greenleafspa.com",
     "contact_phone": ["+1-555-6789"],
     "contact_email": ["info@greenleafspa.com"]
   }
   ```

### ❌ Invalid Leads (Now Rejected)

1. **YouTube Videos**
   ```
   Source: https://youtube.com/watch?v=123
   Title: "How to Automate Restaurant Orders"
   ❌ This is educational content, not a business
   ```

2. **Reddit/Quora Posts**
   ```
   Source: https://reddit.com/r/smallbusiness/...
   Title: "How can I improve my SEO?"
   ❌ This is a discussion, not an identifiable business
   ```

3. **Generic Categories**
   ```json
   {
     "business_name": "Small businesses",
     ❌ Not a specific business
   }
   ```

4. **SaaS Competitors**
   ```
   Source: https://whatsapp-bot-saas.com
   Business: "WhatsApp Automation Platform"
   ❌ They SELL the service we offer - competitor, not customer
   ```

---

## Configuration

### Environment Variables

```bash
# Required for LLM
OPENAI_API_KEY=your_key_here
# OR
ANTHROPIC_API_KEY=your_key_here

# Optional: Search APIs (faster, more accurate)
SERPAPI_API_KEY=your_key_here
GOOGLE_MAPS_API_KEY=your_key_here

# Agency Info (for outreach)
AGENCY_NAME="Your Agency"
AGENCY_WEBSITE="https://youragency.com"
SENDER_NAME="Your Name"
SENDER_WHATSAPP="+1-555-1234"
```

### Minimum Score Threshold

```python
# Strict (only best leads)
workflow = LeadWorkflow(min_score=0.7)

# Balanced (default)
workflow = LeadWorkflow(min_score=0.5)

# Lenient (explore more leads)
workflow = LeadWorkflow(min_score=0.4)
```

---

## Best Practices

### 1. Start with Business-Discovery Queries

❌ **Don't:**
```python
queries = [
    "businesses need websites",
    "how to improve SEO",
    "whatsapp bot tutorial"
]
```

✅ **Do:**
```python
queries = [
    "local restaurants Chicago directory contact",
    "dental clinics Los Angeles website phone",
    "fitness studios Miami business listings"
]
```

### 2. Target Specific Locations

✅ **Do:**
```python
queries = [
    "restaurants in Brooklyn New York directory",
    "law firms Boston Massachusetts contact",
    "clinics San Francisco California website"
]
```

### 3. Review Pain Points

Check that pain points are SPECIFIC:

✅ **Good:**
- "Website copyright 2015, non-mobile friendly"
- "Only phone ordering - no online system"
- "Reviews mention difficulty booking appointments"

❌ **Bad:**
- "Restaurant probably needs online ordering"
- "Small businesses could benefit from SEO"
- "Common industry problem"

### 4. Verify Contact Information

Before outreach, verify:
- ✅ Website URL is valid and loads
- ✅ Email addresses are not generic (no noreply@, admin@)
- ✅ Phone numbers are properly formatted

---

## Troubleshooting

### "No leads found"

**Causes:**
1. Search queries too specific → Try broader terms
2. Minimum score too high → Lower `min_score`
3. Target location has few businesses → Expand geography

**Solutions:**
```python
# Broader queries
queries = [
    "local businesses directory contact",
    "restaurants contact information",
]

# Lower threshold
workflow = LeadWorkflow(min_score=0.4)
```

### "Only getting low-quality leads"

**Causes:**
1. Search queries returning articles/discussions
2. Not using business directories
3. Need better filtering

**Solutions:**
```python
# Target business directories
queries = [
    "chamber of commerce member directory",
    "local business association listings",
    "google my business profiles"
]

# Raise threshold
workflow = LeadWorkflow(min_score=0.6)
```

### "Getting content sources (YouTube, Reddit)"

**This should NOT happen** with the new system. If it does:

1. Check that you're using the updated `jobs.py`
2. Review logs for rejection messages
3. Report as a bug

---

## Monitoring & Logging

### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Rejection Reasons

Look for these log messages:
```
❌ REJECTED: Content source - https://youtube.com/...
❌ REJECTED: SaaS/Agency competitor - https://...
❌ REJECTED: Invalid business name 'Small businesses'
❌ REJECTED: No specific pain points
✅ VALID LEAD: Mario's Pizza (score=0.78)
```

---

## Output Files

### `leads_{timestamp}.json`
All qualified and filtered leads

### `outreach_{timestamp}.json`
Generated outreach messages for each lead:
```json
{
  "lead_id": {
    "email_subject": "Subject line",
    "email_body": "Email body...",
    "whatsapp_message": "WhatsApp message...",
    "cold_dm": "LinkedIn/Instagram DM..."
  }
}
```

---

## Next Steps

After generating leads:

1. **Review** high-priority leads manually
2. **Verify** contact information
3. **Personalize** outreach messages
4. **Track** responses and conversion rates
5. **Refine** search queries based on results

---

## Support

For issues or questions:
1. Check `LEAD_VALIDATION_RULES.md` for validation details
2. Review logs for rejection reasons
3. Test with specific search queries
4. Report bugs with example leads

---

## Examples

### Full Workflow Example

```python
import asyncio
from automation.workflows import LeadWorkflow

async def generate_restaurant_leads():
    """Find restaurants in Chicago that need online ordering."""
    
    queries = [
        "restaurants Chicago directory contact phone",
        "local Chicago restaurants website menu",
        "Chicago food delivery restaurants contact",
    ]
    
    workflow = LeadWorkflow(
        search_queries=queries,
        min_score=0.6,
        output_dir="leads_output"
    )
    
    # Run for WhatsApp bot service
    report = await workflow.run(service="whatsapp_bot")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"CHICAGO RESTAURANT LEADS")
    print(f"{'='*60}")
    print(f"Total leads: {report['summary']['filtered_leads']}")
    print(f"High priority: {report['summary']['high_priority']}")
    print(f"Hot leads: {report['summary']['hot_leads']}")
    
    # Show top 3 leads
    for lead in report['leads'][:3]:
        print(f"\n✅ {lead['business_name']}")
        print(f"   Score: {lead['qualification_score']}")
        print(f"   Pain: {lead['pain_points'][0] if lead['pain_points'] else 'N/A'}")
        print(f"   Contact: {lead['website'] or lead['contact_phone']}")
    
    return report

if __name__ == "__main__":
    asyncio.run(generate_restaurant_leads())
```

### Command Line Usage

```bash
# Run all services
python -m automation.workflows

# Run specific service
python -m automation.workflows --service whatsapp_bot

# Custom queries
python -m automation.workflows --queries "restaurants Chicago" "dentists LA"

# Adjust threshold
python -m automation.workflows --min-score 0.7
```

---

## Summary

The updated system ensures:
- ✅ Only real, identifiable businesses
- ✅ Direct evidence of service needs
- ✅ Contactable businesses with verified info
- ❌ No content sources (YouTube, Reddit, etc.)
- ❌ No generic categories
- ❌ No SaaS competitors

**Result:** High-quality leads you can actually reach out to!
