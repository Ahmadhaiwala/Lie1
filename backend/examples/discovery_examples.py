"""
Discovery Module Examples
Demonstrates business discovery, enrichment, and deduplication
"""
import asyncio
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.business import Business, BusinessContact, BusinessLocation
from models.search_intent import SearchIntent, SearchQuery, SearchType
from discovery import BusinessDiscovery, LocationResolver, WebsiteResolver, Deduplicator


async def example_business_discovery():
    """Example: Discover businesses based on search intent"""
    print("\n=== Business Discovery Example ===")
    
    # Create search intent
    search_intent = SearchIntent(
        raw_input="coffee shops in San Francisco",
        industry="Food & Beverage",
        location="San Francisco, CA",
        keywords=["coffee", "cafe"],
        queries=[
            SearchQuery(
                query="coffee shops San Francisco",
                search_type=SearchType.COMBINED,
                location="San Francisco, CA",
                max_results=10
            )
        ]
    )
    
    # Discover businesses
    discovery = BusinessDiscovery()
    businesses = await discovery.discover(
        search_intent,
        sources=["google_maps", "yelp"],
        max_results=15
    )
    
    print(f"✓ Discovered {len(businesses)} businesses")
    
    for i, business in enumerate(businesses[:5], 1):
        print(f"\n{i}. {business.name}")
        print(f"   Source: {business.source}")
        print(f"   Email: {business.contact.email}")
        print(f"   Phone: {business.contact.phone}")
        if business.locations:
            loc = business.locations[0]
            print(f"   Location: {loc.city}, {loc.state}")


async def example_business_enrichment():
    """Example: Enrich business with LLM"""
    print("\n=== Business Enrichment Example ===")
    
    # Create a basic business
    business = Business(
        name="Blue Bottle Coffee",
        contact=BusinessContact(
            website="https://bluebottlecoffee.com"
        ),
        locations=[
            BusinessLocation(
                city="San Francisco",
                state="CA",
                country="USA"
            )
        ]
    )
    
    print(f"Before enrichment:")
    print(f"  Description: {business.description}")
    print(f"  Industry: {business.industry}")
    
    # Enrich the business
    discovery = BusinessDiscovery()
    enriched = await discovery.enrich_business(business)
    
    print(f"\nAfter enrichment:")
    print(f"  Description: {enriched.description}")
    print(f"  Industry: {enriched.industry}")
    print(f"  Status: {enriched.status}")


async def example_location_resolution():
    """Example: Resolve and geocode locations"""
    print("\n=== Location Resolution Example ===")
    
    resolver = LocationResolver()
    
    # Resolve location
    location = await resolver.resolve_location("San Francisco, CA")
    
    print(f"✓ Resolved location:")
    print(f"  City: {location.city}")
    print(f"  State: {location.state}")
    print(f"  Country: {location.country}")
    print(f"  Coordinates: ({location.latitude}, {location.longitude})")
    
    # Calculate distance between two locations
    location2 = await resolver.resolve_location("Los Angeles, CA")
    
    distance = resolver.calculate_distance(location, location2)
    print(f"\n✓ Distance from SF to LA: {distance:.2f} miles")


async def example_website_resolution():
    """Example: Find and validate business websites"""
    print("\n=== Website Resolution Example ===")
    
    resolver = WebsiteResolver()
    
    # Generate website candidates
    business_name = "Acme Coffee Shop"
    candidates = resolver._generate_website_candidates(business_name)
    
    print(f"✓ Generated {len(candidates)} website candidates for '{business_name}':")
    for candidate in candidates[:5]:
        print(f"  - {candidate}")
    
    # Validate a website
    test_url = "https://example.com"
    is_valid = await resolver.validate_website(test_url, check_content=False)
    print(f"\n✓ Validation for {test_url}: {'Valid' if is_valid else 'Invalid'}")
    
    # Extract contact info (mock example)
    html_sample = """
    <html>
    <body>
        <p>Contact us at info@acmecoffee.com or call (555) 123-4567</p>
        <a href="https://facebook.com/acmecoffee">Facebook</a>
        <a href="https://twitter.com/acmecoffee">Twitter</a>
    </body>
    </html>
    """
    
    emails = resolver._extract_emails(html_sample)
    phones = resolver._extract_phones(html_sample)
    social = resolver._extract_social_media(html_sample)
    
    print(f"\n✓ Extracted contact information:")
    print(f"  Emails: {emails}")
    print(f"  Phones: {phones}")
    print(f"  Social Media: {list(social.keys())}")


async def example_deduplication():
    """Example: Deduplicate business records"""
    print("\n=== Deduplication Example ===")
    
    # Create some duplicate businesses
    businesses = [
        Business(
            name="Acme Coffee",
            contact=BusinessContact(
                email="info@acmecoffee.com",
                phone="+1-555-0100"
            ),
            locations=[BusinessLocation(city="San Francisco", state="CA")]
        ),
        Business(
            name="Acme Coffee Shop",  # Similar name
            contact=BusinessContact(
                email="info@acmecoffee.com",  # Same email
                phone="+1-555-0100"
            ),
            locations=[BusinessLocation(city="San Francisco", state="CA")]
        ),
        Business(
            name="Blue Bottle Coffee",  # Different business
            contact=BusinessContact(
                email="contact@bluebottle.com"
            ),
            locations=[BusinessLocation(city="Oakland", state="CA")]
        ),
        Business(
            name="Acme Coffee",  # Exact duplicate
            contact=BusinessContact(
                email="info@acmecoffee.com",
                phone="+1-555-0100"
            ),
            locations=[BusinessLocation(city="San Francisco", state="CA")]
        ),
    ]
    
    print(f"Before deduplication: {len(businesses)} businesses")
    
    # Deduplicate
    dedup = Deduplicator(similarity_threshold=0.85)
    unique_businesses = await dedup.deduplicate(businesses)
    
    print(f"After deduplication: {len(unique_businesses)} unique businesses")
    
    print(f"\nUnique businesses:")
    for i, business in enumerate(unique_businesses, 1):
        print(f"  {i}. {business.name} - {business.contact.email}")


async def example_similarity_scoring():
    """Example: Calculate similarity between businesses"""
    print("\n=== Similarity Scoring Example ===")
    
    business1 = Business(
        name="Acme Coffee Shop",
        contact=BusinessContact(
            email="info@acmecoffee.com",
            phone="+1-555-0100"
        ),
        locations=[BusinessLocation(city="San Francisco", state="CA")]
    )
    
    business2 = Business(
        name="Acme Coffee",
        contact=BusinessContact(
            email="info@acmecoffee.com",
            phone="+1-555-0100"
        ),
        locations=[BusinessLocation(city="San Francisco", state="CA")]
    )
    
    business3 = Business(
        name="Blue Bottle Coffee",
        contact=BusinessContact(
            email="contact@bluebottle.com"
        ),
        locations=[BusinessLocation(city="Oakland", state="CA")]
    )
    
    dedup = Deduplicator()
    
    sim_1_2 = dedup.calculate_similarity(business1, business2)
    sim_1_3 = dedup.calculate_similarity(business1, business3)
    
    print(f"✓ Similarity scores:")
    print(f"  Acme Coffee Shop vs Acme Coffee: {sim_1_2:.2%}")
    print(f"  Acme Coffee Shop vs Blue Bottle: {sim_1_3:.2%}")


async def example_full_discovery_workflow():
    """Example: Complete discovery workflow"""
    print("\n=== Full Discovery Workflow ===")
    
    # Step 1: Create search intent
    print("Step 1: Creating search intent...")
    search_intent = SearchIntent(
        raw_input="specialty coffee roasters in Bay Area",
        industry="Food & Beverage",
        location="San Francisco Bay Area, CA",
        keywords=["coffee", "roaster", "specialty"],
        queries=[
            SearchQuery(
                query="specialty coffee roasters Bay Area",
                search_type=SearchType.COMBINED,
                location="San Francisco Bay Area, CA",
                max_results=20
            )
        ]
    )
    
    # Step 2: Discover businesses
    print("Step 2: Discovering businesses...")
    discovery = BusinessDiscovery()
    businesses = await discovery.discover(search_intent, max_results=20)
    print(f"  ✓ Found {len(businesses)} businesses")
    
    # Step 3: Deduplicate
    print("Step 3: Deduplicating...")
    dedup = Deduplicator()
    unique_businesses = await dedup.deduplicate(businesses)
    print(f"  ✓ Reduced to {len(unique_businesses)} unique businesses")
    
    # Step 4: Enrich top businesses
    print("Step 4: Enriching top 3 businesses...")
    for i, business in enumerate(unique_businesses[:3], 1):
        enriched = await discovery.enrich_business(business)
        print(f"  {i}. {enriched.name}")
        print(f"     Industry: {enriched.industry}")
        print(f"     Description: {enriched.description[:80]}...")
    
    print(f"\n✓ Workflow complete!")
    print(f"  Total discovered: {len(businesses)}")
    print(f"  Unique: {len(unique_businesses)}")
    print(f"  Enriched: 3")


async def main():
    """Run all examples"""
    print("=" * 60)
    print("Discovery Module Examples")
    print("=" * 60)
    
    try:
        # Run examples
        await example_business_discovery()
        await example_business_enrichment()
        await example_location_resolution()
        await example_website_resolution()
        await example_deduplication()
        await example_similarity_scoring()
        await example_full_discovery_workflow()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
