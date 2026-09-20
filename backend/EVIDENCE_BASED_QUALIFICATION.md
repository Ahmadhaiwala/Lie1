# Evidence-Based Lead Qualification

## Core Principle

**NEVER ASSUME. ALWAYS OBSERVE.**

Every pain point must have direct, observable evidence. Industry assumptions are FORBIDDEN.

---

## The Problem: Hallucinated Pain Points

### ❌ WRONG (Assumption-Based)

```json
{
  "business_name": "Newberg Family Dental",
  "service_needed": "seo",
  "pain_points": [
    "Poor SEO",
    "Poor meta descriptions",
    "Thin content"
  ],
  "website": "",
  "filter_justification": "No web presence"
}
```

**Problems:**
1. Pain points are GENERIC industry assumptions
2. Website marked as non-existent when source_url IS the website
3. No actual observation of SEO issues
4. "Dr. Jennifer Mcleod" (person) confused with business name

---

### ✅ RIGHT (Evidence-Based)

```json
{
  "business_name": "Newberg Community Dental",
  "service_needed": "seo",
  "pain_points": [
    "Homepage meta description tag is empty",
    "Title tag shows 'Home' on 3 different pages",
    "Service pages contain less than 100 words each"
  ],
  "website": "https://www.newbergcommunitydental.com",
  "website_status": "basic",
  "filter_justification": "Website exists but has observable SEO deficiencies"
}
```

**Why this is correct:**
1. Pain points are SPECIFIC observations
2. Website correctly extracted from source_url
3. Each issue can be verified
4. Business entity (not person) identified

---

## Evidence Requirements by Service

### SEO Services

#### ✅ VALID EVIDENCE

**Technical Issues (Observable):**
- "Homepage has no title tag"
- "Meta description missing on contact page"
- "Multiple pages share duplicate title 'Home'"
- "No LocalBusiness schema detected in page source"
- "Canonical tags missing on all pages"
- "Images lack alt attributes (checked 10 images)"

**Content Issues (Observable):**
- "Service pages contain 30-50 words each"
- "Blog last updated in 2019"
- "No city name mentioned on any page"
- "Business hours not listed on website"

**Visibility Issues (Stated or Observable):**
- "Business states 'we don't show up on Google'"
- "Searched 'dentist newberg' - business not in top 50"
- "Google My Business profile shows 'needs verification'"
- "Website returns 404 when searched by exact URL"

#### ❌ INVALID (Assumptions)

- "Poor SEO" → Too vague
- "Bad meta descriptions" → Did you see them missing/bad?
- "Thin content" → Which pages? How thin?
- "Low Google ranking" → Did you check?
- "Needs local SEO" → What signals are missing?
- "Weak online presence" → Define "weak" with evidence

---

### Website Development

#### ✅ VALID EVIDENCE

**No Website:**
- "Business profile links to Facebook page only"
- "Website URL returns 404 error"
- "Google search for business name finds no website"
- "Business states 'coming soon' on social media"

**Broken Website:**
- "Homepage displays 'database connection error'"
- "All images show broken image icons"
- "Contact form returns error on submit"
- "Site uses Flash player (deprecated)"

**Outdated Website:**
- "Copyright footer shows '© 2012'"
- "Site uses HTML tables for layout"
- "Not mobile-responsive (tested on iPhone)"
- "Uses frames and animated GIFs"

#### ❌ INVALID (Assumptions)

- "Small business probably needs a website" → No evidence
- "Website looks old" → Define "old" with specifics
- "Could use a redesign" → Based on what?
- "Poor design" → Subjective without examples

---

### WhatsApp Bot Services

#### ✅ VALID EVIDENCE

**WhatsApp Usage (Observable):**
- "Website displays 'Order via WhatsApp: +123456789'"
- "Contact page lists WhatsApp as primary method"
- "Business hours note 'WhatsApp available 9am-5pm'"
- "Menu includes 'Message us on WhatsApp for delivery'"

**Manual Process Pain (Observable):**
- "Reviews mention 'waited 3 hours for WhatsApp response'"
- "Business posts 'overwhelmed with WhatsApp orders'"
- "FAQ says 'please allow 24h for WhatsApp replies'"
- "Instagram story: 'sorry for delayed WhatsApp responses'"

#### ❌ INVALID (Assumptions)

- "Restaurant probably uses WhatsApp" → No evidence
- "Could benefit from automation" → No pain observed
- "High volume business needs bots" → Volume not demonstrated
- "Manual replies are slow" → No proof of manual process

---

## Business Name vs Person Name

### The Rule

**A person is NOT a business.**

#### ❌ WRONG

```json
{
  "business_name": "Dr. Jennifer Mcleod"
}
```

#### ✅ RIGHT

Option 1 - If practice name is known:
```json
{
  "business_name": "Newberg Family Dental",
  "notes": "Contact: Dr. Jennifer Mcleod"
}
```

Option 2 - If only person is identifiable:
```json
{
  "business_name": null,
  "rejection_reason": "Only individual dentist identified, not the practice entity"
}
```

### Detection Pattern

**Person Indicators:**
- Starts with Dr., Mr., Ms., Prof.
- First name + Last name pattern
- No business entity mentioned

**Business Indicators:**
- Business structure words (Clinic, Associates, Group, LLC, Inc.)
- Location in name (Chicago Dental, Newberg Family...)
- Service description (Family Dental, Legal Services...)

---

## Website Existence Rules

### Rule 1: Source URL = Business Website

If `source_url` points to the business's own website:

```python
source_url = "https://www.businessname.com/about"
```

Then:

```json
{
  "website": "https://www.businessname.com",
  "website_status": "basic|functional|strong",
  "filter_justification": "Website exists but has [specific issues]"
}
```

**NEVER:**
```json
{
  "website": "",
  "filter_justification": "No web presence"
}
```

### Rule 2: Website Status Classification

| Status | Definition | Example |
|--------|------------|---------|
| **none** | No website found anywhere | Facebook-only business |
| **basic** | Website exists with major issues | 404 pages, broken, under construction |
| **functional** | Website works, provides basic info | Contact info, services listed, works |
| **strong** | Professional, modern, full-featured | Online booking, e-commerce, blog |
| **unknown** | Cannot determine from available data | Insufficient information |

### Rule 3: Online Presence Score

**When website exists:**

- `filter_online_score` should NOT be 5.0 (max deficiency)
- Score reflects website QUALITY, not existence

| Website Status | Online Score Range |
|----------------|-------------------|
| none | 9-10 (major deficiency) |
| basic | 6-8 (significant issues) |
| functional | 3-5 (minor improvements needed) |
| strong | 0-2 (minimal deficiency) |

---

## Qualification Scoring Formula

### Components (Total = 1.0)

1. **Business Identity Confidence (40%)**
   - Is this a real, identifiable business entity?
   - Can we distinguish it from content/person/generic category?
   - Is the business name specific and verifiable?

2. **Evidence of Need (30%)**
   - Do we have OBSERVED pain points?
   - Are pain points specific and verifiable?
   - Is evidence direct or indirect?

3. **Service Fit (20%)**
   - Does the observed problem match our service?
   - Would our service actually solve the problem?
   - Is timing right (immediate need vs. future)?

4. **Contactability (10%)**
   - Can we reach this business?
   - Do we have verified contact info?
   - Is decision-maker identifiable?

### Scoring Examples

#### Example 1: Real Business, No Evidence

```
Business Identity: 1.0 (clear business entity)
Evidence of Need:  0.2 (no observed issues)
Service Fit:       0.3 (assumption-based)
Contactability:    0.8 (phone + email)

Total: (0.4 × 1.0) + (0.3 × 0.2) + (0.2 × 0.3) + (0.1 × 0.8)
     = 0.4 + 0.06 + 0.06 + 0.08
     = 0.60 → Moderate confidence, but weak evidence
```

**Interpretation:** Real business, but we can't demonstrate they need our service.

#### Example 2: Real Business, Strong Evidence

```
Business Identity: 1.0 (clear business entity)
Evidence of Need:  0.9 (multiple observed issues)
Service Fit:       0.9 (perfect match)
Contactability:    1.0 (website + email + phone)

Total: (0.4 × 1.0) + (0.3 × 0.9) + (0.2 × 0.9) + (0.1 × 1.0)
     = 0.4 + 0.27 + 0.18 + 0.1
     = 0.95 → High confidence, strong evidence
```

**Interpretation:** Excellent lead with verified needs.

#### Example 3: Weak Business Identity

```
Business Identity: 0.4 (might be a person or category)
Evidence of Need:  0.7 (some issues observed)
Service Fit:       0.6 (moderate fit)
Contactability:    0.5 (phone only)

Total: (0.4 × 0.4) + (0.3 × 0.7) + (0.2 × 0.6) + (0.1 × 0.5)
     = 0.16 + 0.21 + 0.12 + 0.05
     = 0.54 → Low-medium confidence
```

**Interpretation:** Unclear if this is a real business entity.

---

## Required Final Checks

Before returning ANY lead, run this checklist:

### ✅ BUSINESS CHECK

**Question:** Can I identify the actual business entity?

- [ ] Business name is specific (not generic category)
- [ ] Business name is NOT a person's name
- [ ] Business can be independently verified
- [ ] Source represents the business (not content about it)

**Action:** If NO → REJECT

---

### ✅ WEBSITE CHECK

**Question:** Does the business have a website?

If YES:
- [ ] `website` field is populated with URL
- [ ] `website_status` is "basic", "functional", or "strong"
- [ ] `filter_online_score` reflects website QUALITY, not existence

If NO:
- [ ] `website` field is null or empty
- [ ] `website_status` is "none"
- [ ] `filter_justification` explains no website found

**Action:** Never say "no web presence" when website exists

---

### ✅ PAIN POINT CHECK

**Question:** Can I point to concrete evidence for each pain point?

For EACH pain point, verify:
- [ ] It describes a SPECIFIC observation
- [ ] It's NOT an industry assumption
- [ ] It can be independently verified
- [ ] It doesn't use vague terms (poor, bad, weak, low)

**Action:** Remove pain points without evidence

---

### ✅ SERVICE CHECK

**Question:** Does the observed problem match the requested service?

- [ ] Website problem → website service (NOT seo)
- [ ] Missing meta tags → SEO service
- [ ] WhatsApp manual process → WhatsApp bot service
- [ ] No ecommerce → ecommerce service

**Action:** If mismatch → adjust service or reject

---

### ✅ CONTACT CHECK

**Question:** Is there a real, verifiable way to contact this business?

At least ONE of:
- [ ] Business website URL
- [ ] Business email address
- [ ] Business phone number

**Action:** If NONE → REJECT

---

### ✅ HALLUCINATION CHECK

**Question:** Did I infer anything that wasn't actually observed?

Review ALL fields:
- [ ] Business name came from source (not invented)
- [ ] Pain points were observed (not assumed)
- [ ] Contact info was found (not guessed)
- [ ] Scores reflect evidence (not industry averages)

**Action:** If ANY hallucination → Remove it

---

## Implementation Examples

### Example 1: SEO Lead (Correct)

**Source Content:**
```
Newberg Family Dental
615 E 2nd St, Newberg, OR
Phone: (503) 538-7717
Website: www.newbergcommunitydental.com

[Inspected website shows:]
- <title>Home</title> on multiple pages
- Meta description missing
- Only 2 pages indexed by Google
```

**Output:**
```json
{
  "business_name": "Newberg Family Dental",
  "website": "https://www.newbergcommunitydental.com",
  "website_status": "basic",
  "service_needed": "seo",
  "pain_points": [
    "Title tag shows 'Home' on 3 different pages",
    "Meta description tag missing on all pages",
    "Only 2 pages indexed by Google (site: search)"
  ],
  "qualification_score": 0.78,
  "filter_online_score": 6.5,
  "filter_justification": "Website exists but has observable SEO deficiencies"
}
```

---

### Example 2: WhatsApp Bot Lead (Correct)

**Source Content:**
```
Mario's Pizza Chicago
Order via WhatsApp: +1-312-555-0123

Recent review: "Waited 4 hours for reply to my WhatsApp order"
Business post: "Sorry for delays, handling 100+ orders daily"
```

**Output:**
```json
{
  "business_name": "Mario's Pizza Chicago",
  "service_needed": "whatsapp_bot",
  "pain_points": [
    "Business lists WhatsApp as primary ordering method: +1-312-555-0123",
    "Customer review states '4 hour wait for WhatsApp response'",
    "Business publicly mentions '100+ daily orders' causing delays"
  ],
  "qualification_score": 0.85,
  "evidence": "Direct observation of WhatsApp usage + customer complaint + business acknowledgment of volume issue"
}
```

---

### Example 3: No Website Lead (Correct)

**Source Content:**
```
Green Leaf Spa
Facebook: facebook.com/greenleafspa
No website available - contact us on Facebook
```

**Output:**
```json
{
  "business_name": "Green Leaf Spa",
  "website": null,
  "website_status": "none",
  "service_needed": "website",
  "pain_points": [
    "Business explicitly states 'No website available'",
    "Only contactable via Facebook page",
    "No professional web presence for service booking"
  ],
  "qualification_score": 0.82,
  "filter_online_score": 9.5,
  "filter_justification": "No website exists - Facebook-only presence"
}
```

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Industry Assumptions

**Wrong:**
> "Dentists typically need SEO, so this dental practice needs SEO."

**Right:**
> "This dental practice has missing meta tags and no indexed pages, therefore needs SEO."

---

### ❌ Mistake 2: Vague Pain Points

**Wrong:**
> "Poor online presence", "Weak SEO", "Bad website"

**Right:**
> "Homepage meta description missing", "Site not mobile-responsive (tested)", "Copyright dated 2015"

---

### ❌ Mistake 3: Person as Business

**Wrong:**
> business_name: "Dr. John Smith"

**Right:**
> business_name: "Smith Family Dental" or null (if practice unknown)

---

### ❌ Mistake 4: Missing Website When It Exists

**Wrong:**
> source_url: "https://business.com/about"
> website: ""
> filter_justification: "No web presence"

**Right:**
> source_url: "https://business.com/about"
> website: "https://business.com"
> filter_justification: "Website exists with observable issues"

---

## Summary

### Golden Rules

1. **OBSERVE, DON'T ASSUME**
   - Every pain point needs evidence
   - Industry norms are not evidence

2. **BUSINESS vs PERSON**
   - Identify the business entity
   - Don't confuse contacts with businesses

3. **WEBSITE EXISTS?**
   - Extract from source_url when appropriate
   - Never say "no presence" when website exists

4. **SPECIFIC, NOT VAGUE**
   - "Missing meta tag" ✅
   - "Poor SEO" ❌

5. **VERIFY EVERYTHING**
   - Can pain point be independently checked?
   - Is business name verifiable?
   - Is contact info real?

**Result:** High-quality, evidence-based leads that sales teams can trust and act on.
