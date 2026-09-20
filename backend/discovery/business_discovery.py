"""
Business Discovery Engine
Discovers businesses based on search intent using multiple sources
"""
import asyncio
from typing import List, Optional, Dict, Any
import hashlib
import json
from datetime import datetime

from models.business import Business, BusinessContact, BusinessLocation, BusinessStatus
from models.search_intent import SearchIntent, SearchQuery
from llm import LLMClient


class BusinessDiscovery:
    """Discovers businesses from various sources"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize business discovery
        
        Args:
            llm_client: LLM client for enrichment
        """
        self.llm_client = llm_client or LLMClient()
        self._cache: Dict[str, List[Business]] = {}
    
    async def discover(
        self,
        search_intent: SearchIntent,
        sources: Optional[List[str]] = None,
        max_results: int = 50
    ) -> List[Business]:
        """
        Discover businesses based on search intent
        
        Args:
            search_intent: Parsed search intent
            sources: List of sources to use (google_maps, yelp, etc.)
            max_results: Maximum number of businesses to return
            
        Returns:
            List of discovered businesses
        """
        if sources is None:
            sources = ["google_maps", "yelp", "web_search"]
        
        # Check cache
        cache_key = self._generate_cache_key(search_intent)
        if cache_key in self._cache:
            return self._cache[cache_key][:max_results]
        
        businesses = []
        
        # Execute queries from each source
        for source in sources:
            if source == "google_maps":
                results = await self._discover_from_google_maps(search_intent)
            elif source == "yelp":
                results = await self._discover_from_yelp(search_intent)
            elif source == "web_search":
                results = await self._discover_from_web_search(search_intent)
            else:
                continue
            
            businesses.extend(results)
        
        # Cache results
        self._cache[cache_key] = businesses
        
        return businesses[:max_results]
    
    async def _discover_from_google_maps(
        self,
        search_intent: SearchIntent
    ) -> List[Business]:
        """
        Discover businesses from Google Maps
        
        Note: In production, this would use Google Maps Places API
        For now, returns mock data
        """
        businesses = []
        
        for query in search_intent.queries:
            # Mock implementation
            # In production: Use Google Maps Places API
            mock_businesses = self._generate_mock_businesses(
                query.query,
                query.location,
                source="google_maps",
                count=5
            )
            businesses.extend(mock_businesses)
        
        return businesses
    
    async def _discover_from_yelp(
        self,
        search_intent: SearchIntent
    ) -> List[Business]:
        """
        Discover businesses from Yelp
        
        Note: In production, this would use Yelp Fusion API
        """
        businesses = []
        
        for query in search_intent.queries:
            # Mock implementation
            # In production: Use Yelp Fusion API
            mock_businesses = self._generate_mock_businesses(
                query.query,
                query.location,
                source="yelp",
                count=3
            )
            businesses.extend(mock_businesses)
        
        return businesses
    
    async def _discover_from_web_search(
        self,
        search_intent: SearchIntent
    ) -> List[Business]:
        """
        Discover businesses from general web search
        
        Uses LLM to extract business information from search results
        """
        businesses = []
        
        # Mock implementation
        # In production: Use web search API + LLM extraction
        for query in search_intent.queries:
            mock_businesses = self._generate_mock_businesses(
                query.query,
                query.location,
                source="web_search",
                count=2
            )
            businesses.extend(mock_businesses)
        
        return businesses
    
    async def enrich_business(
        self,
        business: Business,
        enrich_fields: Optional[List[str]] = None
    ) -> Business:
        """
        Enrich business with additional data
        
        Args:
            business: Business to enrich
            enrich_fields: Specific fields to enrich (None = all)
            
        Returns:
            Enriched business
        """
        if enrich_fields is None:
            enrich_fields = ["description", "industry", "technologies"]
        
        # Use LLM to generate enrichment
        if "description" in enrich_fields and not business.description:
            business.description = await self._generate_description(business)
        
        if "industry" in enrich_fields and not business.industry:
            business.industry = await self._classify_industry(business)
        
        business.status = BusinessStatus.ENRICHED
        business.updated_at = datetime.utcnow()
        
        return business
    
    async def _generate_description(self, business: Business) -> str:
        """Generate business description using LLM"""
        prompt = f"Generate a brief one-sentence description for a business named '{business.name}'"
        if business.industry:
            prompt += f" in the {business.industry} industry"
        if business.locations:
            loc = business.locations[0]
            if loc.city:
                prompt += f" located in {loc.city}"
        
        description = await self.llm_client.complete(
            prompt=prompt,
            max_tokens=100
        )
        
        return description.strip()
    
    async def _classify_industry(self, business: Business) -> str:
        """Classify business industry using LLM"""
        context = f"Business name: {business.name}"
        if business.description:
            context += f"\nDescription: {business.description}"
        
        prompt = """Based on the business information, classify it into ONE of these industries:
        - Retail
        - Food & Beverage
        - Healthcare
        - Professional Services
        - Technology
        - Education
        - Real Estate
        - Automotive
        - Entertainment
        - Other
        
        Return only the industry name."""
        
        industry = await self.llm_client.complete_with_context(
            prompt=prompt,
            context=context,
            max_tokens=20
        )
        
        return industry.strip()
    
    def _generate_mock_businesses(
        self,
        query: str,
        location: Optional[str],
        source: str,
        count: int = 5
    ) -> List[Business]:
        """Generate mock businesses for testing"""
        businesses = []
        
        for i in range(count):
            # Generate deterministic ID based on query and index
            business_id = hashlib.md5(
                f"{query}{location}{source}{i}".encode()
            ).hexdigest()[:12]
            
            business = Business(
                id=f"biz_{business_id}",
                name=f"{query.title()} Business {i+1}",
                description=f"A business discovered from {source}",
                industry="Unknown",
                contact=BusinessContact(
                    email=f"contact{i+1}@business{i+1}.com",
                    phone=f"+1-555-{1000+i:04d}",
                    website=f"https://business{i+1}.example.com"
                ),
                locations=[
                    BusinessLocation(
                        city=location.split(",")[0] if location and "," in location else location,
                        state=location.split(",")[1].strip() if location and "," in location else None,
                        country="USA"
                    )
                ] if location else [],
                source=source,
                source_id=f"{source}_{business_id}",
                status=BusinessStatus.DISCOVERED
            )
            
            businesses.append(business)
        
        return businesses
    
    def _generate_cache_key(self, search_intent: SearchIntent) -> str:
        """Generate cache key for search intent"""
        key_data = {
            "industry": search_intent.industry,
            "location": search_intent.location,
            "keywords": sorted(search_intent.keywords)
        }
        return hashlib.md5(
            json.dumps(key_data, sort_keys=True).encode()
        ).hexdigest()
