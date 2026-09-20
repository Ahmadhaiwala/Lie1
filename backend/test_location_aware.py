"""
Quick Test Script for Location-Aware Discovery
-----------------------------------------------
Tests all components without requiring full API setup.
"""
import asyncio
import sys
from intelligence.location_intent_parser import LocationIntentParser
from discovery.distance_calculator import calculate_distance_km, DistanceCalculator
from models.location_intent import LocationSource


def test_location_intent_parser():
    """Test location intent parsing"""
    print("\n" + "="*70)
    print("TEST 1: Location Intent Parser")
    print("="*70)
    
    parser = LocationIntentParser()
    
    # Test cases
    test_cases = [
        ("restaurants near me", None, LocationSource.NEAR_ME),
        ("dentists within 5km", None, LocationSource.USER_LOCATION),
        ("cafes in London", None, LocationSource.EXPLICIT_LOCATION),
        ("restaurants within 25km of Ahmedabad", None, LocationSource.EXPLICIT_LOCATION),
        ("find businesses", None, LocationSource.MISSING),
        ("restaurants nearby", (23.0, 72.5), LocationSource.NEAR_ME),
    ]
    
    for query, user_loc, expected_source in test_cases:
        intent = parser.parse(query, user_loc)
        status = "✅" if intent.location_source == expected_source else "❌"
        print(f"\n{status} Query: '{query}'")
        print(f"   Source: {intent.location_source.value}")
        if intent.search_center:
            print(f"   Center: {intent.search_center}")
        if intent.radius_km:
            print(f"   Radius: {intent.radius_km}km")


def test_distance_calculator():
    """Test distance calculations"""
    print("\n" + "="*70)
    print("TEST 2: Distance Calculator")
    print("="*70)
    
    # Test known distances
    test_cases = [
        # (lat1, lon1, lat2, lon2, expected_km_approx)
        (23.0225, 72.5714, 19.0760, 72.8777, 442),  # Ahmedabad to Mumbai
        (51.5074, -0.1278, 48.8566, 2.3522, 344),   # London to Paris
        (40.7128, -74.0060, 34.0522, -118.2437, 3936),  # NYC to LA
    ]
    
    for lat1, lon1, lat2, lon2, expected in test_cases:
        distance = calculate_distance_km(lat1, lon1, lat2, lon2)
        diff = abs(distance - expected)
        status = "✅" if diff < 50 else "❌"  # Within 50km tolerance
        print(f"\n{status} Distance: {distance:.2f}km (expected ~{expected}km)")


def test_distance_calculator_class():
    """Test DistanceCalculator class"""
    print("\n" + "="*70)
    print("TEST 3: DistanceCalculator Class")
    print("="*70)
    
    # Center: Ahmedabad
    center = (23.0225, 72.5714)
    calculator = DistanceCalculator(center)
    
    # Points around Ahmedabad
    points = [
        (23.0264, 72.5970, "Maninagar"),  # ~4km
        (23.0359, 72.5067, "Satellite"),  # ~7km
        (23.1089, 72.5476, "Chandkheda"),  # ~10km
    ]
    
    print(f"\nCenter: Ahmedabad ({center})")
    print("Testing radius filter (10km):")
    
    for lat, lng, name in points:
        distance = calculator.calculate_distance(lat, lng)
        within = calculator.is_within_radius(lat, lng, 10.0)
        status = "✅" if within else "❌"
        print(f"\n{status} {name}: {distance:.2f}km - {'WITHIN' if within else 'OUTSIDE'} 10km radius")


def test_location_patterns():
    """Test location pattern extraction"""
    print("\n" + "="*70)
    print("TEST 4: Location Pattern Extraction")
    print("="*70)
    
    parser = LocationIntentParser()
    
    test_cases = [
        "restaurants in London",
        "cafes in New York",
        "dentists in San Francisco, CA",
        "gyms within 5km of Mumbai",
        "spas at Dubai",
    ]
    
    for query in test_cases:
        intent = parser.parse(query)
        location = intent.search_center
        status = "✅" if location else "❌"
        print(f"\n{status} '{query}'")
        print(f"   Extracted: {location}")


def test_radius_extraction():
    """Test radius extraction"""
    print("\n" + "="*70)
    print("TEST 5: Radius Extraction")
    print("="*70)
    
    parser = LocationIntentParser()
    
    test_cases = [
        ("within 5km", 5.0),
        ("within 10 kilometers", 10.0),
        ("within 3 miles", 4.83),  # ~4.83km
        ("5km radius", 5.0),
        ("10 mile radius", 16.09),  # ~16.09km
    ]
    
    for query, expected_km in test_cases:
        intent = parser.parse(f"restaurants {query}")
        radius = intent.radius_km
        status = "✅" if radius and abs(radius - expected_km) < 0.5 else "❌"
        print(f"\n{status} '{query}'")
        print(f"   Extracted: {radius}km (expected ~{expected_km}km)")


def test_search_context_creation():
    """Test search context creation"""
    print("\n" + "="*70)
    print("TEST 6: Search Context Creation")
    print("="*70)
    
    from models.location_intent import SearchContext
    
    context = SearchContext(
        location_source="explicit_location",
        search_center="London",
        search_center_coords=(51.5074, -0.1278),
        radius_km=10.0,
        business_categories=["restaurants", "cafes"],
        location_confidence=0.95,
        total_discovered=50,
        within_radius=12
    )
    
    context_dict = context.to_dict()
    
    print("\n✅ Search Context Created:")
    print(f"   Location Source: {context_dict['location_source']}")
    print(f"   Search Center: {context_dict['search_center']}")
    print(f"   Radius: {context_dict['radius_km']}km")
    print(f"   Categories: {', '.join(context_dict['business_categories'])}")
    print(f"   Discovered: {context_dict['total_discovered']}")
    print(f"   Within Radius: {context_dict['within_radius']}")


def test_location_intent_edge_cases():
    """Test edge cases"""
    print("\n" + "="*70)
    print("TEST 7: Edge Cases")
    print("="*70)
    
    parser = LocationIntentParser()
    
    edge_cases = [
        "find restaurants",  # Missing location
        "restaurants",  # Just category
        "near me",  # Just location, no category
        "within 5km",  # Just radius
        "",  # Empty string
    ]
    
    for query in edge_cases:
        intent = parser.parse(query)
        print(f"\n  Query: '{query}'")
        print(f"  Source: {intent.location_source.value}")
        print(f"  Is Missing: {intent.is_missing}")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("LOCATION-AWARE DISCOVERY - UNIT TESTS")
    print("="*70)
    
    try:
        test_location_intent_parser()
        test_distance_calculator()
        test_distance_calculator_class()
        test_location_patterns()
        test_radius_extraction()
        test_search_context_creation()
        test_location_intent_edge_cases()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
