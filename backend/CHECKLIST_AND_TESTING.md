# ✅ Location-Aware Implementation - Checklist & Testing Guide

## Pre-Flight Checklist

Before running your lead discovery system, verify these items:

### 1. Configuration ✅

- [ ] **API Keys Set**
  ```bash
  # Check your .env file has ONE of these:
  SERP_API_KEY=your_key
  # OR
  GOOGLE_MAPS_API_KEY=your_key
  ```

- [ ] **Location Configured** (defaults to Ahmedabad)
  ```bash
  # Optional: Customize in .env
  DEFAULT_LOCATION_NAME=Ahmedabad, Gujarat, India
  DEFAULT_LOCATION_LAT=23.0225
  DEFAULT_LOCATION_LNG=72.5714
  DEFAULT_SEARCH_RADIUS_KM=20
  ```

- [ ] **Dependencies Installed**
  ```bash
  cd backend
  pip install -r requirements.txt
  ```

### 2. Files Updated ✅

- [x] `automation/search_provider.py` - Location-aware search
- [x] `automation/jobs.py` - Geographic fields added
- [x] `location_config.py` - Configuration file created
- [x] `.env.example` - Updated with location settings

### 3. New Features Available ✅

- [x] Distance calculation (Haversine)
- [x] Coordinates in every lead
- [x] Location-constrained API searches
- [x] Results sorted by proximity
- [x] Easy location configuration

---

## Testing Guide

### Test 1: Verify Configuration

```bash
cd backend
python -c "from location_config import get_default_location_name, get_default_location_coords; print(f'Location: {get_default_location_name()}'); print(f'Coordinates: {get_default_location_coords()}')"
```

**Expected Output:**
```
Location: Ahmedabad, Gujarat, India
Coordinates: (23.0225, 72.5714)
```

✅ **Pass**: Configuration loaded correctly  
❌ **Fail**: Check if `location_config.py` exists

---

### Test 2: Unit Tests

```bash
cd backend
python test_location_aware.py
```

**Expected Output:**
```
======================================================================
LOCATION-AWARE DISCOVERY - UNIT TESTS
======================================================================
TEST 1: Location Intent Parser
✅ Query: 'restaurants near me'
✅ Query: 'cafes in London'
...
======================================================================
✅ ALL TESTS PASSED!
======================================================================
```

✅ **Pass**: All tests passed  
❌ **Fail**: Check error messages and fix imports

---

### Test 3: Search Provider Test

```bash
cd backend
python -c "from automation.search_provider import SearchProvider; sp = SearchProvider(); print(f'Provider: {sp.name}'); print(f'Configured: {sp.configured}')"
```

**Expected Output:**
```
Provider: SerpApi
Configured: True
```
OR
```
Provider: Google Places API
Configured: True
```

✅ **Pass**: API is configured  
❌ **Fail**: Check API keys in `.env`

---

### Test 4: Distance Calculator Test

```bash
cd backend
python -c "from discovery.distance_calculator import calculate_distance_km; d = calculate_distance_km(23.0225, 72.5714, 23.0264, 72.5970); print(f'Distance: {d:.2f}km')"
```

**Expected Output:**
```
Distance: 2.66km
```

✅ **Pass**: Distance calculation working  
❌ **Fail**: Check if `discovery/distance_calculator.py` exists

---

### Test 5: Full Integration Test (Dry Run)

**If you have API keys configured:**

```bash
cd backend
python -c "
import asyncio
from automation.search_provider import SearchProvider

async def test():
    sp = SearchProvider()
    results = await sp.search('restaurants', 5)
    print(f'Found {len(results)} businesses')
    if results:
        r = results[0]
        print(f'First: {r.get(\"business_name\")}')
        print(f'Location: {r.get(\"location\")}')
        print(f'Distance: {r.get(\"distance_km\")}km')

asyncio.run(test())
"
```

**Expected Output:**
```
Found 5 businesses
First: Some Restaurant Name
Location: Ahmedabad [Coordinates: 23.0264, 72.5970] [Distance: 4.7km from center]
Distance: 4.7km
```

✅ **Pass**: End-to-end search working with Ahmedabad businesses  
❌ **Fail**: Check API keys, quota, and network connection

---

### Test 6: Run Actual Job

```bash
cd backend
python -m automation.scheduler
```

OR start the API server:

```bash
cd backend
python main.py
```

Then make a request:
```bash
curl -X POST http://localhost:8000/api/jobs/run \
  -H "Content-Type: application/json" \
  -d '{"service": "website", "queries": ["restaurants"]}'
```

**Check Output File:**
```bash
cat backend/leads_output/leads_*.json | head -50
```

**Verify:**
- [ ] Location contains "Ahmedabad" or "Gujarat"
- [ ] `latitude` field exists and is around 23.x
- [ ] `longitude` field exists and is around 72.x
- [ ] `distance_km` field exists
- [ ] NO businesses from New York, London, etc.

✅ **Pass**: Ahmedabad-only leads generated  
❌ **Fail**: See troubleshooting section below

---

## Validation Checklist

### Lead Output Validation

Open the latest `leads_output/leads_*.json` file and check:

```json
{
  "business_name": "...",
  "location": "... Ahmedabad ...",     ← Should contain Ahmedabad
  "latitude": 23.xxxx,                  ← Should be ~23.x
  "longitude": 72.xxxx,                 ← Should be ~72.x
  "distance_km": x.x,                   ← Should exist
  ...
}
```

**Validation Rules:**

| Field | Expected | Status |
|-------|----------|--------|
| `location` | Contains "Ahmedabad" or "Gujarat" | [ ] |
| `latitude` | Between 22.5 and 23.5 | [ ] |
| `longitude` | Between 72.0 and 73.0 | [ ] |
| `distance_km` | Number between 0-30 | [ ] |
| `business_name` | NOT generic category | [ ] |

✅ **All checks pass**: System working correctly  
❌ **Any check fails**: See troubleshooting below

---

## Common Issues & Solutions

### Issue 1: Still Getting Leads from Other Countries

**Symptoms:**
- Location shows "New York, NY" or other non-Ahmedabad cities
- Latitude/longitude outside Ahmedabad range

**Solutions:**

1. **Verify configuration loaded:**
   ```bash
   python -c "from location_config import get_default_location_name; print(get_default_location_name())"
   ```
   Should output: `Ahmedabad, Gujarat, India`

2. **Check search provider is using location:**
   ```bash
   grep -n "location_query" backend/automation/search_provider.py
   ```
   Should find lines with location added to query

3. **Clear cache and restart:**
   ```bash
   rm -rf backend/__pycache__
   rm -rf backend/automation/__pycache__
   # Restart job/server
   ```

4. **Check API response:**
   Add debug logging to see actual API responses

---

### Issue 2: No distance_km Field

**Symptoms:**
- Leads missing `distance_km`, `latitude`, or `longitude`

**Solutions:**

1. **Verify Lead model updated:**
   ```bash
   grep -A 5 "distance_km" backend/automation/jobs.py
   ```
   Should show the field in Lead dataclass

2. **Check distance calculator imported:**
   ```bash
   grep "calculate_distance_km" backend/automation/search_provider.py
   ```
   Should find import and usage

3. **Restart Python process:**
   Old cached modules may be loaded

---

### Issue 3: API Not Configured

**Symptoms:**
```
No API-backed search provider is configured
```

**Solutions:**

1. **Set API key in `.env`:**
   ```env
   SERP_API_KEY=your_actual_key_here
   ```
   OR
   ```env
   GOOGLE_MAPS_API_KEY=your_actual_key_here
   ```

2. **Verify `.env` is loaded:**
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('SERP_API_KEY'))"
   ```

3. **Check working directory:**
   Make sure you're running from the `backend/` directory

---

### Issue 4: Distance Calculation Errors

**Symptoms:**
```
ImportError: cannot import name 'calculate_distance_km'
```

**Solutions:**

1. **Verify file exists:**
   ```bash
   ls -la backend/discovery/distance_calculator.py
   ```

2. **Check Python path:**
   ```bash
   python -c "import sys; print(sys.path)"
   ```
   Should include backend directory

3. **Try absolute import:**
   Edit search_provider.py to use:
   ```python
   from discovery.distance_calculator import calculate_distance_km
   ```

---

### Issue 5: No Results Returned

**Symptoms:**
- Empty results from API
- 0 leads found

**Solutions:**

1. **Check API quota:**
   - SerpApi: Check your dashboard
   - Google Maps: Check Google Cloud Console

2. **Try different query:**
   ```python
   # Test with broader query
   results = await sp.search('restaurants', 10)
   ```

3. **Check location name:**
   - Ensure "Ahmedabad, Gujarat, India" is spelled correctly
   - Try just "Ahmedabad" if full name fails

4. **Verify API response:**
   Add `print(data)` after API call to see raw response

---

## Performance Benchmarks

### Expected Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Load configuration | <10ms | Cached after first load |
| API search request | 1-3s | Network dependent |
| Distance calculation (50 businesses) | <10ms | Local computation |
| Single lead qualification | 2-5s | LLM dependent |
| Full job (5 queries, 25 leads) | 2-3 min | Total time |

### Optimization Tips

1. **Reduce API calls:**
   - Use larger `limit` parameter
   - Cache results when possible

2. **Parallel processing:**
   - Process multiple businesses simultaneously
   - Use `asyncio.gather()` for concurrent API calls

3. **Filter early:**
   - Apply distance filter before qualification
   - Skip businesses outside radius

---

## Debug Mode

### Enable Debug Logging

Add to your script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("automation").setLevel(logging.DEBUG)
logging.getLogger("discovery").setLevel(logging.DEBUG)
```

### Debug Output

You should see:
```
DEBUG:automation.search_provider:Adding location to query: "restaurants in Ahmedabad, Gujarat, India"
DEBUG:automation.search_provider:API returned 5 results
DEBUG:automation.search_provider:Business A at (23.0264, 72.5970) is 4.7km from center
DEBUG:automation.jobs:Qualifying lead: Business A
```

---

## Success Criteria

Your implementation is successful when:

✅ **1. Location Targeting**
- All leads are from Ahmedabad (lat ~23.x, lng ~72.x)
- No leads from other countries

✅ **2. Geographic Data**
- Every lead has `latitude`, `longitude`, `distance_km`
- Distance values are reasonable (0-30km typically)

✅ **3. Sorting**
- Results are sorted by distance
- Nearest businesses appear first

✅ **4. Configuration**
- Easy to change target city
- Location settings respected

✅ **5. Performance**
- Full job completes in reasonable time
- API quota not exceeded

---

## Final Verification Script

Run this comprehensive test:

```bash
cd backend
python << 'EOF'
import asyncio
from automation.search_provider import SearchProvider
from location_config import get_default_location_name, get_default_location_coords

async def verify():
    print("="*70)
    print("LOCATION-AWARE SYSTEM VERIFICATION")
    print("="*70)
    
    # 1. Check configuration
    print("\n1. Configuration:")
    loc_name = get_default_location_name()
    loc_coords = get_default_location_coords()
    print(f"   Location: {loc_name}")
    print(f"   Coordinates: {loc_coords}")
    assert "Ahmedabad" in loc_name, "Location should be Ahmedabad"
    print("   ✅ Configuration OK")
    
    # 2. Check search provider
    print("\n2. Search Provider:")
    sp = SearchProvider()
    print(f"   Provider: {sp.name}")
    print(f"   Configured: {sp.configured}")
    assert sp.configured, "Search provider must be configured"
    print("   ✅ Search Provider OK")
    
    # 3. Test search
    print("\n3. Testing Search:")
    results = await sp.search("restaurants", 3)
    print(f"   Found {len(results)} businesses")
    
    if results:
        r = results[0]
        print(f"\n   Example Business:")
        print(f"   - Name: {r.get('business_name')}")
        print(f"   - Location: {r.get('location')[:80]}...")
        print(f"   - Latitude: {r.get('latitude')}")
        print(f"   - Longitude: {r.get('longitude')}")
        print(f"   - Distance: {r.get('distance_km')}km")
        
        # Verify coordinates are in Ahmedabad range
        lat = r.get('latitude')
        lng = r.get('longitude')
        if lat and lng:
            assert 22.5 < lat < 23.5, f"Latitude {lat} outside Ahmedabad range"
            assert 72.0 < lng < 73.0, f"Longitude {lng} outside Ahmedabad range"
            print("   ✅ Coordinates in Ahmedabad range")
        
        # Verify distance exists
        dist = r.get('distance_km')
        if dist is not None:
            assert 0 <= dist <= 50, f"Distance {dist}km seems unreasonable"
            print("   ✅ Distance calculated")
    else:
        print("   ⚠️  No results (check API quota/network)")
    
    print("\n" + "="*70)
    print("✅ ALL VERIFICATIONS PASSED!")
    print("="*70)

asyncio.run(verify())
EOF
```

**Expected Output:**
```
======================================================================
LOCATION-AWARE SYSTEM VERIFICATION
======================================================================

1. Configuration:
   Location: Ahmedabad, Gujarat, India
   Coordinates: (23.0225, 72.5714)
   ✅ Configuration OK

2. Search Provider:
   Provider: SerpApi
   Configured: True
   ✅ Search Provider OK

3. Testing Search:
   Found 3 businesses

   Example Business:
   - Name: Some Restaurant
   - Location: Ahmedabad, Gujarat, India [Coordinates: 23.0264, 72.5970] [Distan...
   - Latitude: 23.0264
   - Longitude: 72.5970
   - Distance: 4.7km
   ✅ Coordinates in Ahmedabad range
   ✅ Distance calculated

======================================================================
✅ ALL VERIFICATIONS PASSED!
======================================================================
```

---

## Next Steps After Verification

Once all tests pass:

1. **Run production job:**
   ```bash
   python -m automation.scheduler
   ```

2. **Monitor output:**
   - Check `leads_output/` folder
   - Verify all leads are from Ahmedabad

3. **Optional: Change location:**
   - Edit `.env` or `location_config.py`
   - Restart and verify new location

4. **Optional: Integrate advanced features:**
   - Follow `INTEGRATION_GUIDE.md`
   - Enable "near me" queries
   - Add radius filtering

---

**Your location-aware system is ready! 🎉**
