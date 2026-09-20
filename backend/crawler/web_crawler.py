"""
Web Crawler - Uses SerpAPI for REAL Google search results
Falls back to Crawl4AI if available, then mock crawler
"""
import asyncio
import logging
from typing import Optional, Dict, Any, List
import os

logger = logging.getLogger(__name__)

# Try to import SerpAPI first (for REAL data)
try:
    import aiohttp
    SERPAPI_AVAILABLE = True
except Exception as e:
    logger.warning(f"SerpAPI not available: {e}")
    SERPAPI_AVAILABLE = False

# Try to import Crawl4AI
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
    CRAWL4AI_AVAILABLE = True
except Exception as e:
    logger.warning(f"Crawl4AI not available: {e}")
    CRAWL4AI_AVAILABLE = False

from crawler.config import CrawlerConfig
from crawler.mock_crawler import MockWebCrawler


class WebCrawler:
    """Web crawler - tries SerpAPI first, then Crawl4AI, then mock"""
    
    def __init__(self, config: Optional[CrawlerConfig] = None):
        """Initialize the web crawler"""
        self.config = config or CrawlerConfig()
        self._crawler: Optional[Any] = None
        self.crawler_type = None
        
        # Get API keys from environment
        self.serpapi_key = os.getenv('SERP_API_KEY')
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
        
    async def start(self):
        """Initialize crawler - prioritizes SerpAPI for real data"""
        if SERPAPI_AVAILABLE and self.serpapi_key:
            logger.info("✓ Using SerpAPI for REAL Google search results")
            self.crawler_type = "serpapi"
            self._crawler = "serpapi"  # SerpAPI uses async HTTP, not a crawler object
        elif CRAWL4AI_AVAILABLE:
            logger.info("Using Crawl4AI web crawler")
            self.crawler_type = "crawl4ai"
            try:
                browser_config = BrowserConfig(
                    headless=self.config.headless,
                    browser_type=self.config.browser_type,
                )
                self._crawler = AsyncWebCrawler(config=browser_config)
                await self._crawler.__aenter__()
            except Exception as e:
                logger.warning(f"Crawl4AI failed: {e}. Using mock crawler.")
                self.crawler_type = "mock"
                self._crawler = MockWebCrawler(self.config)
                await self._crawler.start()
        else:
            logger.info("Using mock crawler")
            self.crawler_type = "mock"
            self._crawler = MockWebCrawler(self.config)
            await self._crawler.start()
        
    async def close(self):
        """Close the crawler"""
        if self._crawler and self.crawler_type == "crawl4ai":
            try:
                await self._crawler.__aexit__(None, None, None)
            except:
                pass
        elif self._crawler and self.crawler_type == "mock":
            await self._crawler.close()
        self._crawler = None
    
    async def search_google(
        self,
        query: str,
        location: Optional[str] = None,
        num_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search Google using SerpAPI for REAL results
        
        Args:
            query: Search query (e.g., "cloth shops")
            location: Location (e.g., "Ahmedabad, India")
            num_results: Number of results
            
        Returns:
            List of real search results with business info
        """
        if self.crawler_type != "serpapi":
            logger.warning("SerpAPI not available, cannot search real data")
            return []
        
        try:
            import aiohttp
            
            params = {
                "api_key": self.serpapi_key,
                "q": f"{query} in {location}" if location else query,
                "engine": "google",
                "num": num_results,
                "gl": "in",  # India
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://serpapi.com/search",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✓ Real Google search: {query}")
                        return self._parse_search_results(data)
                    else:
                        logger.error(f"SerpAPI error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Google search failed: {str(e)}")
            return []
    
    def _parse_search_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse SerpAPI results into business objects"""
        businesses = []
        
        # Parse organic results
        if "organic_results" in data:
            for result in data.get("organic_results", [])[:10]:
                business = {
                    "name": result.get("title", "Unknown"),
                    "website": result.get("link", ""),
                    "description": result.get("snippet", ""),
                    "source": "google_search",
                    "score": 0.8
                }
                if business["website"]:
                    businesses.append(business)
        
        # Parse local/knowledge panel results
        if "knowledge_graph" in data:
            kg = data["knowledge_graph"]
            business = {
                "name": kg.get("title", "Unknown"),
                "website": kg.get("website", ""),
                "phone": kg.get("phone", ""),
                "address": kg.get("address", ""),
                "description": kg.get("description", ""),
                "source": "knowledge_graph",
                "score": 0.9
            }
            if business["name"]:
                businesses.append(business)
        
        logger.info(f"Parsed {len(businesses)} real businesses")
        return businesses
            
    async def crawl(
        self,
        url: str,
        wait_for: Optional[str] = None,
        css_selector: Optional[str] = None,
        screenshot: bool = False,
        bypass_cache: bool = False,
    ) -> Dict[str, Any]:
        """
        Crawl a single URL
        
        Args:
            url: URL to crawl
            wait_for: CSS selector to wait for before extracting content
            css_selector: CSS selector to extract specific content
            screenshot: Whether to take a screenshot
            bypass_cache: Whether to bypass cache
            
        Returns:
            Dictionary containing crawl results
        """
        if not self._crawler:
            raise RuntimeError("Crawler not started. Use 'async with' or call start() first")
        
        # Configure crawler run
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS if bypass_cache else CacheMode.ENABLED,
            page_timeout=self.config.page_timeout,
            wait_for_images=True,
            screenshot=screenshot,
            remove_overlay_elements=self.config.remove_overlay_elements,
        )
        
        if wait_for:
            run_config.wait_for = wait_for
            
        if css_selector:
            run_config.css_selector = css_selector
        
        # Execute crawl
        result = await self._crawler.arun(
            url=url,
            config=run_config,
        )
        
        return {
            'success': result.success,
            'url': result.url,
            'html': result.html,
            'markdown': result.markdown,
            'cleaned_html': result.cleaned_html,
            'media': result.media,
            'links': result.links,
            'metadata': result.metadata,
            'screenshot': result.screenshot if screenshot else None,
            'status_code': result.status_code,
            'error_message': result.error_message,
        }
    
    async def crawl_multiple(
        self,
        urls: List[str],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Crawl multiple URLs
        
        Args:
            urls: List of URLs to crawl
            **kwargs: Additional arguments passed to crawl()
            
        Returns:
            List of crawl results
        """
        tasks = [self.crawl(url, **kwargs) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'url': urls[i],
                    'error_message': str(result),
                })
            else:
                processed_results.append(result)
                
        return processed_results
    
    async def extract_structured_data(
        self,
        url: str,
        schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Extract structured data from a URL using a schema
        
        Args:
            url: URL to crawl
            schema: JSON schema for data extraction
            
        Returns:
            Extracted structured data
        """
        # This is a placeholder for LLM-based extraction
        # You would integrate with OpenAI or other LLM here
        result = await self.crawl(url)
        
        if not result['success']:
            return {'success': False, 'error': result.get('error_message')}
        
        return {
            'success': True,
            'url': url,
            'data': result,  # In real implementation, parse with LLM using schema
            'schema': schema,
        }
