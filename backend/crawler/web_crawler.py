"""
Web Crawler using Crawl4AI
"""
import asyncio
from typing import Optional, Dict, Any, List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawler.config import CrawlerConfig


class WebCrawler:
    """Web crawler wrapper for Crawl4AI"""
    
    def __init__(self, config: Optional[CrawlerConfig] = None):
        """
        Initialize the web crawler
        
        Args:
            config: CrawlerConfig instance with crawler settings
        """
        self.config = config or CrawlerConfig()
        self._crawler: Optional[AsyncWebCrawler] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
        
    async def start(self):
        """Initialize and start the crawler"""
        browser_config_kwargs = {
            'headless': self.config.headless,
            'browser_type': self.config.browser_type,
            'viewport_width': self.config.viewport_width,
            'viewport_height': self.config.viewport_height,
            'use_managed_browser': not self.config.use_stealth_mode,
        }
        
        # Only add optional parameters if they are not None
        if self.config.user_agent:
            browser_config_kwargs['user_agent'] = self.config.user_agent
        
        if self.config.extra_headers:
            browser_config_kwargs['headers'] = self.config.extra_headers
        
        browser_config = BrowserConfig(**browser_config_kwargs)
        
        self._crawler = AsyncWebCrawler(config=browser_config)
        await self._crawler.__aenter__()
        
    async def close(self):
        """Close the crawler and cleanup resources"""
        if self._crawler:
            await self._crawler.__aexit__(None, None, None)
            self._crawler = None
            
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
