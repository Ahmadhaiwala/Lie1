"""
Test cases for Discovery Module
"""
import pytest
import asyncio
from datetime import datetime

from models.business import Business, BusinessContact, BusinessLocation
from models.search_intent import SearchIntent, SearchQuery, SearchType
from discovery import BusinessDiscovery, LocationResolver, WebsiteResolver, Deduplicator


class TestBusinessDiscovery:
    """Test suite for BusinessDiscovery"""
    
    @pytest.mark.asyncio
    async def test_discover_businesses(self):
        """Test business discovery"""
        discovery = BusinessDiscovery()
        
        search_intent = SearchIntent(
            raw_input="coffee shops in San Francisco",
            industry="Food & Beverage",
            location="San Francisco, CA",
            keywords=["coffee"],
            queries=[
                SearchQuery(
                    query="coffee shops San Francisco",
                    search_type=SearchType.COMBINED,
                    location="San Francisco, CA"
                )
            ]
        )
        
        businesses = await discovery.discover(search_intent, max_results=10)
        
        assert len(businesses) > 0
        assert all(isinstance(b, Business) for b in businesses)
    
    @pytest.mark.asyncio
    async def test_enrich_business(self):
        """Test business enrichment"""
        discovery = BusinessDiscovery()
        
        business = Business(
            name="Test Coffee Shop",
            contact=BusinessContact(),
            locations=[BusinessLocation(city="San Francisco", state="CA")]
        )
        
        enriched = await discovery.enrich_business(business)
        
        assert enriched.description is not None
        assert len(enriched.description) > 0


class TestLocationResolver:
    """Test suite for LocationResolver"""
    
    @pytest.mark.asyncio
    async def test_resolve_location(self):
        """Test location resolution"""
        resolver = LocationResolver()
        
        location = await resolver.resolve_location("San Francisco, CA")
        
        assert location is not None
        assert location.city == "San Francisco"
        assert location.state == "CA"
    
    def test_parse_location_string(self):
        """Test location string parsing"""
        resolver = LocationResolver()
        
        components = resolver._parse_location_string("San Francisco, CA, USA")
        
        assert components["city"] == "San Francisco"
        assert components["state"] == "CA"
        assert components["country"] == "USA"
    
    def test_normalize_location_string(self):
        """Test location normalization"""
        resolver = LocationResolver()
        
        normalized = resolver.normalize_location_string("  San Francisco, CA  ")
        
        assert normalized == "San Francisco, California"
    
    def test_calculate_distance(self):
        """Test distance calculation"""
        resolver = LocationResolver()
        
        loc1 = BusinessLocation(
            city="San Francisco",
            latitude=37.7749,
            longitude=-122.4194
        )
        loc2 = BusinessLocation(
            city="Los Angeles",
            latitude=34.0522,
            longitude=-118.2437
        )
        
        distance = resolver.calculate_distance(loc1, loc2)
        
        assert distance is not None
        assert 340 < distance < 360  # ~347 miles


class TestWebsiteResolver:
    """Test suite for WebsiteResolver"""
    
    def test_generate_website_candidates(self):
        """Test website candidate generation"""
        resolver = WebsiteResolver()
        
        candidates = resolver._generate_website_candidates("Acme Coffee")
        
        assert len(candidates) > 0
        assert "https://www.acmecoffee.com" in candidates or "https://acmecoffee.com" in candidates
    
    def test_extract_emails(self):
        """Test email extraction"""
        resolver = WebsiteResolver()
        
        html = """
        <html>
        <body>
        Contact us at info@example.com or sales@example.com
        </body>
        </html>
        """
        
        emails = resolver._extract_emails(html)
        
        assert len(emails) > 0
        assert "info@example.com" in emails
    
    def test_extract_phones(self):
        """Test phone extraction"""
        resolver = WebsiteResolver()
        
        html = "Call us at (555) 123-4567 or 555-987-6543"
        
        phones = resolver._extract_phones(html)
        
        assert len(phones) > 0
    
    def test_normalize_url(self):
        """Test URL normalization"""
        resolver = WebsiteResolver()
        
        normalized = resolver.normalize_url("www.example.com")
        
        assert normalized == "https://example.com"


class TestDeduplicator:
    """Test suite for Deduplicator"""
    
    @pytest.mark.asyncio
    async def test_exact_duplicates(self):
        """Test exact duplicate removal"""
        dedup = Deduplicator()
        
        business1 = Business(
            name="Acme Coffee",
            contact=BusinessContact(email="info@acme.com"),
            locations=[BusinessLocation(city="SF")]
        )
        business2 = Business(
            name="Acme Coffee",
            contact=BusinessContact(email="info@acme.com"),
            locations=[BusinessLocation(city="SF")]
        )
        
        unique = await dedup.deduplicate([business1, business2])
        
        assert len(unique) == 1
    
    def test_calculate_similarity(self):
        """Test similarity calculation"""
        dedup = Deduplicator()
        
        business1 = Business(
            name="Acme Coffee Shop",
            contact=BusinessContact(email="info@acme.com"),
            locations=[BusinessLocation(city="San Francisco")]
        )
        business2 = Business(
            name="Acme Coffee",
            contact=BusinessContact(email="info@acme.com"),
            locations=[BusinessLocation(city="San Francisco")]
        )
        
        similarity = dedup.calculate_similarity(business1, business2)
        
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.7  # Should be similar
    
    def test_merge_businesses(self):
        """Test business merging"""
        dedup = Deduplicator()
        
        primary = Business(
            name="Acme Coffee",
            contact=BusinessContact(email="info@acme.com"),
            locations=[]
        )
        duplicate = Business(
            name="Acme Coffee",
            contact=BusinessContact(phone="+1-555-0123"),
            locations=[BusinessLocation(city="SF")]
        )
        
        merged = dedup.merge_businesses(primary, duplicate)
        
        assert merged.contact.email == "info@acme.com"
        assert merged.contact.phone == "+1-555-0123"
        assert len(merged.locations) == 1
