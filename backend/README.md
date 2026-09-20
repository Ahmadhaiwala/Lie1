# AI Sales Intelligence & Lead Research Automation

An automated sales-research platform that turns a natural-language sales objective into a complete lead-discovery and research workflow.

Instead of manually searching for businesses, opening websites, researching their services, identifying potential problems, and writing outreach messages, the system automatically performs the research pipeline.

```text
Natural Language Request
        ↓
Intent Understanding
        ↓
Research Planning
        ↓
Location & Business Discovery
        ↓
Website Resolution
        ↓
Web Crawling (Crawl4AI)
        ↓
Evidence Extraction
        ↓
Opportunity Detection
        ↓
Lead Qualification
        ↓
Personalized Outreach
```

---

## 1. Problem

Traditional lead generation requires a lot of manual work.

A salesperson may need to:

1. Search for businesses in a specific area.
2. Find their websites.
3. Open multiple pages.
4. Understand what the business offers.
5. Check whether they already use certain technologies.
6. Identify possible business problems.
7. Decide whether the business could benefit from a service.
8. Research contact information.
9. Write a personalized message.

This project automates that workflow.

For example, a user can enter:

> Find gyms near me that might need an automated membership lead system.

The system transforms that request into a structured research task and executes the workflow automatically.

---

# 2. Core Idea

The platform separates **discovery**, **crawling**, **evidence collection**, and **reasoning**.

Crawl4AI is used as the web-research layer rather than being treated as the entire sales system.

```text
                    ┌──────────────────┐
                    │      USER        │
                    │ Natural Language │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │  Intent Parser   │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Research Planner │
                    └────────┬─────────┘
                             ↓
              ┌──────────────┴──────────────┐
              ↓                             ↓
      Location Resolver              Service Profile
              ↓                             ↓
      Business Discovery                     │
              │                             │
              └──────────────┬──────────────┘
                             ↓
                    ┌──────────────────┐
                    │ Website Resolver │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │     Crawl4AI     │
                    │  Public Web Data │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Evidence Engine  │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Opportunity      │
                    │ Engine           │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Lead Generation  │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Outreach Draft   │
                    └──────────────────┘
```

---

# 3. Example

### User request

```text
Find restaurants within 10 km of me
that could benefit from online ordering.
```

### Step 1 — Intent extraction

The system converts the request into structured intent:

```json
{
  "intent": "find_potential_customers",
  "business_types": [
    "restaurant"
  ],
  "location": {
    "source": "user_location",
    "radius_km": 10
  },
  "target_service": {
    "name": "online_ordering_system",
    "capabilities": [
      "online_menu",
      "online_ordering",
      "digital_payment"
    ]
  }
}
```

---

### Step 2 — Business discovery

The system discovers businesses matching the criteria.

```text
User Location
      ↓
Business Discovery
      ↓
Restaurant A
Restaurant B
Restaurant C
Restaurant D
...
```

Potential discovery sources can include:

* Business/Places APIs
* OpenStreetMap
* Search APIs
* Other permitted public business directories

---

### Step 3 — Website resolution

Each business is resolved to a website.

```json
{
  "business": "Restaurant A",
  "website": "https://example.com"
}
```

Businesses without usable web presence can be handled separately.

---

### Step 4 — Crawl4AI research

Crawl4AI researches the publicly accessible website.

Potential pages:

```text
/
├── about
├── menu
├── services
├── ordering
├── contact
├── pricing
├── reservation
└── blog
```

The crawler produces clean content that can be processed by the intelligence layer.

---

# 4. Evidence First

The system should distinguish between **observed facts** and **AI-generated inferences**.

Instead of storing:

```text
Restaurant A needs an ordering system.
```

the system stores evidence:

```json
{
  "business": "Restaurant A",
  "evidence": [
    {
      "finding": "Menu is available on the website",
      "source_url": "https://example.com/menu"
    },
    {
      "finding": "No obvious online ordering flow was found",
      "source_url": "https://example.com/menu"
    },
    {
      "finding": "Customers are directed to phone/WhatsApp for orders",
      "source_url": "https://example.com/contact"
    }
  ]
}
```

Then the system derives:

```json
{
  "potential_opportunity": "online_ordering_system",
  "reason": "Existing digital menu but no obvious online ordering workflow",
  "confidence": 0.78
}
```

This makes the result explainable and allows users to verify the research.

---

# 5. Service Profiles

The platform uses a **Service Profile** to define what signals are relevant for a particular service.

Example:

```json
{
  "service": "online_booking_system",

  "problems": [
    "phone-only booking",
    "manual appointment scheduling",
    "WhatsApp-only booking"
  ],

  "positive_signals": [
    "appointment-based business",
    "customer consultation",
    "service reservations"
  ],

  "negative_signals": [
    "existing online booking system",
    "existing booking application"
  ],

  "evidence_to_collect": [
    "booking page",
    "appointment form",
    "booking CTA",
    "reservation system"
  ]
}
```

This allows the same research infrastructure to work with different products and services.

---

# 6. Intent → Research Plan

The system should not blindly crawl every page.

The user's intent is converted into a research plan.

Example:

```json
{
  "business_type": "gym",

  "target_service": "lead_followup_automation",

  "pages_to_prioritize": [
    "membership",
    "pricing",
    "contact",
    "booking",
    "about"
  ],

  "signals": [
    "lead_form",
    "contact_form",
    "whatsapp",
    "online_booking",
    "membership_registration"
  ],

  "crawl": {
    "max_pages": 25,
    "max_depth": 2
  }
}
```

The crawler can then focus resources on information relevant to the sales objective.

---

# 7. Opportunity Detection

The opportunity engine combines:

```text
Business Information
        +
Website Evidence
        +
Service Profile
        +
Research Signals
        ↓
Potential Opportunity
```

Example:

```text
Business:
ABC Gym

Evidence:
✓ Membership information
✓ Contact form
✓ WhatsApp
✗ No obvious consultation booking

Potential opportunity:
Appointment / consultation automation

Reason:
Prospective customers appear to rely on manual contact
rather than an obvious self-service booking flow.
```

The system should preserve the evidence supporting every generated opportunity.

---

# 8. Lead Qualification

A lead should not simply be:

```text
Business + email
```

Instead, a lead contains research context.

```json
{
  "business": {
    "name": "ABC Gym",
    "website": "https://example.com"
  },

  "opportunity": {
    "service": "appointment_automation",
    "reason": "No obvious online consultation booking"
  },

  "evidence": [
    {
      "finding": "Contact form found",
      "source": "https://example.com/contact"
    }
  ],

  "confidence": 0.78
}
```

This gives the salesperson context before contacting the business.

---

# 9. Automated Outreach

Once an opportunity has been identified, the system can generate an outreach draft.

```text
Evidence
    ↓
Opportunity
    ↓
Value Proposition
    ↓
Personalized Outreach
```

The outreach generator receives evidence rather than making unsupported assumptions.

Example input:

```json
{
  "business": "ABC Gym",

  "opportunity": "appointment_automation",

  "evidence": [
    "Membership information is available online",
    "Contact form is available",
    "No obvious consultation booking flow found"
  ]
}
```

The system can then generate a personalized message based on those observations.

Messages should remain drafts unless the user explicitly enables automated sending.

---

# 10. Automation Engine

The long-term goal is to turn the research pipeline into a reusable automation.

Example:

```text
Automation
────────────────────────────

Schedule:
Every Monday at 9:00 AM

Location:
Within 10 km of my location

Business:
Dental clinics

Service:
AI appointment assistant

Research:
Public websites

Signals:
- online booking
- appointment forms
- WhatsApp
- phone-only booking

Action:
Create potential opportunities

Output:
Personalized outreach drafts
```

The workflow then becomes:

```text
Scheduler
   ↓
Location Resolver
   ↓
Business Discovery
   ↓
Website Resolver
   ↓
Crawl4AI
   ↓
Evidence Extraction
   ↓
Opportunity Detection
   ↓
Lead Qualification
   ↓
Database
   ↓
Notification / Outreach Draft
```

---

# 11. Proposed Architecture

```text
sales-intelligence/
│
├── apps/
│   ├── api/
│   │   ├── routes/
│   │   └── dependencies/
│   │
│   └── worker/
│
├── discovery/
│   ├── business_discovery.py
│   ├── location_resolver.py
│   ├── website_resolver.py
│   └── deduplicator.py
│
├── crawler/
│   ├── crawl4ai_client.py
│   ├── crawler_config.py
│   ├── frontier.py
│   └── policies.py
│
├── intelligence/
│   ├── intent_parser.py
│   ├── research_planner.py
│   ├── evidence_extractor.py
│   ├── opportunity_engine.py
│   └── lead_qualifier.py
│
├── services/
│   ├── service_profiles/
│   │   ├── ecommerce.json
│   │   ├── booking.json
│   │   └── crm.json
│   │
│   └── outreach_generator.py
│
├── embeddings/
│   ├── embedder.py
│   └── vector_store.py
│
├── models/
│   ├── business.py
│   ├── search_intent.py
│   ├── research_job.py
│   ├── crawl.py
│   ├── evidence.py
│   └── opportunity.py
│
├── automation/
│   ├── scheduler.py
│   ├── workflows.py
│   └── jobs.py
│
├── storage/
│   ├── postgres.py
│   ├── cache.py
│   └── repositories/
│
└── README.md
```

---

# 12. Technology Stack

### Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS

### Backend

* Python
* FastAPI

### Web Research

* Crawl4AI

### AI

* LLM provider
* Structured output / JSON schemas
* Sentence Transformers

### Search / Discovery

Potential integrations:

* OpenStreetMap / Overpass
* Business/Places APIs
* Search APIs

### Database

* PostgreSQL

### Vector Search

* pgvector

### Background Processing

Potential architecture:

* Redis
* Celery / task queue
* Scheduled workers

---

# 13. Core Data Flow

```text
                  ┌──────────────┐
                  │ User Request │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │ Intent Parser│
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │Research Plan │
                  └──────┬───────┘
                         ↓
             ┌───────────┴───────────┐
             ↓                       ↓
      Location Resolver       Service Profile
             │                       │
             └───────────┬───────────┘
                         ↓
                  ┌──────────────┐
                  │  Discovery   │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │   Businesses │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │  Crawl4AI    │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │   Evidence   │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │ Opportunity  │
                  │   Engine     │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │ Lead Record  │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │   Outreach   │
                  └──────────────┘
```

---

# 14. MVP

The first version should intentionally be small.

### Phase 1 — Intent

Support natural-language requests such as:

```text
Find gyms near me that might need booking software.
```

Convert them into structured JSON.

### Phase 2 — Discovery

Implement:

```text
Location
   ↓
Business category
   ↓
Nearby businesses
```

Start with one discovery source.

### Phase 3 — Crawl4AI

For every discovered business:

```text
Business
   ↓
Website
   ↓
Crawl
   ↓
Clean content
```

### Phase 4 — Evidence

Extract a small set of signals:

```text
✓ Services
✓ Contact methods
✓ Booking
✓ Pricing
✓ Online ordering
✓ Forms
✓ Social links
```

### Phase 5 — Opportunity Engine

Map:

```text
Evidence → Potential Opportunity
```

### Phase 6 — UI

Display:

```text
Business
Potential opportunity
Why it was detected
Evidence
Source URLs
Confidence
```

### Phase 7 — Automation

Add:

```text
Schedule
   ↓
Automatic discovery
   ↓
Automatic research
   ↓
Automatic opportunity detection
```

---

# 15. Design Principles

### Evidence over assumptions

Every important inference should have supporting evidence.

### Separate discovery from crawling

Business discovery finds businesses.

Crawl4AI researches their websites.

### Structured data over raw LLM output

Prefer:

```json
{
  "booking_available": false
}
```

over:

```text
"The website seems like it doesn't have booking."
```

### Human verification

Potential opportunities should be presented with their evidence so users can verify them before contacting a business.

### Public data and responsible crawling

Only research publicly accessible information and respect website policies, rate limits, robots directives where applicable, and applicable laws and terms.

### Modular architecture

Each major component should be replaceable:

```text
Discovery Provider
       ↓
Crawl Provider
       ↓
LLM Provider
       ↓
Vector Database
```

The platform should not depend on one vendor for the entire workflow.

---

# 16. Long-Term Vision

The final system becomes a general-purpose **Sales Research Automation Engine**.

A user describes:

```text
WHO
I want to sell to

WHERE
I want to find them

WHAT
I am selling

WHAT SIGNALS
I care about
```

The platform handles the rest:

```text
Intent
 ↓
Discovery
 ↓
Research
 ↓
Evidence
 ↓
Opportunity
 ↓
Qualification
 ↓
Outreach
```

The goal is not simply to build another web scraper.

The goal is to build a system that can **autonomously transform a sales objective into a repeatable, evidence-backed research workflow.**
