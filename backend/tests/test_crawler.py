"""
Test cases for Web Crawler
"""
import pytest
import asyncio
from crawler import WebCrawler, CrawlerConfig


class TestWebCrawler:
    """Test suite for WebCrawler"""
    
    @pytest.mark.asyncio
    async def test_crawler_initialization(self):
        """Test crawler can be initialized"""
        config = CrawlerConfig(headless=True)
        crawler = WebCrawler(config)
        
        assert crawler.config.headless == True
        assert crawler._crawler is None
    
    @pytest.mark.asyncio
    async def test_crawler_context_manager(self):
        """Test crawler works as async context manager"""
        config = CrawlerConfig(headless=True)
        
        async with WebCrawler(config) as crawler:
            assert crawler._crawler is not None
        
        # Should be closed after context
        assert crawler._crawler is None
    
    @pytest.mark.asyncio
    async def test_simple_crawl(self):
        """Test crawling a simple webpage"""
        config = CrawlerConfig(headless=True, page_timeout=30000)
        
        async with WebCrawler(config) as crawler:
            # Use example.com as a reliable test target
            result = await crawler.crawl('https://example.com')
            
            assert result['success'] == True
            assert 'example.com' in result['url']  # Allow for trailing slash variations
            assert 'Example Domain' in result['html']
            assert len(result['markdown']) > 0
    
    @pytest.mark.asyncio
    async def test_crawl_with_invalid_url(self):
        """Test crawling with invalid URL"""
        config = CrawlerConfig(headless=True, page_timeout=10000)
        
        async with WebCrawler(config) as crawler:
            result = await crawler.crawl('https://this-domain-does-not-exist-12345.com')
            
            assert result['success'] == False
            assert result['error_message'] is not None
    
    @pytest.mark.asyncio
    async def test_crawl_multiple_urls(self):
        """Test crawling multiple URLs concurrently"""
        config = CrawlerConfig(headless=True)
        
        urls = [
            'https://example.com',
            'https://www.iana.org',
        ]
        
        async with WebCrawler(config) as crawler:
            results = await crawler.crawl_multiple(urls)
            
            assert len(results) == 2
            # At least one should succeed
            successful_results = [r for r in results if r['success']]
            assert len(successful_results) > 0
    
    @pytest.mark.asyncio
    async def test_crawl_with_css_selector(self):
        """Test crawling with CSS selector"""
        config = CrawlerConfig(headless=True)
        
        async with WebCrawler(config) as crawler:
            result = await crawler.crawl(
                'https://example.com',
                css_selector='h1'
            )
            
            assert result['success'] == True
            assert 'Example Domain' in result['cleaned_html']
    
    @pytest.mark.asyncio
    async def test_crawler_without_start(self):
        """Test that crawler raises error if not started"""
        config = CrawlerConfig(headless=True)
        crawler = WebCrawler(config)
        
        with pytest.raises(RuntimeError, match="Crawler not started"):
            await crawler.crawl('https://example.com')
    
    @pytest.mark.asyncio
    async def test_config_from_env(self):
        """Test creating config from environment variables"""
        config = CrawlerConfig.from_env()
        
        assert isinstance(config.headless, bool)
        assert config.page_timeout > 0
    
    @pytest.mark.asyncio
    async def test_crawler_metadata_extraction(self):
        """Test that crawler extracts metadata"""
        config = CrawlerConfig(headless=True)
        
        async with WebCrawler(config) as crawler:
            result = await crawler.crawl('https://example.com')
            
            assert result['success'] == True
            assert result['metadata'] is not None
            assert 'title' in result['metadata']
    
    @pytest.mark.asyncio
    async def test_crawler_links_extraction(self):
        """Test that crawler extracts links"""
        config = CrawlerConfig(headless=True)
        
        async with WebCrawler(config) as crawler:
            result = await crawler.crawl('https://example.com')
            
            assert result['success'] == True
            assert 'links' in result
            assert isinstance(result['links'], dict)


class TestCrawlerConfig:
    """Test suite for CrawlerConfig"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = CrawlerConfig()
        
        assert config.headless == True
        assert config.browser_type == "chromium"
        assert config.viewport_width == 1920
        assert config.viewport_height == 1080
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = CrawlerConfig(
            headless=False,
            browser_type="firefox",
            page_timeout=60000
        )
        
        assert config.headless == False
        assert config.browser_type == "firefox"
        assert config.page_timeout == 60000
    
    def test_config_to_dict(self):
        """Test converting config to dictionary"""
        config = CrawlerConfig(
            headless=True,
            user_agent="Custom Agent"
        )
        
        config_dict = config.to_dict()
        
        assert config_dict['headless'] == True
        assert config_dict['user_agent'] == "Custom Agent"
        assert 'browser_type' in config_dict
