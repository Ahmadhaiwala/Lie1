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
        Discover businesses from real Google search (SerpAPI)
        """
        businesses = []
        
        from crawler.web_crawler import WebCrawler
        
        async with WebCrawler() as crawler:
            for query in search_intent.queries:
                try:
                    # Search REAL Google using SerpAPI
                    real_results = await crawler.search_google(
                        query=query.query,
                        location=query.location or search_intent.location,
                        num_results=10
                    )
                    
                    # Convert search results to Business objects
                    for result in real_results:
                        business = Business(
                            id=f"biz_{hash(result.get('website', result.get('name')))}",
                            name=result.get('name', 'Unknown'),
                            description=result.get('description', 'Business found via Google search'),
                            industry=search_intent.industry or "General",
                            contact=BusinessContact(
                                website=result.get('website'),
                                phone=result.get('phone'),
                                email=None  # Not available from search results
                            ),
                            locations=[
                                BusinessLocation(
                                    address=result.get('address'),
                                    city=search_intent.location if search_intent.location else "Unknown",
                                    country="India"
                                )
                            ] if result.get('address') or search_intent.location else [],
                            source="google_search",
                            source_id=result.get('website', result.get('name')),
                            status=BusinessStatus.DISCOVERED
                        )
                        businesses.append(business)
                        
                except Exception as e:
                    logger.warning(f"Web search failed for query '{query.query}': {e}")
                    # Fall back to mock data if search fails
                    mock_results = self._generate_mock_businesses(
                        query.query,
                        query.location or search_intent.location,
                        source="web_search_fallback",
                        count=2
                    )
                    businesses.extend(mock_results)
        
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
        """Generate realistic mock businesses for lead generation"""
        businesses = []
        
        # Realistic digital marketing agencies for NYC
        mock_data = [
            {
                "name": "Blue Whale Digital",
                "email": "hello@bluewhaledigital.com",
                "phone": "+1-212-555-0142",
                "website": "https://bluewhaledigital.com",
                "services": "SEO, PPC, Content Marketing, Social Media Management"
            },
            {
                "name": "Growth Hacker NYC",
                "email": "contact@growthhakernyc.com",
                "phone": "+1-646-555-0189",
                "website": "https://growthhackernyc.com",
                "services": "Growth Marketing, Analytics, Conversion Optimization"
            },
            {
                "name": "Manhattan SEO Experts",
                "email": "info@manhattanseo.com",
                "phone": "+1-212-555-0156",
                "website": "https://manhattanseo.com",
                "services": "SEO, Link Building, Technical SEO"
            },
            {
                "name": "Digital Catalyst Agency",
                "email": "team@digitalcatalyst.io",
                "phone": "+1-917-555-0173",
                "website": "https://digitalcatalyst.io",
                "services": "Web Design, Digital Strategy, Branding"
            },
            {
                "name": "Performance Marketing Co",
                "email": "sales@perfmkt.com",
                "phone": "+1-212-555-0201",
                "website": "https://perfmkt.com",
                "services": "Google Ads, Facebook Ads, Retargeting"
            },
            {
                "name": "NextGen Digital Solutions",
                "email": "inquiry@nextgendigital.com",
                "phone": "+1-646-555-0234",
                "website": "https://nextgendigital.com",
                "services": "Full-Stack Digital, CRM Setup, Marketing Automation"
            },
            {
                "name": "Creative Studio NYC",
                "email": "studio@creativenyc.com",
                "phone": "+1-212-555-0267",
                "website": "https://creativenyc.com",
                "services": "Content Creation, Video Production, Social Media"
            },
            {
                "name": "Data Driven Marketing",
                "email": "hello@datadrvenmarketing.com",
                "phone": "+1-917-555-0298",
                "website": "https://datadrvenmarketing.com",
                "services": "Analytics, BI Dashboard, Reporting, Insights"
            }
        ]
        
        for i in range(min(count, len(mock_data))):
            data = mock_data[i]
            business_id = hashlib.md5(
                f"{data['name']}{location}{source}".encode()
            ).hexdigest()[:12]
            
            business = Business(
                id=f"biz_{business_id}",
                name=data['name'],
                description=data.get('services', 'Digital marketing and web services'),
                industry="Digital Marketing",
                contact=BusinessContact(
                    email=data['email'],
                    phone=data['phone'],
                    website=data['website']
                ),
                locations=[
                    BusinessLocation(
                        city=location.split(",")[0] if location and "," in location else "New York",
                        state=location.split(",")[1].strip() if location and "," in location else "NY",
                        country="USA"
                    )
                ],
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
