# Location-Aware Lead Discovery - Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         USER / API REQUEST                                  │
│                    "Find dentists" or "Find restaurants"                     │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LOCATION CONFIGURATION                               │
│                                                                              │
│  location_config.py:                                                        │
│  - DEFAULT_LOCATION_NAME = "Ahmedabad, Gujarat, India"                     │
│  - DEFAULT_LOCATION_LAT = 23.0225                                          │
│  - DEFAULT_LOCATION_LNG = 72.5714                                          │
│  - DEFAULT_SEARCH_RADIUS_KM = 20                                           │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         JOB EXECUTION LAYER                                  │
│                      automation/jobs.py                                      │
│                                                                              │
│  BaseLeadJob → WebsiteLeadJob / WhatsAppBotLeadJob / SEOLeadJob            │
│                                                                              │
│  Responsibilities:                                                           │
│  - Define search queries                                                     │
│  - Call SearchProvider                                                       │
│  - Qualify leads via LLM                                                     │
│  - Extract contact information                                               │
│  - Create Lead objects                                                       │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SEARCH PROVIDER LAYER                                   │
│                   automation/search_provider.py                              │
│                                                                              │
│  SearchProvider:                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │ 1. Receive query: "dentists"                                     │       │
│  │                                                                   │       │
│  │ 2. Add location: "dentists in Ahmedabad, Gujarat, India"        │       │
│  │                                                                   │       │
│  │ 3. Choose API:                                                   │       │
│  │    ├── SerpApi (Google Maps engine)                             │       │
│  │    └── Google Places API                                         │       │
│  │                                                                   │       │
│  │ 4. Add location constraints:                                     │       │
│  │    - Center: lat=23.0225, lng=72.5714                           │       │
│  │    - Radius: 20km                                                │       │
│  └─────────────────────────────────────────────────────────────────┘       │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
        ┌──────────────────────┐     ┌──────────────────────┐
        │   SERPAPI GOOGLE     │     │  GOOGLE PLACES API   │
        │   MAPS ENGINE        │     │                      │
        │                      │     │  ┌────────────────┐  │
        │  Request:            │     │  │ Request:       │  │
        │  {                   │     │  │ {              │  │
        │    "engine":         │     │  │   "textQuery": │  │
        │      "google_maps",  │     │  │     "...",     │  │
        │    "q": "...",       │     │  │   "locationBias":│
        │    "ll": "@23.0225,  │     │  │   {            │  │
        │           72.5714"   │     │  │    "circle": { │  │
        │  }                   │     │  │      "center": {...},│
        └──────────┬───────────┘     │  │      "radius": 20000│
                   │                 │  │    }           │  │
                   │                 │  │   }            │  │
                   │                 │  │ }              │  │
                   │                 └──┴────────────────┘  │
                   │                    └────────┬───────────┘
                   └─────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BUSINESS DISCOVERY RESULTS                                │
│                                                                              │
│  Raw API Response:                                                           │
│  [                                                                           │
│    {                                                                         │
│      "title": "Royal Dental Clinic",                                        │
│      "address": "123 Main St, Ahmedabad",                                   │
│      "phone": "+91 79 1234 5678",                                           │
│      "website": "https://royaldental.com",                                  │
│      "gps_coordinates": {                                                    │
│        "latitude": 23.0264,                                                  │
│        "longitude": 72.5970                                                  │
│      }                                                                        │
│    },                                                                        │
│    ...                                                                       │
│  ]                                                                           │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DISTANCE CALCULATION                                      │
│                 discovery/distance_calculator.py                             │
│                                                                              │
│  For each business:                                                          │
│  ┌────────────────────────────────────────────────────────────────┐        │
│  │ calculate_distance_km(                                          │        │
│  │   center_lat=23.0225,      # Ahmedabad center                  │        │
│  │   center_lng=72.5714,                                           │        │
│  │   business_lat=23.0264,    # Business location                 │        │
│  │   business_lng=72.5970                                          │        │
│  │ )                                                                │        │
│  │                                                                  │        │
│  │ Returns: 4.7 km                                                  │        │
│  └────────────────────────────────────────────────────────────────┘        │
│                                                                              │
│  Haversine Formula:                                                          │
│  - Accurate to ~99.5% for typical distances                                 │
│  - No API calls required                                                     │
│  - Fast: <1ms per calculation                                               │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ENRICHED BUSINESS DATA                                    │
│                                                                              │
│  [                                                                           │
│    {                                                                         │
│      "business_name": "Royal Dental Clinic",                                │
│      "location": "Ahmedabad [Coordinates: 23.0264, 72.5970] [4.7km]",     │
│      "latitude": 23.0264,                                                    │
│      "longitude": 72.5970,                                                   │
│      "distance_km": 4.7,                                                     │
│      "phone": "+91 79 1234 5678",                                           │
│      "website": "https://royaldental.com",                                  │
│      "content": "..."                                                        │
│    },                                                                        │
│    ...                                                                       │
│  ]                                                                           │
│                                                                              │
│  Sorted by: distance_km (nearest first)                                     │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LEAD QUALIFICATION                                        │
│                     automation/jobs.py                                       │
│                                                                              │
│  For each business:                                                          │
│  ┌────────────────────────────────────────────────────────────────┐        │
│  │ 1. Validate source (not YouTube/Reddit/etc)                     │        │
│  │ 2. LLM qualification:                                            │        │
│  │    - Is this a real business?                                    │        │
│  │    - What are the pain points?                                   │        │
│  │    - Qualification score (0-1)                                   │        │
│  │ 3. Extract contact info                                          │        │
│  │ 4. Create Lead object with geographic data                       │        │
│  └────────────────────────────────────────────────────────────────┘        │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BUSINESS FILTERING                                        │
│                  filters/business_filter.py                                  │
│                                                                              │
│  For each lead:                                                              │
│  - Online presence score (0-10)                                             │
│  - Suitability score (0-10)                                                 │
│  - Priority: HIGH / MEDIUM / DISCARD                                        │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FINAL LEAD OUTPUT                                    │
│                    leads_output/leads_*.json                                 │
│                                                                              │
│  [                                                                           │
│    {                                                                         │
│      "id": "abc-123",                                                        │
│      "business_name": "Royal Dental Clinic",                                │
│      "service_needed": "website",                                           │
│      "location": "Ahmedabad [Coordinates: 23.0264, 72.5970] [4.7km]",     │
│      "latitude": 23.0264,                    ← NEW                          │
│      "longitude": 72.5970,                   ← NEW                          │
│      "distance_km": 4.7,                     ← NEW                          │
│      "contact_email": ["info@royaldental.com"],                            │
│      "contact_phone": ["+91 79 1234 5678"],                                │
│      "website": "https://royaldental.com",                                  │
│      "pain_points": [                                                        │
│        "No online booking system",                                           │
│        "Website not mobile-friendly"                                         │
│      ],                                                                      │
│      "qualification_score": 0.85,                                           │
│      "filter_priority": "high",                                             │
│      "industry": "Dental Clinic"                                            │
│    }                                                                         │
│  ]                                                                           │
│                                                                              │
│  ✅ All businesses from Ahmedabad                                           │
│  ✅ Sorted by distance (nearest first)                                      │
│  ✅ Includes coordinates and distance                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Summary

```
User Query
    ↓
Location Config (Ahmedabad)
    ↓
Search Provider + Location
    ↓
API Search (Google Maps/SerpApi)
    ↓
Raw Business Results
    ↓
Distance Calculation (Haversine)
    ↓
Sort by Distance
    ↓
LLM Qualification
    ↓
Business Filtering
    ↓
Final Leads (JSON)
```

## Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| Location Config | Central location settings | `location_config.py` |
| Search Provider | API integration + location | `automation/search_provider.py` |
| Distance Calculator | Haversine formula | `discovery/distance_calculator.py` |
| Job Classes | Lead qualification | `automation/jobs.py` |
| Business Filter | Quality filtering | `filters/business_filter.py` |

## Geographic Flow

```
1. Configuration:
   Ahmedabad, Gujarat, India
   lat: 23.0225, lng: 72.5714
   radius: 20km

2. Query Enhancement:
   "dentists" → "dentists in Ahmedabad, Gujarat, India"

3. API Request:
   location_bias: {
     center: {lat: 23.0225, lng: 72.5714},
     radius: 20000 meters
   }

4. Distance Calculation:
   For each business:
   distance = haversine(center, business_coords)

5. Sorting:
   Sort by distance ASC

6. Output:
   All leads with coordinates + distance
```

## Integration Points

```
┌─────────────────┐
│ Existing System │
│   (jobs.py)     │
└────────┬────────┘
         │
         ├─→ Uses SearchProvider (UPDATED)
         │   └─→ Adds location to queries
         │   └─→ Calculates distances
         │   └─→ Returns geographic data
         │
         └─→ Creates Leads (UPDATED)
             └─→ Includes lat/lng/distance
```

## Configuration Hierarchy

```
Environment Variables (.env)
    ↓ (overrides)
location_config.py defaults
    ↓ (provides)
SearchProvider
    ↓ (uses in)
API Requests
```

## Output Comparison

### Before:
```json
{
  "business_name": "Some Dental",
  "location": "New York, NY"
}
```

### After:
```json
{
  "business_name": "Royal Dental Clinic",
  "location": "Ahmedabad [Coordinates: 23.0264, 72.5970] [4.7km]",
  "latitude": 23.0264,
  "longitude": 72.5970,
  "distance_km": 4.7
}
```

---

**System is now fully location-aware and targets Ahmedabad by default!** 🎯
