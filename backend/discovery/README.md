# Discovery Module

The Discovery module is responsible for finding, enriching, and deduplicating business records.

## Components

### 1. BusinessDiscovery
Discovers businesses from multiple sources based on search intent.

**Features:**
- Multi-source discovery (Google Maps, Yelp, Web Search)
- LLM-powered enrichment
- Industry classification
- Caching for performance

**Usage:**
```python
from discovery import BusinessDiscovery
from models.search_intent import SearchIntent

discovery = BusinessDiscovery()

search_intent = SearchIntent(
    raw_input="coffee shops in San Francisco",
    industry="Food & Beverage",
    location="San Francisco, CA"
)

businesses = await discovery.discover(search_intent, max_results=50)
```

### 2. LocationResolver
Resolves and normalizes location data with geocoding support.

**Features:**
- Location string parsing
- Geocoding (coordinates)
- Distance calculation
- Radius-based filtering

**Usage:**
```python
from discovery import LocationResolver

resolver = LocationResolver()

location = await resolver.resolve_location("San Francisco, CA")
print(f"Coordinates: {location.latitude}, {location.longitude}")

# Calculate distance
distance = resolver.calculate_distance(location1, location2)
print(f"Distance: {distance} miles")
```

### 3. WebsiteResolver
Finds and validates business websites, extracts contact information.

**Features:**
- Website candidate generation
- URL validation
- Contact info extraction (emails, phones, social media)
- URL normalization

**Usage:**
```python
from discovery import WebsiteResolver

resolver = WebsiteResolver(crawler)

# Find website
website = await resolver.resolve_website(
    "Acme Coffee Shop",
    location="San Francisco, CA"
)

# Extract contact info
contact_info = await resolver.extract_contact_info(website)
print(f"Emails: {contact_info['emails']}")
```

### 4. Deduplicator
Identifies and merges duplicate business records.

**Features:**
- Exact duplicate detection (hash-based)
- Fuzzy matching (similarity-based)
- Configurable similarity threshold
- Smart merging

**Usage:**
```python
from discovery import Deduplicator

dedup = Deduplicator(similarity_threshold=0.85)

# Remove duplicates
unique_businesses = await dedup.deduplicate(businesses)

# Merge two businesses
merged = dedup.merge_businesses(primary, duplicate)
```

## Models

### Business
Core business entity with contact, location, and metadata.

```python
from models.business import Business, BusinessContact, BusinessLocation

business = Business(
    name="Acme Coffee",
    description="Specialty coffee shop",
    industry="Food & Beverage",
    contact=BusinessContact(
        email="info@acme.com",
        phone="+1-555-0123",
        website="https://acmecoffee.com"
    ),
    locations=[
        BusinessLocation(
            city="San Francisco",
            state="CA",
            latitude=37.7749,
            longitude=-122.4194
        )
    ]
)
```

### SearchIntent
Parsed search intent with query strategies.

```python
from models.search_intent import SearchIntent, SearchQuery, SearchType

intent = SearchIntent(
    raw_input="coffee shops in San Francisco",
    industry="Food & Beverage",
    location="San Francisco, CA",
    keywords=["coffee", "cafe"],
    queries=[
        SearchQuery(
            query="coffee shops San Francisco",
            search_type=SearchType.COMBINED,
            location="San Francisco, CA",
            max_results=20
        )
    ]
)
```

## Integration Points

### With Crawler
```python
from crawler import WebCrawler, CrawlerConfig
from discovery import WebsiteResolver

crawler_config = CrawlerConfig(headless=True)
async with WebCrawler(crawler_config) as crawler:
    resolver = WebsiteResolver(crawler)
    contact_info = await resolver.extract_contact_info(url)
```

### With LLM
```python
from llm import LLMClient
from discovery import BusinessDiscovery

llm_client = LLMClient()
discovery = BusinessDiscovery(llm_client)

enriched = await discovery.enrich_business(business)
```

## Testing

Run discovery tests:
```bash
pytest tests/test_discovery.py -v
```

## Future Enhancements

### Planned Features
- [ ] Real API integrations (Google Maps, Yelp, etc.)
- [ ] Advanced geocoding with multiple providers
- [ ] Machine learning-based deduplication
- [ ] Website content scoring
- [ ] Bulk discovery operations
- [ ] Advanced caching strategies
- [ ] Rate limiting and retry logic
- [ ] Parallel discovery from multiple sources

### API Integrations Needed
1. **Google Maps Places API** - Business discovery
2. **Yelp Fusion API** - Business discovery
3. **Clearbit API** - Business enrichment
4. **Hunter.io API** - Email finding
5. **Geocoding APIs** - Location resolution

## Architecture Notes

### Caching Strategy
- In-memory caching for session-based operations
- Redis integration for persistent caching (planned)
- TTL-based cache invalidation

### Error Handling
- Graceful degradation when APIs are unavailable
- Retry logic with exponential backoff
- Fallback to mock data for development

### Performance
- Async/await for concurrent operations
- Batch processing support
- Configurable rate limiting

## Configuration

Environment variables:
```bash
# Discovery settings
DISCOVERY_MAX_RESULTS=50
DISCOVERY_CACHE_TTL=3600

# API Keys (when integrated)
GOOGLE_MAPS_API_KEY=your-key-here
YELP_API_KEY=your-key-here
CLEARBIT_API_KEY=your-key-here
```

## Examples

See `examples/discovery_examples.py` for complete working examples.
