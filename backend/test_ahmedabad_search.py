"""
Quick Test - Verify Ahmedabad Location is Working
--------------------------------------------------
Run this to test if the location-aware search is active.
"""
import asyncio
import sys
import os

# Ensure backend is in path
sys.path.insert(0, os.path.dirname(__file__))

from automation.search_provider import SearchProvider
from location_config import get_default_location_name, get_default_location_coords


async def test_ahmedabad_search():
    print("\n" + "="*70)
    print("TESTING AHMEDABAD LOCATION-AWARE SEARCH")
    print("="*70)
    
    # 1. Check configuration
    print("\n📍 Step 1: Checking Configuration...")
    loc_name = get_default_location_name()
    loc_coords = get_default_location_coords()
    print(f"   Target Location: {loc_name}")
    print(f"   Coordinates: {loc_coords}")
    
    if "Ahmedabad" not in loc_name:
        print("   ⚠️  WARNING: Location is not set to Ahmedabad!")
        print("   Edit location_config.py to fix this.")
        return False
    else:
        print("   ✅ Configuration: Ahmedabad")
    
    # 2. Check search provider
    print("\n🔍 Step 2: Checking Search Provider...")
    sp = SearchProvider()
    print(f"   Provider: {sp.name}")
    print(f"   Configured: {sp.configured}")
    
    if not sp.configured:
        print("   ❌ ERROR: No API key configured!")
        print("   Set SERP_API_KEY or GOOGLE_MAPS_API_KEY in .env")
        return False
    else:
        print("   ✅ Search Provider: Ready")
    
    # 3. Test actual search
    print("\n🌐 Step 3: Testing Live Search...")
    print("   Searching for: 'restaurants'")
    print("   Expected location: Ahmedabad, India")
    print("   Please wait...")
    
    try:
        results = await sp.search("restaurants", 3)
        print(f"\n   📊 Results: Found {len(results)} businesses")
        
        if not results:
            print("   ⚠️  No results returned (check API quota/network)")
            return False
        
        # 4. Verify results
        print("\n✅ Step 4: Verifying Results...")
        
        ahmedabad_count = 0
        other_count = 0
        
        for i, business in enumerate(results, 1):
            name = business.get('business_name', 'Unknown')
            location = business.get('location', '')
            lat = business.get('latitude')
            lng = business.get('longitude')
            distance = business.get('distance_km')
            
            # Check if location is in Ahmedabad
            is_ahmedabad = False
            if lat and lng:
                # Ahmedabad rough bounds: lat 22.5-23.5, lng 72-73
                if 22.5 <= lat <= 23.5 and 72.0 <= lng <= 73.0:
                    is_ahmedabad = True
                    ahmedabad_count += 1
                else:
                    other_count += 1
            
            status = "✅" if is_ahmedabad else "❌"
            
            print(f"\n   {status} Business {i}: {name}")
            print(f"      Location: {location[:60]}...")
            if lat and lng:
                print(f"      Coordinates: ({lat:.4f}, {lng:.4f})")
            if distance is not None:
                print(f"      Distance: {distance:.1f}km from center")
            
            if not is_ahmedabad:
                print(f"      ⚠️  NOT in Ahmedabad range!")
        
        # 5. Final verdict
        print("\n" + "="*70)
        print("RESULTS SUMMARY")
        print("="*70)
        print(f"   Ahmedabad businesses: {ahmedabad_count}")
        print(f"   Other locations: {other_count}")
        
        if ahmedabad_count == len(results):
            print("\n   ✅ SUCCESS! All businesses are from Ahmedabad!")
            print("   Your location-aware search is working correctly.")
            return True
        elif ahmedabad_count > 0:
            print("\n   ⚠️  PARTIAL: Some businesses from Ahmedabad, some from elsewhere")
            print("   This might be an API issue. Try running again.")
            return False
        else:
            print("\n   ❌ FAILED! No businesses from Ahmedabad found!")
            print("\n   TROUBLESHOOTING:")
            print("   1. Make sure you saved all file changes")
            print("   2. Restart Python (kill any running processes)")
            print("   3. Check if search_provider.py has the location code")
            print("   4. Try: grep -n 'location_query' automation/search_provider.py")
            return False
            
    except Exception as e:
        print(f"\n   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    success = await test_ahmedabad_search()
    
    if success:
        print("\n" + "="*70)
        print("🎉 AHMEDABAD LOCATION IS ACTIVE!")
        print("="*70)
        print("\nYou can now run your jobs and get Ahmedabad businesses.")
        print("\nNext steps:")
        print("  1. Run your scheduler: python -m automation.scheduler")
        print("  2. Check leads_output/ for Ahmedabad businesses")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("❌ AHMEDABAD LOCATION NOT WORKING YET")
        print("="*70)
        print("\nPlease:")
        print("  1. Make sure all code changes are saved")
        print("  2. Restart any running Python processes")
        print("  3. Re-run this test")
        print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
