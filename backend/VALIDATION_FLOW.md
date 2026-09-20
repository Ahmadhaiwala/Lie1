# Lead Validation Flow - Visual Guide

## Complete Validation Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     SEARCH & DISCOVERY                          │
│                                                                 │
│  Search Query: "restaurants Chicago directory contact"         │
│         ↓                                                       │
│  Web Search / API Results                                      │
│         ↓                                                       │
│  URLs: [url1, url2, url3, ...]                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    STAGE 1: PRE-FILTERING                       │
│                    (Before LLM / Crawler)                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────────────┐
                    │ Content Source? │
                    │  YouTube, Reddit│
                    │  Quora, Blogs   │
                    └────────┬────────┘
                             │
                    YES ←────┴────→ NO
                     │              │
                     ↓              ↓
            ┌────────────────┐    ┌──────────────────┐
            │ ❌ REJECTED    │    │ SaaS/Competitor? │
            │                │    └────────┬─────────┘
            │ Reason:        │             │
            │ Content source │    YES ←────┴────→ NO
            └────────────────┘     │              │
                                   ↓              ↓
                          ┌────────────────┐    ┌────────────────┐
                          │ ❌ REJECTED    │    │ ✅ PROCEED     │
                          │                │    │                │
                          │ Reason:        │    │ To Stage 2     │
                          │ Competitor     │    └────────┬───────┘
                          └────────────────┘             │
                                                         ↓
┌─────────────────────────────────────────────────────────────────┐
│              STAGE 2: CONTENT CRAWLING/RETRIEVAL                │
│                                                                 │
│  - Fetch page content                                           │
│  - Extract text                                                 │
│  - Prepare for LLM analysis                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│           STAGE 3: LLM BUSINESS IDENTITY VALIDATION             │
│                                                                 │
│  Enhanced System Prompt:                                        │
│  ┌──────────────────────────────────────────────────┐          │
│  │ • Reject content sources                         │          │
│  │ • Require specific business name                 │          │
│  │ • Require direct evidence (not assumptions)      │          │
│  │ • Classify source type                           │          │
│  │ • Score based on identity + need                 │          │
│  └──────────────────────────────────────────────────┘          │
│                                                                 │
│  LLM Response Required Fields:                                  │
│  ┌──────────────────────────────────────────────────┐          │
│  │ {                                                │          │
│  │   "is_real_business": boolean,                   │          │
│  │   "source_type": "actual_business"|"content"|... │          │
│  │   "business_name": "Specific Name or null",      │          │
│  │   "website": "URL or null",                      │          │
│  │   "score": 0.0-1.0,                              │          │
│  │   "pain_points": ["specific evidence"],          │          │
│  │   "evidence": "direct observation"               │          │
│  │ }                                                │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              STAGE 4: POST-LLM VALIDATION CHECKS                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                   ┌──────────────────────┐
                   │ is_real_business =   │
                   │       true?          │
                   └──────────┬───────────┘
                              │
                     NO ←─────┴─────→ YES
                      │              │
                      ↓              ↓
             ┌────────────────┐   ┌─────────────────────┐
             │ ❌ REJECTED    │   │ source_type =       │
             │                │   │ "actual_business"?  │
             │ Reason:        │   └──────────┬──────────┘
             │ Not a business │              │
             └────────────────┘     NO ←─────┴─────→ YES
                                     │              │
                                     ↓              ↓
                            ┌────────────────┐   ┌──────────────┐
                            │ ❌ REJECTED    │   │ score >= 0.5?│
                            │                │   └──────┬───────┘
                            │ Reason: Content│          │
                            │ or generic     │   NO ←───┴───→ YES
                            └────────────────┘    │          │
                                                  ↓          ↓
                                         ┌─────────────┐  ┌────────────────────┐
                                         │ ❌ REJECTED │  │ Valid business     │
                                         │             │  │ name check?        │
                                         │ Reason:     │  └─────────┬──────────┘
                                         │ Score low   │            │
                                         └─────────────┘   NO ←─────┴─────→ YES
                                                            │              │
                                                            ↓              ↓
                                                   ┌─────────────┐  ┌────────────────┐
                                                   │ ❌ REJECTED │  │ Specific pain  │
                                                   │             │  │ points exist?  │
                                                   │ Reason:     │  └────────┬───────┘
                                                   │ Invalid name│           │
                                                   └─────────────┘  NO ←─────┴─────→ YES
                                                                     │              │
                                                                     ↓              ↓
                                                            ┌─────────────┐  ┌──────────┐
                                                            │ ❌ REJECTED │  │ ✅ PASS  │
                                                            │             │  │          │
                                                            │ Reason: No  │  │ To Stage │
                                                            │ evidence    │  │    5     │
                                                            └─────────────┘  └────┬─────┘
                                                                                  │
                                                                                  ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                     STAGE 5: CONTACT PATH VERIFICATION                              │
│                                                                                     │
│  Extract Contact Information:                                                       │
│  - Business website URL                                                             │
│  - Email addresses                                                                  │
│  - Phone numbers                                                                    │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        ↓
                           ┌────────────────────────────┐
                           │ Has at least ONE contact   │
                           │ method?                    │
                           │ (website OR email OR phone)│
                           └──────────────┬─────────────┘
                                          │
                                 NO ←─────┴─────→ YES
                                  │              │
                                  ↓              ↓
                         ┌─────────────────┐  ┌────────────────┐
                         │ ❌ REJECTED     │  │ ✅ VALID LEAD  │
                         │                 │  │                │
                         │ Reason:         │  │ Create Lead    │
                         │ No contact path │  │ Object         │
                         └─────────────────┘  └────────┬───────┘
                                                       │
                                                       ↓
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            LEAD OBJECT CREATED                                      │
│                                                                                     │
│  {                                                                                  │
│    "id": "uuid",                                                                    │
│    "business_name": "Mario's Pizza Chicago",                                        │
│    "source_url": "https://mariospizzachicago.com",                                  │
│    "service_needed": "whatsapp_bot",                                                │
│    "contact_email": ["contact@mariospizza.com"],                                    │
│    "contact_phone": ["+1-312-555-0123"],                                            │
│    "website": "https://mariospizzachicago.com",                                     │
│    "location": "Chicago, IL",                                                       │
│    "industry": "Restaurant",                                                        │
│    "pain_points": [                                                                 │
│      "Website only shows phone number for orders",                                  │
│      "No online ordering system detected"                                           │
│    ],                                                                               │
│    "qualification_score": 0.76                                                      │
│  }                                                                                  │
│                                                                                     │
│  ✅ LOGGED: "VALID LEAD: Mario's Pizza Chicago (score=0.76)"                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                        ↓
                           ┌────────────────────────┐
                           │  Continue to Business  │
                           │  Filter & Outreach     │
                           └────────────────────────┘
```

---

## Rejection Points Summary

### 🚫 Rejection Point 1: Content Source Detection
**Location:** Stage 1 (Pre-LLM)  
**Method:** `_is_content_source()`  
**Triggers:**
- YouTube, Reddit, Quora URLs
- Blog posts, articles, tutorials
- Social media content URLs

**Log Message:**
```
❌ REJECTED: Content source - https://youtube.com/watch?v=...
```

---

### 🚫 Rejection Point 2: SaaS/Competitor Detection
**Location:** Stage 1 (Pre-LLM)  
**Method:** `_is_saas_or_agency()`  
**Triggers:**
- 3+ SaaS indicators (pricing, trial, subscribe)
- 3+ Agency indicators (we build, portfolio, hire us)

**Log Message:**
```
❌ REJECTED: SaaS/Agency competitor - https://whatsapp-bot-saas.com
```

---

### 🚫 Rejection Point 3: Not a Real Business
**Location:** Stage 4 (Post-LLM)  
**LLM Field:** `is_real_business = false`  
**Triggers:**
- LLM determines source is not a business
- Generic discussion or question

**Log Message:**
```
❌ REJECTED: Not a real business - https://...
```

---

### 🚫 Rejection Point 4: Wrong Source Type
**Location:** Stage 4 (Post-LLM)  
**LLM Field:** `source_type != "actual_business"`  
**Triggers:**
- source_type = "content"
- source_type = "saas_provider"
- source_type = "generic_discussion"

**Log Message:**
```
❌ REJECTED: LLM classified as content - https://...
```

---

### 🚫 Rejection Point 5: Score Too Low
**Location:** Stage 4 (Post-LLM)  
**Condition:** `score < 0.5`  
**Triggers:**
- Weak evidence of service need
- Uncertain business identification
- Low confidence

**Log Message:**
```
❌ REJECTED: Score too low (0.42) - https://...
```

---

### 🚫 Rejection Point 6: Invalid Business Name
**Location:** Stage 4 (Post-LLM)  
**Method:** `_is_valid_business_name()`  
**Triggers:**
- Generic category ("Restaurants", "Small businesses")
- Content indicator ("How to...", "Best way...")
- Platform name ("YouTube", "Reddit")
- Null or empty

**Log Message:**
```
❌ REJECTED: Invalid business name 'Small businesses' - https://...
```

---

### 🚫 Rejection Point 7: No Specific Pain Points
**Location:** Stage 4 (Post-LLM)  
**Condition:** Pain points empty or all generic  
**Triggers:**
- All pain points contain "probably", "could", "may need"
- No pain points provided by LLM

**Log Message:**
```
❌ REJECTED: No specific pain points - https://...
```

---

### 🚫 Rejection Point 8: No Contact Path
**Location:** Stage 5 (Contact Extraction)  
**Condition:** `!(website OR email OR phone)`  
**Triggers:**
- No website URL found
- No email addresses found
- No phone numbers found

**Log Message:**
```
❌ REJECTED: No contact path - https://...
```

---

## Success Path

```
✅ Stage 1: Not content, not competitor
          ↓
✅ Stage 2: Content successfully retrieved
          ↓
✅ Stage 3: LLM returns structured validation
          ↓
✅ Stage 4: All checks pass
          ↓
✅ Stage 5: Contact information found
          ↓
✅ VALID LEAD CREATED
```

**Log Message:**
```
✅ VALID LEAD: Mario's Pizza Chicago (score=0.76) - https://mariospizzachicago.com
```

---

## Example Trace: Valid Lead

```
[DEBUG] Processing URL: https://mariospizzachicago.com
[DEBUG] ✅ Stage 1: Not a content source
[DEBUG] ✅ Stage 1: Not a SaaS/competitor (1 indicators)
[INFO]  Sending to LLM for qualification...
[DEBUG] ✅ Stage 3: LLM returned is_real_business=true
[DEBUG] ✅ Stage 3: source_type="actual_business"
[DEBUG] ✅ Stage 4: Score=0.76 (>= 0.5)
[DEBUG] ✅ Stage 4: Valid business name "Mario's Pizza Chicago"
[DEBUG] ✅ Stage 4: 2 specific pain points found
[INFO]  Extracting contact information...
[DEBUG] ✅ Stage 5: Found website: https://mariospizzachicago.com
[DEBUG] ✅ Stage 5: Found phone: +1-312-555-0123
[DEBUG] ✅ Stage 5: Found email: contact@mariospizza.com
[INFO]  ✅ VALID LEAD: Mario's Pizza Chicago (score=0.76) - https://mariospizzachicago.com
```

---

## Example Trace: Rejected (YouTube)

```
[DEBUG] Processing URL: https://youtube.com/watch?v=abc123
[DEBUG] ❌ Stage 1: Content source detected (youtube.com)
[INFO]  ❌ REJECTED: Content source - https://youtube.com/watch?v=abc123
```

---

## Example Trace: Rejected (Generic Name)

```
[DEBUG] Processing URL: https://smallbusiness-tips.com/seo-guide
[DEBUG] ✅ Stage 1: Not a content source
[DEBUG] ✅ Stage 1: Not a SaaS/competitor
[INFO]  Sending to LLM for qualification...
[DEBUG] ✅ Stage 3: LLM returned is_real_business=true
[DEBUG] ✅ Stage 3: source_type="actual_business"
[DEBUG] ✅ Stage 4: Score=0.65 (>= 0.5)
[DEBUG] ❌ Stage 4: Invalid business name 'Small businesses'
[INFO]  ❌ REJECTED: Invalid business name 'Small businesses' - https://...
```

---

## Performance Metrics

### Efficiency Gains

```
┌──────────────────────────────────────────────────────────────┐
│                    Before Optimization                       │
├──────────────────────────────────────────────────────────────┤
│  100 URLs                                                    │
│    ↓ (all processed)                                         │
│  100 LLM calls                                               │
│    ↓                                                         │
│  40 valid leads + 60 invalid (content sources, etc.)        │
│                                                              │
│  Cost: 100 LLM calls                                         │
│  Quality: 40% valid                                          │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                     After Optimization                       │
├──────────────────────────────────────────────────────────────┤
│  100 URLs                                                    │
│    ↓ (Stage 1 filtering)                                     │
│  60 URLs remaining (40 content sources rejected)            │
│    ↓                                                         │
│  60 LLM calls                                                │
│    ↓ (Stage 4 validation)                                    │
│  45 pass validation + 15 fail                                │
│    ↓ (Stage 5 contact verification)                          │
│  40 have contact info + 5 don't                              │
│    ↓                                                         │
│  40 valid leads                                              │
│                                                              │
│  Cost: 60 LLM calls (-40%)                                   │
│  Quality: 67% valid (+67% efficiency)                        │
└──────────────────────────────────────────────────────────────┘
```

---

## Summary

**5 Stages → 8 Rejection Points → 1 Success Path**

- **Stage 1:** Pre-filtering (content & competitors) → 2 rejection points
- **Stage 2:** Content retrieval
- **Stage 3:** LLM validation with enhanced prompts
- **Stage 4:** Post-LLM validation → 5 rejection points
- **Stage 5:** Contact verification → 1 rejection point

**Result:** Only REAL, SPECIFIC, CONTACTABLE BUSINESSES become leads.
