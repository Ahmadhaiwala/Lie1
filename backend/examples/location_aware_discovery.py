"""
Location-Aware Lead Discovery Example
--------------------------------------
Demonstrates the complete flow of geographic-aware B2B lead discovery.

Usage:
    python examples/location_aware_discovery.py
"""
import asyncio
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intelligence.location_intent_parser import LocationIntentParser
from discovery.geocoding_service import GeocodingService
from discovery.google_maps_discovery import GoogleMapsDiscovery
from filters.geographic_filter import GeographicFilter
from models.location_intent import SearchContext


async def example_near_me():
    """Example: 'restaurants near me'"""
    print("\n" + "="*70)
    print("EXAMPLE 1: 'restaurants near me'")
    print("="*70)
    
    # Simulate user location (Ahmedabad, India)
    user_location = (23.0225, 72.5714)
    
    # Parse location intent
    parser = LocationIntentParser()
    location_intent = parser.parse("restaurants near me", user_location)
    
    print(f"\n📍 Location Intent:")
    print(f"  Source: {location_intent.location_source.value}")
    print(f"  Center: {location_intent.search_center}")
    print(f"  Coordinates: {location_intent.search_center_coords}")
    print(f"  Radius: {location_intent.radius_km}km")
    print(f"  Confidence: {location_intent.location_confidence}")
    
    # Discover businesses
    discovery = GoogleMapsDiscovery()
    
    if not discovery.is_configured:
        print("\n⚠️  No API configured. Set GOOGLE_MAPS_API_KEY or SERPAPI_API_KEY")
        return
    
    print(f"\n🔍 Discovering via {discovery.provider_name}...")
    businesses = await discovery.discover_businesses(
        query="restaurants",
        location_intent=location_intent,
        max_results=10
    )
    
    print(f"\n✅ Found {len(businesses)} businesses:")
    for i, biz in enumerate(businesses[:5], 1):
        loc = biz.locations[0] if biz.locations else None
        distance = loc.distance_km if loc else None
        print(f"\n  {i}. {biz.name}")
        if loc:
            print(f"     📍 {loc.city}, {loc.state}")
            print(f"     📏 {distance:.2f}km away")
        if biz.contact.phone:
            print(f"     📞 {biz.contact.phone}")
        if biz.contact.website:
            print(f"     🌐 {biz.contact.website}")


async def example_explicit_location_with_radius():
    """Example: 'dentists within 5km of Ahmedabad'"""
    print("\n" + "="*70)
    print("EXAMPLE 2: 'dentists within 5km of Ahmedabad'")
    print("="*70)
    
    # Parse location intent
    parser = LocationIntentParser()
    location_intent = parser.parse("dentists within 5km of Ahmedabad")
    
    print(f"\n📍 Location Intent:")
    print(f"  Source: {location_intent.location_source.value}")
    print(f"  Center: {location_intent.search_center}")
    print(f"  Radius: {location_intent.radius_km}km")
    
    # Geocode the location
    geocoding = GeocodingService()
    lat, lng, confidence = await geocoding.geocode(location_intent.search_center)
    
    if lat and lng:
        location_intent.search_center_coords = (lat, lng)
        print(f"  Geocoded to: ({lat}, {lng})")
        print(f"  Geocoding confidence: {confidence}")
    else:
        print("  ❌ Geocoding failed")
        return
    
    # Discover businesses
    discovery = GoogleMapsDiscovery()
    
    if not discovery.is_configured:
        print("\n⚠️  No API configured. Set GOOGLE_MAPS_API_KEY or SERPAPI_API_KEY")
        return
    
    print(f"\n🔍 Discovering via {discovery.provider_name}...")
    businesses = await discovery.discover_businesses(
        query="dentists",
        location_intent=location_intent,
        max_results=10
    )
    
    print(f"\n✅ Found {len(businesses)} businesses within 5km:")
    for i, biz in enumerate(businesses, 1):
        loc = biz.locations[0] if biz.locations else None
        distance = loc.distance_km if loc else None
        print(f"\n  {i}. {biz.name}")
        if loc:
            print(f"     📍 {loc.address}")
            print(f"     📏 {distance:.2f}km from center")


async def example_explicit_location_no_radius():
    """Example: 'cafes in London'"""
    print("\n" + "="*70)
    print("EXAMPLE 3: 'cafes in London'")
    print("="*70)
    
    # Parse location intent
    parser = LocationIntentParser()
    location_intent = parser.parse("cafes in London")
    
    print(f"\n📍 Location Intent:")
    print(f"  Source: {location_intent.location_source.value}")
    print(f"  Center: {location_intent.search_center}")
    print(f"  Radius: {location_intent.radius_km} (no radius constraint)")
    
    # Geocode the location
    geocoding = GeocodingService()
    lat, lng, confidence = await geocoding.geocode(location_intent.search_center)
    
    if lat and lng:
        location_intent.search_center_coords = (lat, lng)
        print(f"  Geocoded to: ({lat}, {lng})")
    
    # Discover businesses
    discovery = GoogleMapsDiscovery()
    
    if not discovery.is_configured:
        print("\n⚠️  No API configured. Set GOOGLE_MAPS_API_KEY or SERPAPI_API_KEY")
        return
    
    print(f"\n🔍 Discovering via {discovery.provider_name}...")
    businesses = await discovery.discover_businesses(
        query="cafes",
        location_intent=location_intent,
        max_results=10
    )
    
    print(f"\n✅ Found {len(businesses)} businesses:")
    for i, biz in enumerate(businesses[:5], 1):
        loc = biz.locations[0] if biz.locations else None
        distance = loc.distance_km if loc and loc.distance_km else None
        print(f"\n  {i}. {biz.name}")
        if loc:
            print(f"     📍 {loc.address}")
            if distance:
                print(f"     📏 {distance:.2f}km from center")


async def example_missing_location():
    """Example: 'find restaurants' (no location)"""
    print("\n" + "="*70)
    print("EXAMPLE 4: 'find restaurants' (missing location)")
    print("="*70)
    
    # Parse location intent
    parser = LocationIntentParser()
    location_intent = parser.parse("find restaurants")
    
    print(f"\n📍 Location Intent:")
    print(f"  Source: {location_intent.location_source.value}")
    print(f"  Status: MISSING")
    
    if location_intent.is_missing:
        print("\n❌ Location required!")
        print("   Please specify a location, e.g.:")
        print("   - 'restaurants near me'")
        print("   - 'restaurants in London'")
        print("   - 'restaurants within 10km'")


async def example_search_context_output():
    """Example: Complete lead output with search context"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Complete Lead Output Format")
    print("="*70)
    
    # Simulate discovered leads
    user_location = (23.0225, 72.5714)
    
    parser = LocationIntentParser()
    location_intent = parser.parse("restaurants near me", user_location)
    
    # Create search context
    search_context = SearchContext(
        location_source=location_intent.location_source.value,
        search_center=location_intent.search_center,
        search_center_coords=location_intent.search_center_coords,
        radius_km=location_intent.radius_km,
        business_categories=["restaurants", "cafes"],
        location_confidence=location_intent.location_confidence,
        total_discovered=50,
        within_radius=12,
    )
    
    # Example lead structure
    example_lead = {
        "id": "abc-123",
        "business_name": "Royal Spice Restaurant",
        "service_needed": "website",
        "location": {
            "address": "123 Main Street, Maninagar",
            "city": "Ahmedabad",
            "state": "Gujarat",
            "country": "India",
            "postal_code": "380008",
            "latitude": 23.0264,
            "longitude": 72.5970,
            "distance_km": 4.7
        },
        "contact_email": ["info@royalspice.com"],
        "contact_phone": ["+91 79 1234 5678"],
        "website": "https://royalspice.com",
        "pain_points": [
            "No online ordering system",
            "Website not mobile-friendly",
            "Poor Google ranking"
        ],
        "qualification_score": 0.85,
        "search_context": search_context.to_dict()
    }
    
    print("\n📄 Example Lead Output (JSON):")
    print(json.dumps(example_lead, indent=2))


async def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("LOCATION-AWARE LEAD DISCOVERY EXAMPLES")
    print("="*70)
    
    await example_near_me()
    await example_explicit_location_with_radius()
    await example_explicit_location_no_radius()
    await example_missing_location()
    await example_search_context_output()
    
    print("\n" + "="*70)
    print("✅ Examples complete!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
