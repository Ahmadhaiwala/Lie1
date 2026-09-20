# Location-Aware Lead Discovery Implementation Plan

## Problem Statement
Current system generates leads WITHOUT geographic awareness:
- ❌ No understanding of "near me" vs "in [city]"
- ❌ No radius-based filtering
- ❌ No distance calculation
- ❌ Discovers businesses globally regardless of user intent
- ❌ Location is just a string, not structured data

## Solution Architecture

### 1. Enhanced Location Models

**LocationIntent** (new model):
```python
@dataclass
class LocationIntent:
    """Parsed geographic intent from user query"""
    location_source: str  # "user_location" | "explicit_location" | "near_me" | "country" | "missing"
    search_center: Optional[str]  # "Ahmedabad" | "London" | "user_current_location"
    search_center_coords: Optional[Tuple[float, float]]  # (lat, lng)
    radius_km: Optional[float]  # Explicit or default radius
    location_confidence: float  # 0.0 - 1.0
```

**Enhanced BusinessLocation**:
```python
class BusinessLocation(BaseModel):
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    postal_code: Optional[str]
    latitude: Optional[float]  # REQUIRED for distance filtering
    longitude: Optional[float]  # REQUIRED for distance filtering
    distance_km: Optional[float]  # Calculated from search center
    is_primary: bool = True
```

**SearchContext** (new model):
```python
@dataclass
class SearchContext:
    """Metadata about the geographic search scope"""
    location_source: str
    search_center: str
    search_center_coords: Optional[Tuple[float, float]]
    radius_km: Optional[float]
    business_categories: List[str]
    location_confidence: float
    total_discovered: int
    within_radius: int
```

### 2. Location Intent Parser

**File**: `intelligence/location_intent_parser.py`

Responsibilities:
- Parse user queries for geographic intent
- Detect "near me", "within X km", "in [city]"
- Determine default radius based on location type
- Handle international searches
- Return LocationIntent object

Examples:
- "restaurants near me" → `location_source="near_me"`, `radius_km=10`
- "dentists within 5km of Ahmedabad" → `location_source="explicit_location"`, `search_center="Ahmedabad"`, `radius_km=5`
- "cafes in London" → `location_source="explicit_location"`, `search_center="London"`, `radius_km=None`
- "businesses" → `location_source="missing"` → ASK USER

### 3. Enhanced Google Maps Discovery

**File**: `discovery/google_maps_discovery.py` (new)

Features:
- **Primary discovery source** for local businesses
- Extract full location data: address, city, coordinates
- Use Google Maps Places API or SerpApi Google Maps
- Calculate distance from search center
- Apply radius filter BEFORE returning results

API Integration:
```python
async def discover_businesses(
    query: str,
    location_intent: LocationIntent,
    max_results: int = 50
) -> List[Business]:
    # 1. Build Google Maps query with location constraints
    # 2. Call API (Google Places or SerpApi)
    # 3. Parse results into Business objects with full location data
    # 4. Calculate distance_km for each business
    # 5. Filter by radius if specified
    # 6. Return businesses within scope
```

### 4. Distance Calculator

**File**: `discovery/distance_calculator.py` (new)

Haversine formula implementation:
```python
def calculate_distance_km(
    lat1: float, lon1: float,
    lat2: float, lon2: float
) -> float:
    """Calculate distance between two coordinates in kilometers"""
```

### 5. Geographic Geocoding Service

**File**: `discovery/geocoding_service.py` (new)

Replace mock coordinates with real API:
- **Primary**: Google Maps Geocoding API
- **Fallback**: OpenStreetMap Nominatim (free)

Features:
- Convert location strings to coordinates
- Cache results to minimize API calls
- Handle ambiguous locations
- Return confidence score

### 6. Enhanced Search Provider

**Update**: `automation/search_provider.py`

Changes:
- Accept `LocationIntent` parameter
- Build location-constrained queries
- For Google Maps: use `location` and `radius` parameters
- For SerpApi: include location in query string
- Extract coordinates from all results

### 7. Geographic Lead Filter

**File**: `filters/geographic_filter.py` (new)

Purpose: Filter leads by geographic constraints BEFORE qualification

```python
def filter_by_geography(
    leads: List[Lead],
    location_intent: LocationIntent
) -> List[Lead]:
    # 1. Skip if no geographic constraints
    # 2. Remove leads without coordinates
    # 3. Calculate distance for each lead
    # 4. Filter by radius if specified
    # 5. Sort by distance (nearest first)
    # 6. Return filtered leads
```

### 8. Enhanced Lead Output

**New Fields in Lead JSON**:
```json
{
  "id": "...",
  "business_name": "...",
  "location": {
    "address": "123 Main St",
    "city": "Ahmedabad",
    "state": "Gujarat",
    "country": "India",
    "postal_code": "380001",
    "latitude": 23.0225,
    "longitude": 72.5714,
    "distance_km": 4.7
  },
  "search_context": {
    "location_source": "explicit_location",
    "search_center": "Ahmedabad",
    "radius_km": 10,
    "business_categories": ["restaurants"],
    "location_confidence": 0.95
  }
}
```

### 9. Updated Workflow

**File**: `automation/workflows.py`

New discovery flow:
```python
async def run_location_aware_discovery(
    user_query: str,
    user_location: Optional[Tuple[float, float]] = None
) -> Dict[str, Any]:
    # 1. Parse location intent
    location_intent = await location_parser.parse(user_query, user_location)
    
    # 2. Check if location is missing
    if location_intent.location_source == "missing":
        return {"status": "location_required", "message": "Please specify a location"}
    
    # 3. Geocode search center if needed
    if location_intent.search_center and not location_intent.search_center_coords:
        coords = await geocoding_service.geocode(location_intent.search_center)
        location_intent.search_center_coords = coords
    
    # 4. Discover businesses from Google Maps
    businesses = await google_maps_discovery.discover_businesses(
        query=business_category,
        location_intent=location_intent,
        max_results=50
    )
    
    # 5. Calculate distances
    for business in businesses:
        if business.locations and location_intent.search_center_coords:
            distance = calculate_distance_km(
                location_intent.search_center_coords[0],
                location_intent.search_center_coords[1],
                business.locations[0].latitude,
                business.locations[0].longitude
            )
            business.locations[0].distance_km = distance
    
    # 6. Filter by radius
    if location_intent.radius_km:
        businesses = [b for b in businesses 
                     if b.locations and b.locations[0].distance_km <= location_intent.radius_km]
    
    # 7. Qualify leads (existing pipeline)
    leads = await qualify_businesses(businesses)
    
    # 8. Return with search context
    return {
        "search_context": location_intent.to_dict(),
        "leads": [lead.to_dict() for lead in leads]
    }
```

## Implementation Priority

### Phase 1: Core Infrastructure (Day 1)
1. ✅ Create `LocationIntent` model
2. ✅ Create `location_intent_parser.py`
3. ✅ Create `distance_calculator.py`
4. ✅ Update `BusinessLocation` model with distance_km

### Phase 2: API Integration (Day 2)
5. ✅ Create `geocoding_service.py` with real API
6. ✅ Create `google_maps_discovery.py`
7. ✅ Update `search_provider.py` to accept LocationIntent

### Phase 3: Filtering & Workflow (Day 3)
8. ✅ Create `geographic_filter.py`
9. ✅ Update `workflows.py` with location-aware flow
10. ✅ Update Lead model output with search_context

### Phase 4: Testing & Validation (Day 4)
11. ✅ Test "near me" queries
12. ✅ Test explicit location + radius
13. ✅ Test international searches
14. ✅ Verify distance calculations
15. ✅ Validate lead output format

## Configuration

**Required Environment Variables**:
```env
# Primary geocoding & maps
GOOGLE_MAPS_API_KEY=your_key_here

# Alternative search (if not using Google Places)
SERPAPI_API_KEY=your_key_here

# Optional: User location source (if building web app)
USER_LOCATION_API_ENABLED=true
```

## Example Queries & Expected Behavior

| User Query | Expected Behavior |
|------------|-------------------|
| "Find restaurants near me" | Use user's current location + 10km radius |
| "Find dentists within 5km" | Use user's current location + 5km radius |
| "Find restaurants in Ahmedabad" | Search Ahmedabad, no radius limit |
| "Find cafes within 25km of London" | Search London + 25km radius |
| "Find businesses" | Return error: "Please specify a location" |
| "Find dentists in New York" | Search New York, USA (not user's location) |

## Success Criteria

✅ Every lead has structured location with lat/lng  
✅ Distance_km calculated for all leads  
✅ Radius filtering works correctly  
✅ "Near me" uses user location  
✅ Explicit locations override user location  
✅ Missing location returns error message  
✅ Search context included in output  
✅ Google Maps is primary discovery source  

## Migration Notes

**Backward Compatibility**:
- Old `location` string field → map to `location.address` or `location.city`
- Jobs without location intent → treat as missing, prompt user
- Existing leads can be geocoded retroactively

**Breaking Changes**:
- Lead output format changes (location becomes object)
- WorkflowEngine signature changes (add location_intent parameter)
- Search queries must include location

---

*This document serves as the technical specification for implementing fully location-aware B2B lead discovery.*
