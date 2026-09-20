"""
Basic usage examples for the crawler
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import crawler
sys.path.insert(0, str(Path(__file__).parent.parent))

from crawler import WebCrawler, CrawlerConfig


async def example_basic_crawl():
    """Example: Basic web crawling"""
    print("\n=== Basic Crawl Example ===")
    
    config = CrawlerConfig(headless=True)
    
    async with WebCrawler(config) as crawler:
        result = await crawler.crawl('https://example.com')
        
        if result['success']:
            print(f"✓ Successfully crawled: {result['url']}")
            print(f"  Status Code: {result['status_code']}")
            print(f"  Title: {result['metadata'].get('title', 'N/A')}")
            print(f"  Content Length: {len(result['html'])} characters")
            print(f"\nFirst 200 chars of markdown:\n{result['markdown'][:200]}...")
        else:
            print(f"✗ Failed to crawl: {result['error_message']}")


async def example_multiple_urls():
    """Example: Crawl multiple URLs concurrently"""
    print("\n=== Multiple URLs Crawl Example ===")
    
    urls = [
        'https://example.com',
        'https://www.iana.org',
        'https://httpbin.org/html',
    ]
    
    config = CrawlerConfig(headless=True)
    
    async with WebCrawler(config) as crawler:
        results = await crawler.crawl_multiple(urls)
        
        for result in results:
            if result['success']:
                print(f"✓ {result['url']}: {result['status_code']}")
            else:
                print(f"✗ {result['url']}: {result.get('error_message', 'Unknown error')}")


async def example_css_selector():
    """Example: Extract specific content using CSS selector"""
    print("\n=== CSS Selector Example ===")
    
    config = CrawlerConfig(headless=True)
    
    async with WebCrawler(config) as crawler:
        result = await crawler.crawl(
            'https://example.com',
            css_selector='div'
        )
        
        if result['success']:
            print(f"✓ Extracted content with CSS selector")
            print(f"  Cleaned HTML length: {len(result['cleaned_html'])} characters")
            print(f"\nExtracted content:\n{result['cleaned_html'][:300]}...")
        else:
            print(f"✗ Failed: {result['error_message']}")


async def example_with_screenshot():
    """Example: Take screenshot while crawling"""
    print("\n=== Screenshot Example ===")
    
    config = CrawlerConfig(headless=True)
    
    async with WebCrawler(config) as crawler:
        result = await crawler.crawl(
            'https://example.com',
            screenshot=True
        )
        
        if result['success'] and result['screenshot']:
            print(f"✓ Screenshot taken successfully")
            print(f"  Screenshot size: {len(result['screenshot'])} bytes")
            
            # Save screenshot to file
            import base64
            with open('screenshot.png', 'wb') as f:
                f.write(base64.b64decode(result['screenshot']))
            print(f"  Saved to: screenshot.png")
        else:
            print(f"✗ Failed to take screenshot")


async def main():
    """Run all examples"""
    print("=" * 60)
    print("Crawl4AI Crawler Examples")
    print("=" * 60)
    
    try:
        await example_basic_crawl()
        await example_multiple_urls()
        await example_css_selector()
        # await example_with_screenshot()  # Uncomment to test screenshots
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
