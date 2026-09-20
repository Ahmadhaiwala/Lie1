"""
SerpAPI Web Crawler - Real Google Search Results
Finds actual businesses from real Google search results
"""
import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)


class SerpAPICrawler:
    """Real web crawler using SerpAPI for actual Google search results"""
    
    def __init__(self, api_key: str):
        """
        Initialize SerpAPI crawler
        
        Args:
            api_key: SerpAPI key from https://serpapi.com
        """
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
        
    async def search(
        self,
        query: str,
        location: Optional[str] = None,
        num_results: int = 10,
        engine: str = "google"
    ) -> Dict[str, Any]:
        """
        Search using SerpAPI to get REAL Google results
        
        Args:
            query: Search query (e.g., "cloth shops in Ahmedabad")
            location: Location for local search
            num_results: Number of results to fetch
            engine: Search engine (google, google_maps, etc.)
            
        Returns:
            Dictionary with search results including business info
        """
        params = {
            "api_key": self.api_key,
            "q": query,
            "num": num_results,
            "engine": engine,
        }
        
        # Add location if provided
        if location:
            params["location"] = location
            params["google_domain"] = "google.co.in"  # For India searches
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✓ SerpAPI search successful: {query}")
                        return data
                    else:
                        logger.error(f"SerpAPI error: {response.status}")
                        return {"error": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"SerpAPI search failed: {str(e)}")
            return {"error": str(e)}
    
    async def search_google_maps(
        self,
        query: str,
        location: str,
        num_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search Google Maps for local businesses
        
        Args:
            query: Business type (e.g., "cloth shops")
            location: City/location (e.g., "Ahmedabad, India")
            num_results: Number of results
            
        Returns:
            Google Maps results with real businesses
        """
        params = {
            "api_key": self.api_key,
            "q": f"{query} in {location}",
            "type": "maps",
            "num": num_results,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✓ Google Maps search: {query} in {location}")
                        return data
                    else:
                        return {"error": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"Google Maps search failed: {str(e)}")
            return {"error": str(e)}
    
    async def get_business_details(self, url: str) -> Dict[str, Any]:
        """
        Get detailed information about a business from its website
        
        Args:
            url: Business website URL
            
        Returns:
            Business details extracted from website
        """
        # In production, you'd use BeautifulSoup or Selenium to scrape details
        # For now, return the URL and basic info
        return {
            "website": url,
            "source": "serpapi"
        }


def parse_search_results(search_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse SerpAPI search results into business objects
    
    Args:
        search_data: Raw SerpAPI response
        
    Returns:
        List of businesses with contact info
    """
    businesses = []
    
    # Parse organic results (regular Google search results)
    if "organic_results" in search_data:
        for result in search_data["organic_results"][:10]:
            business = {
                "name": result.get("title", "Unknown"),
                "website": result.get("link", ""),
                "description": result.get("snippet", ""),
                "source": "google_search"
            }
            businesses.append(business)
    
    # Parse local results (Google Maps)
    if "local_results" in search_data:
        for result in search_data["local_results"][:10]:
            business = {
                "name": result.get("title", "Unknown"),
                "address": result.get("address", ""),
                "phone": result.get("phone", ""),
                "website": result.get("website", ""),
                "rating": result.get("rating", ""),
                "type": result.get("type", ""),
                "source": "google_maps"
            }
            businesses.append(business)
    
    logger.info(f"Parsed {len(businesses)} businesses from search results")
    return businesses


async def search_real_businesses(
    query: str,
    location: str,
    api_key: str
) -> List[Dict[str, Any]]:
    """
    Search for real businesses using SerpAPI
    
    Args:
        query: What to search (e.g., "cloth shops")
        location: Where to search (e.g., "Ahmedabad, India")
        api_key: SerpAPI key
        
    Returns:
        List of real businesses found
    """
    crawler = SerpAPICrawler(api_key)
    
    # Search Google Maps for local results
    logger.info(f"Searching for: {query} in {location}")
    results = await crawler.search_google_maps(query, location, num_results=15)
    
    # Parse results into business objects
    businesses = parse_search_results(results)
    
    logger.info(f"Found {len(businesses)} real businesses")
    return businesses
