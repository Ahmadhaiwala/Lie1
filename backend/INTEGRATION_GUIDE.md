# Location-Aware Lead Discovery - Integration Guide

## Overview

This guide explains how to integrate the new location-aware discovery system into your existing lead generation workflow.

## What Changed

### New Components

1. **Location Intent Parser** (`intelligence/location_intent_parser.py`)
   - Parses user queries for geographic intent
   - Detects "near me", explicit locations, radius constraints

2. **Geocoding Service** (`discovery/geocoding_service.py`)
   - Converts location strings to coordinates
   - Supports Google Geocoding API + OpenStreetMap Nominatim

3. **Distance Calculator** (`discovery/distance_calculator.py`)
   - Haversine formula for distance calculation
   - Radius-based filtering utilities

4. **Geographic Filter** (`filters/geographic_filter.py`)
   - Filters leads by location before qualification
   - Saves LLM tokens by excluding out-of-scope businesses

5. **Google Maps Discovery** (`discovery/google_maps_discovery.py`)
   - Primary business discovery from Google Maps
   - Full location data extraction with coordinates

### Enhanced Models

- **LocationIntent**: New model for parsed location constraints
- **SearchContext**: Metadata about geographic search scope
- **BusinessLocation**: Added `distance_km` field

## Integration Steps

### Step 1: Update Environment Variables

Add required API keys to your `.env` file:

```env
# Primary option (recommended)
GOOGLE_MAPS_API_KEY=your_google_api_key_here

# Alternative (SerpApi)
SERPAPI_API_KEY=your_serpapi_key_here
```

**Note**: You need at least ONE of these APIs configured.

### Step 2: Update Job Classes

Modify your job classes in `automation/jobs.py` to accept location intent:

```python
from intelligence.location_intent_parser import parse_location_intent
from discovery.google_maps_discovery import GoogleMapsDiscovery
from filters.geographic_filter import filter_by_geography

async def run_job(self, user_query: str, user_location=None):
    # 1. Parse location intent
    location_intent = parse_location_intent(user_query, user_location)
    
    # 2. Check if location is missing
    if location_intent.is_missing:
        return {
            "status": "error",
            "message": "Location required. Please specify a location.",
            "suggestions": [
                "Add 'near me' to your query",
                "Specify a city: 'restaurants in London'",
                "Add radius: 'dentists within 5km'"
            ]
        }
    
    # 3. Geocode if needed
    if location_intent.search_center and not location_intent.search_center_coords:
        from discovery.geocoding_service import geocode
        lat, lng, confidence = await geocode(location_intent.search_center)
        location_intent.search_center_coords = (lat, lng)
    
    # 4. Discover businesses using Google Maps
    discovery = GoogleMapsDiscovery()
    businesses = await discovery.discover_businesses(
        query=self.business_category,  # e.g., "restaurants"
        location_intent=location_intent,
        max_results=50
    )
    
    # 5. Convert businesses to leads (existing qualification logic)
    leads = await self.qualify_businesses(businesses)
    
    # 6. Apply geographic filter
    geo_result = filter_by_geography(leads, location_intent)
    filtered_leads = geo_result.filtered_leads
    
    # 7. Continue with existing pipeline (scoring, enrichment, outreach)
    # ...
```

### Step 3: Update Workflow Engine

Modify `automation/workflows.py` to support location intent:

```python
from models.location_intent import SearchContext

async def run_discovery_workflow(
    service_needed: str,
    user_query: str,
    user_location: Optional[Tuple[float, float]] = None
) -> Dict[str, Any]:
    """
    Run location-aware discovery workflow.
    
    Args:
        service_needed: "website" | "whatsapp_bot" | "seo"
        user_query: User's search query
        user_location: Optional (lat, lng) of user
    
    Returns:
        Dict with leads and search_context
    """
    # Parse location intent
    location_intent = parse_location_intent(user_query, user_location)
    
    # Check location
    if location_intent.is_missing:
        return {"status": "location_required", "message": "Please specify a location"}
    
    # Run appropriate job with location awareness
    job = get_job_for_service(service_needed)
    result = await job.run(user_query, user_location)
    
    # Build search context
    search_context = SearchContext(
        location_source=location_intent.location_source.value,
        search_center=location_intent.search_center,
        search_center_coords=location_intent.search_center_coords,
        radius_km=location_intent.radius_km,
        business_categories=[job.business_category],
        location_confidence=location_intent.location_confidence,
        total_discovered=len(result.get("leads", [])),
        within_radius=len([l for l in result.get("leads", []) 
                          if l.get("location", {}).get("distance_km") is not None])
    )
    
    return {
        "search_context": search_context.to_dict(),
        "leads": result.get("leads", []),
        "outreach": result.get("outreach", [])
    }
```

### Step 4: Update Lead Output Format

Ensure your lead dictionaries include structured location:

```python
def lead_to_dict(lead: Lead) -> dict:
    return {
        "id": lead.id,
        "business_name": lead.business_name,
        "service_needed": lead.service_needed,
        "location": {
            "address": lead.location_address,
            "city": lead.location_city,
            "state": lead.location_state,
            "country": lead.location_country,
            "postal_code": lead.location_postal,
            "latitude": lead.location_lat,
            "longitude": lead.location_lng,
            "distance_km": lead.distance_km
        },
        # ... other fields
    }
```

### Step 5: Update API Routes

If you have API endpoints, update them to accept location:

```python
# api/routes/leads.py

@router.post("/discover")
async def discover_leads(
    service: str,
    query: str,
    user_lat: Optional[float] = None,
    user_lng: Optional[float] = None
):
    user_location = (user_lat, user_lng) if user_lat and user_lng else None
    
    result = await run_discovery_workflow(
        service_needed=service,
        user_query=query,
        user_location=user_location
    )
    
    return result
```

## Usage Examples

### Example 1: Near Me

```python
result = await run_discovery_workflow(
    service_needed="website",
    user_query="restaurants near me",
    user_location=(23.0225, 72.5714)  # Ahmedabad
)
```

**Expected Output**:
```json
{
  "search_context": {
    "location_source": "near_me",
    "search_center": "user_current_location",
    "radius_km": 10,
    "business_categories": ["restaurants"],
    "location_confidence": 0.85
  },
  "leads": [
    {
      "business_name": "Royal Spice Restaurant",
      "location": {
        "city": "Ahmedabad",
        "distance_km": 4.7
      }
    }
  ]
}
```

### Example 2: Explicit Location + Radius

```python
result = await run_discovery_workflow(
    service_needed="seo",
    user_query="dentists within 5km of London"
)
```

### Example 3: City Search (No Radius)

```python
result = await run_discovery_workflow(
    service_needed="whatsapp_bot",
    user_query="cafes in New York"
)
```

### Example 4: Missing Location (Error Case)

```python
result = await run_discovery_workflow(
    service_needed="website",
    user_query="find restaurants"
)

# Returns:
# {
#   "status": "location_required",
#   "message": "Please specify a location"
# }
```

## Migration Path

### Option A: Gradual Migration (Recommended)

1. Deploy new code alongside existing system
2. Add feature flag: `ENABLE_LOCATION_AWARE_DISCOVERY=true`
3. Route new requests through location-aware pipeline
4. Keep old pipeline for backward compatibility
5. Phase out old pipeline after testing

### Option B: Full Migration

1. Update all job classes to require location intent
2. Update API routes to require location parameter
3. Update frontend/CLI to capture user location
4. Deploy with breaking changes notice

## Testing

Run the example script:

```bash
cd backend
python examples/location_aware_discovery.py
```

**Expected Output**: Examples demonstrating all location patterns

## Troubleshooting

### Issue: "No API configured"

**Solution**: Set `GOOGLE_MAPS_API_KEY` or `SERPAPI_API_KEY` in `.env`

### Issue: Geocoding returns None

**Possible causes**:
- Invalid location string
- API key issues
- Rate limiting

**Solution**: Check logs for specific error messages

### Issue: No businesses found

**Possible causes**:
- Radius too small
- Location too specific
- API query formatting

**Solution**: 
- Increase radius
- Use broader location (city vs. neighborhood)
- Check API logs

### Issue: Distance calculation incorrect

**Solution**: Verify coordinates are in decimal degrees format (not DMS)

## Performance Considerations

1. **Geocoding Cache**: Locations are cached to minimize API calls
2. **Distance Filtering**: Applied BEFORE LLM qualification to save tokens
3. **Batch Processing**: Calculate distances in batch for efficiency
4. **API Rate Limits**: 
   - Google Maps: 40,000 requests/day (free tier)
   - SerpApi: Varies by plan
   - Nominatim: Max 1 request/second

## Next Steps

After integration:

1. Monitor API usage and costs
2. Add location autocomplete in frontend
3. Implement location caching strategy
4. Add geographic analytics (heatmaps, coverage areas)
5. Support multi-location searches
6. Add location-based lead scoring

## Support

For issues or questions:
- Check `examples/location_aware_discovery.py`
- Review `LOCATION_AWARE_LEAD_DISCOVERY.md` specification
- Enable debug logging: `logging.getLogger("discovery").setLevel(logging.DEBUG)`
