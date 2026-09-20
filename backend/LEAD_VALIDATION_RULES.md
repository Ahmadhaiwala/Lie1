# Lead Validation Rules

## Overview

This document explains the multi-stage validation system that ensures only **REAL, SPECIFIC BUSINESSES** are identified as leads, not articles, tutorials, or generic discussions.

---

## The Core Problem

Early versions of the system produced invalid leads like:
- ❌ YouTube videos ("How to Automate Clinic Appointments")
- ❌ Reddit posts asking questions
- ❌ Quora discussions
- ❌ SaaS companies offering the same service
- ❌ Generic categories ("Small businesses", "Restaurants")
- ❌ Blog articles about problems

These are **NOT** leads because:
1. They don't represent a specific, contactable business
2. They're content ABOUT a problem, not evidence of a customer need
3. The source URL is not the business itself

---

## Multi-Stage Validation System

### Stage 1: Source Type Validation (Pre-LLM)

**Before** sending content to the LLM, we check:

#### 1.1 Content Source Detection
Reject if URL contains:
- `youtube.com`, `youtu.be`
- `reddit.com`, `redd.it`
- `quora.com`
- `medium.com`
- `facebook.com/watch`, `instagram.com/tv`
- `tiktok.com`
- `linkedin.com/pulse` (articles, not business profiles)
- `/blog/`, `/article/`, `/post/`, `/tutorial/`
- `/how-to`, `/guide`, `/tips`

**Why?** These are content platforms, not business websites.

#### 1.2 SaaS/Agency Detection
Reject if content contains 3+ indicators of:
- SaaS providers: "pricing", "free trial", "plans & pricing", "API docs"
- Agencies: "we build", "our services", "portfolio", "hire us"

**Why?** These are competitors, not potential customers.

---

### Stage 2: Business Identity Validation (LLM)

The LLM receives enhanced system prompts with strict rules:

#### 2.1 Business Name Requirements
✅ **Valid:**
- "ABC Dental Clinic"
- "Royal Spice Restaurant"
- "John's Auto Repair"
- "XYZ Fitness Studio"

❌ **Invalid:**
- "Small businesses" (generic category)
- "Restaurants" (plural category)
- "How to build a WhatsApp bot" (article title)
- "YouTube" (platform name)
- "null", "unknown"

#### 2.2 Source Type Classification
LLM must classify each source as:
- `actual_business` ✅
- `content` ❌
- `saas_provider` ❌
- `generic_discussion` ❌

Only `actual_business` passes validation.

#### 2.3 Service Need Evidence
Must be **DIRECT, OBSERVABLE EVIDENCE**, not assumptions:

✅ **Strong Evidence:**
- "Restaurant website only shows phone number for orders - no online ordering"
- "Clinic website says 'Call reception to schedule appointments'"
- "Website copyright 2015, broken images, non-mobile friendly"
- "Business has WhatsApp number but no automated responses"

❌ **Weak/Generic Assumptions:**
- "Restaurants probably need WhatsApp bots"
- "Small businesses could benefit from SEO"
- "Clinics often need appointment automation"

Generic assumptions are **filtered out** from pain points.

---

### Stage 3: Validation Checks

After LLM response, we verify:

1. **is_real_business** = `true`
2. **source_type** = `"actual_business"`
3. **score** ≥ 0.5 (minimum threshold)
4. **business_name** passes `_is_valid_business_name()` check
5. **pain_points** exist and are specific (not generic)

If ANY check fails → Reject.

---

### Stage 4: Contact Path Verification

Must have at least ONE of:
- Business website URL
- Business email address
- Business phone number

**Why?** A lead is worthless if you can't contact them.

---

## Scoring Guidelines

The LLM is instructed to score based on BOTH business identity AND service need:

| Score Range | Meaning |
|-------------|---------|
| 0.0 - 0.2 | Not a business / Pure content |
| 0.2 - 0.4 | Might be a business but no clear service need |
| 0.4 - 0.6 | Identifiable business, weak/indirect need signals |
| 0.6 - 0.8 | Clear business + meaningful evidence of service need |
| 0.8 - 1.0 | Specific business + strong direct evidence + verified contact |

Minimum passing score: **0.5**

---

## Search Query Strategy

### ❌ OLD APPROACH (Problem-Focused)
```
"restaurants need whatsapp bot"
"how restaurants lose orders"
"small business SEO problems"
```
**Result:** Returns articles, tutorials, discussions - NOT businesses.

### ✅ NEW APPROACH (Business-Discovery)
```
"local restaurants directory contact phone website"
"businesses whatsapp contact directory"
"local business listings website contact"
"dentists website location phone hours"
```
**Result:** Returns actual business listings, directories, and business websites.

---

## Example Validation Flow

### ❌ Invalid Lead (Rejected)

**Source:** `https://www.youtube.com/watch?v=sjO9Xtdmudc`  
**Title:** "Smart WhatsApp Order Assistant for Restaurants"

**Validation:**
1. ❌ **Stage 1:** Content source detected (youtube.com)
2. **Result:** REJECTED before LLM call
3. **Reason:** YouTube video is educational content, not a business

---

### ❌ Invalid Lead (Rejected)

**Source:** `https://www.reddit.com/r/smallbusiness/comments/...`  
**Title:** "How can a small business improve its google ranking"

**Validation:**
1. ❌ **Stage 1:** Content source detected (reddit.com)
2. **Result:** REJECTED before LLM call
3. **Reason:** Reddit post is a discussion, not a business

---

### ❌ Invalid Lead (Rejected)

**Source:** `https://olaclick.com/en/orders-by-whatsapp/`  
**Business Name:** "Olaclick"

**Validation:**
1. ✅ **Stage 1:** Not a content source
2. ❌ **Stage 1:** SaaS provider detected (>3 indicators: "free trial", "sign up", "pricing")
3. **Result:** REJECTED before LLM call
4. **Reason:** SaaS company offering WhatsApp ordering - competitor, not customer

---

### ✅ Valid Lead (Accepted)

**Source:** `https://royalspicerestaurant.com/contact`  
**Business Name:** "Royal Spice Restaurant"

**Validation:**
1. ✅ **Stage 1:** Not content, not SaaS
2. ✅ **Stage 2:** LLM confirms real business
3. ✅ **Stage 2:** source_type = "actual_business"
4. ✅ **Stage 2:** Direct evidence: "Website only shows phone number for orders"
5. ✅ **Stage 3:** Score = 0.75, valid business name
6. ✅ **Stage 4:** Contact: website + phone number
7. **Result:** ✅ ACCEPTED as valid lead

---

## Implementation Files

### Modified Files:
1. **`backend/automation/jobs.py`**
   - Added `_is_content_source()` method
   - Added `_is_saas_or_agency()` method
   - Enhanced `_is_valid_business_name()` with comprehensive validation
   - Rewrote `_qualify_lead()` with 5-stage validation
   - Updated search queries to be business-discovery focused
   - Added filtering to `_scrape_search_results()` and `_run_with_search_api()`

### Key Methods:
- `_is_content_source(url)` - Detects YouTube, Reddit, Quora, blogs, etc.
- `_is_saas_or_agency(url, name, content)` - Detects competitors
- `_is_valid_business_name(name)` - Validates business names
- `_qualify_lead(content, url)` - Multi-stage validation pipeline

---

## Testing the New System

### Manual Test
```python
from automation.jobs import WebsiteLeadJob, WhatsAppBotLeadJob, SEOLeadJob

# Test with custom queries
job = WebsiteLeadJob(custom_queries=[
    "dentists local area website phone"
])
result = await job.run()

# Check results
for lead in result.leads:
    print(f"✅ {lead.business_name}")
    print(f"   URL: {lead.source_url}")
    print(f"   Score: {lead.qualification_score}")
    print(f"   Pain Points: {lead.pain_points}")
```

### What to Expect
- ✅ Fewer total leads (quality over quantity)
- ✅ Each lead has a specific business name
- ✅ Each lead has contactable information
- ✅ Pain points are specific and evidence-based
- ❌ No YouTube videos, Reddit posts, or Quora questions
- ❌ No generic category names as "businesses"
- ❌ No articles or tutorials masquerading as leads

---

## Future Improvements

1. **Google Maps API Integration**
   - Directly query Google Business Profile listings
   - Get verified business data with photos, reviews, hours

2. **Business Directory APIs**
   - Yelp Fusion API
   - Yellow Pages API
   - Local chamber of commerce listings

3. **Website Technical Analysis**
   - Automated technical SEO audit
   - Mobile-friendliness check
   - Page speed analysis
   - Automated evidence extraction

4. **Social Media Verification**
   - Check if business has only social media (no website)
   - Verify business activity and engagement
   - Extract business hours, menu, services

---

## Summary

The new validation system ensures that:

1. ✅ Every lead is a **REAL, SPECIFIC BUSINESS**
2. ✅ Every lead has **DIRECT EVIDENCE** of service need
3. ✅ Every lead is **CONTACTABLE** (website, email, or phone)
4. ❌ Content, discussions, and articles are **REJECTED**
5. ❌ SaaS competitors are **REJECTED**
6. ❌ Generic assumptions are **FILTERED OUT**

**Result:** High-quality, actionable B2B leads that sales teams can actually use.
