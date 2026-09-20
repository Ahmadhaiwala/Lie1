# Lead Validation Quick Checklist

Use this checklist to manually review leads or understand rejection reasons.

---

## ✅ VALID LEAD CHECKLIST

Before accepting a lead as valid, verify ALL of these:

### 1. Real Business Entity ✓

- [ ] Has specific business name (not generic category)
- [ ] NOT a person's name (Dr. Smith → ❌, Smith Dental → ✅)
- [ ] Can be independently verified
- [ ] Source represents business (not content about it)

**Examples:**
- ✅ "Mario's Pizza Chicago"
- ✅ "Sunset Dental Clinic"
- ❌ "Small businesses"
- ❌ "Dr. Jennifer Mcleod"
- ❌ "Restaurants"

---

### 2. Source Type ✓

- [ ] NOT YouTube, Reddit, Quora, blog
- [ ] NOT SaaS product page
- [ ] NOT competitor/agency
- [ ] IS actual business website or listing

**Auto-reject domains:**
- ❌ youtube.com, reddit.com, quora.com
- ❌ medium.com, /blog/, /article/
- ❌ Sites with "pricing", "free trial", "API docs"

---

### 3. Website Detection ✓

If source_url IS the business website:
- [ ] `website` field populated (extracted from source_url)
- [ ] `website_status` set correctly (not "none")
- [ ] `filter_online_score` reflects QUALITY (not existence)

If business has NO website:
- [ ] `website` field is null/empty
- [ ] `website_status` = "none"
- [ ] `filter_justification` explains why

**Common mistake:**
```
❌ source_url: "https://business.com/about"
   website: ""
   justification: "No web presence"

✅ source_url: "https://business.com/about"
   website: "https://business.com"
   justification: "Website exists with basic issues"
```

---

### 4. Evidence-Based Pain Points ✓

For EACH pain point, verify:
- [ ] Describes SPECIFIC observation
- [ ] NOT generic ("poor SEO", "bad website")
- [ ] NOT assumption ("probably needs", "could benefit")
- [ ] CAN be independently verified

**Valid examples:**
- ✅ "Homepage meta description tag is missing"
- ✅ "Title tag shows 'Home' on 3 pages"
- ✅ "Website copyright says © 2012"
- ✅ "Review states 'waited 4 hours for reply'"

**Invalid examples:**
- ❌ "Poor SEO"
- ❌ "Thin content"
- ❌ "Low ranking"
- ❌ "Could benefit from automation"

---

### 5. Service Match ✓

- [ ] Observed problem matches requested service
- [ ] NOT mapping every issue to SEO
- [ ] Service would actually solve the problem

**Service mapping:**
- No website / Broken website → **website**
- Missing meta tags / No indexing → **seo**
- WhatsApp manual process → **whatsapp_bot**
- No online ordering → **ecommerce**

---

### 6. Contact Information ✓

At least ONE of:
- [ ] Business website URL
- [ ] Business email address
- [ ] Business phone number

**Note:** Contact must be for the BUSINESS, not general info

---

### 7. Qualification Score ✓

- [ ] Score ≥ 0.5 (minimum threshold)
- [ ] Score reflects evidence quality
- [ ] High score (≥0.7) has strong evidence
- [ ] No evidence → score should be <0.5

**Score breakdown:**
- 40% Business identity
- 30% Evidence of need
- 20% Service fit
- 10% Contactability

---

## ❌ REJECTION REASONS

### Common Rejection Points

| Rejection | Reason | Log Message |
|-----------|--------|-------------|
| Content Source | YouTube, Reddit, Quora URL | "❌ REJECTED: Content source" |
| SaaS/Competitor | Pricing page, API docs | "❌ REJECTED: SaaS/Agency competitor" |
| Not Business | LLM classification | "❌ REJECTED: Not a real business" |
| Low Score | score < 0.5 | "❌ REJECTED: Score too low (0.42)" |
| Invalid Name | Generic/person/content | "❌ REJECTED: Invalid business name" |
| No Evidence | No specific pain points | "❌ REJECTED: No specific pain points" |
| No Contact | No website/email/phone | "❌ REJECTED: No contact path" |

---

## 🎯 SCORING GUIDE

### High Quality Lead (0.7 - 1.0)

```
✅ Real business: "Mario's Pizza"
✅ Website: https://mariospizza.com
✅ Pain points:
   - "Website only shows phone for orders"
   - "No online ordering system detected"
   - "Reviews mention 'can't order online'"
✅ Contact: website + phone + email
✅ Evidence: Strong, observable, specific
```

**Score: 0.85**

---

### Medium Quality Lead (0.5 - 0.7)

```
✅ Real business: "Local Gym Fitness"
✅ Website: https://localg ymfitness.com
⚠️ Pain points:
   - "Website last updated 2018"
⚠️ Contact: website only
⚠️ Evidence: Some observable, limited
```

**Score: 0.58**

---

### Low Quality / Rejected (<0.5)

```
❌ Real business: "Dentists in Chicago"
❌ Website: null
❌ Pain points:
   - "Poor online presence"
   - "Could benefit from SEO"
❌ Contact: none
❌ Evidence: Generic assumptions only
```

**Score: 0.25 → REJECTED**

---

## 🔍 QUICK DEBUGGING

### Lead Got Rejected - Why?

**Check logs for:**
```
❌ REJECTED: [REASON] - [URL]
```

**Common fixes:**

| Issue | Fix |
|-------|-----|
| "Content source" | Change search query to find businesses, not articles |
| "Invalid business name" | Ensure LLM extracts actual business entity |
| "No specific pain points" | Need observable evidence, not assumptions |
| "Score too low" | Strengthen evidence or adjust min_score threshold |

---

### Lead Missing Website - Why?

**Check:**
1. Is source_url a business website? → Extract domain
2. Did LLM return website field? → Check LLM response
3. Is website actually missing? → Correct status = "none"

**Fix:**
```python
# Ensure website extraction in _qualify_lead()
from urllib.parse import urlparse
parsed = urlparse(source_url)
if not is_content_source(source_url):
    website = f"{parsed.scheme}://{parsed.netloc}"
```

---

### Pain Points Too Generic - Why?

**Check for banned phrases:**
- "probably", "likely", "could benefit"
- "poor seo", "poor visibility"
- "thin content", "bad structure"

**Solution:**
Make LLM prompts more explicit about evidence requirements.

---

## 💡 TIPS FOR SUCCESS

### 1. Start with Good Search Queries

✅ **Business-discovery:**
- "restaurants [city] directory contact"
- "dentists [city] website phone"
- "local businesses [city] listings"

❌ **Problem-discovery:**
- "businesses need websites"
- "poor seo help"
- "how to improve ranking"

---

### 2. Review First 10 Leads Manually

Check that:
- Business names are specific entities
- Pain points have real evidence
- Websites are correctly detected
- Contact info is valid

---

### 3. Adjust Threshold Based on Volume

```python
# Need high quality only
min_score=0.7  # ~30% of leads

# Balanced
min_score=0.6  # ~50% of leads

# More volume
min_score=0.5  # ~70% of leads
```

---

### 4. Monitor Rejection Patterns

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python -m automation.workflows

# Look for patterns
grep "REJECTED" logs/*.log | sort | uniq -c
```

---

## 📋 MANUAL REVIEW TEMPLATE

For each lead, ask:

1. **Can I find this business on Google?**
   - YES → Continue
   - NO → Investigate or reject

2. **Is the business name the actual entity?**
   - "ABC Clinic" → ✅
   - "Dr. Smith" → ❌

3. **Can I verify each pain point?**
   - Visit website, check claim
   - All verified → ✅
   - Can't verify → Remove or downgrade

4. **Can I contact this business?**
   - Website/email/phone works → ✅
   - No contact method → ❌

5. **Would they actually need our service?**
   - Strong case → ✅
   - Weak/unclear → ⚠️

---

## 🎓 TRAINING EXAMPLES

### Example 1: Perfect Lead ✅

```json
{
  "business_name": "Mario's Pizza Chicago",
  "website": "https://mariospizza.com",
  "website_status": "functional",
  "service_needed": "whatsapp_bot",
  "pain_points": [
    "Website lists 'Order via WhatsApp: +1-312-555-0123'",
    "Google review: 'Waited 3 hours for WhatsApp response'",
    "Business Instagram post: 'Sorry for delayed replies, 100+ orders/day'"
  ],
  "qualification_score": 0.88,
  "contact_phone": ["+1-312-555-0123"],
  "contact_email": ["orders@mariospizza.com"]
}
```

**Why it's perfect:**
- ✅ Specific business name
- ✅ Website correctly identified
- ✅ Three specific, verifiable pain points
- ✅ Strong evidence of WhatsApp usage + pain
- ✅ Multiple contact methods
- ✅ High score justified by evidence

---

### Example 2: Should Be Rejected ❌

```json
{
  "business_name": "Small businesses",
  "website": "",
  "pain_points": [
    "Poor online presence",
    "Could benefit from SEO"
  ],
  "qualification_score": 0.75,
  "source_url": "https://reddit.com/r/smallbusiness"
}
```

**Why it should be rejected:**
- ❌ Generic category, not specific business
- ❌ Source is Reddit (content)
- ❌ Pain points are assumptions
- ❌ No contact information
- ❌ Score inflated despite no evidence

**Would be caught by:**
- Stage 1: Content source rejection
- Stage 4: Invalid business name
- Stage 4: Generic pain points filtered

---

## 📊 SUCCESS METRICS

Track these to measure system quality:

- **Valid Business Rate:** >95% of leads are real businesses
- **Evidence Rate:** >85% of pain points are verifiable
- **Contact Rate:** >90% have valid contact info
- **False Positive Rate:** <5% (content sources, generic names)
- **Conversion Rate:** % of leads that respond to outreach

---

## 🚀 QUICK START

```python
from automation.workflows import LeadWorkflow

# 1. Create workflow
workflow = LeadWorkflow(
    search_queries=[
        "restaurants Chicago directory contact",
        "dentists LA website phone"
    ],
    min_score=0.6
)

# 2. Run
report = await workflow.run()

# 3. Review
for lead in report['leads'][:5]:
    print(f"✓ {lead['business_name']}")
    print(f"  Score: {lead['qualification_score']}")
    print(f"  Evidence: {lead['pain_points'][0]}")
```

---

## 📞 GETTING HELP

**Check Documentation:**
1. `EVIDENCE_BASED_QUALIFICATION.md` - Full evidence rules
2. `VALIDATION_FLOW.md` - Visual diagrams
3. `USAGE_GUIDE.md` - How to use

**Debug Issues:**
1. Enable debug logging
2. Check rejection log messages
3. Review test_validation.py examples

---

**Last Updated:** 2026-09-21  
**Version:** 3.0  
**Status:** Production Ready ✅
