# Crawl4AI Quick Reference

## 🚀 Common Commands

### Run All Tests
```bash
cd backend
python -m pytest -v
```

### Run Specific Test
```bash
python -m pytest tests/test_crawler.py::TestWebCrawler::test_simple_crawl -v
```

### Run Examples
```bash
python examples\basic_usage.py
```

## 💻 Code Snippets

### Basic Crawl
```python
from crawler import WebCrawler, CrawlerConfig
import asyncio

async def crawl_page():
    config = CrawlerConfig(headless=True)
    async with WebCrawler(config) as crawler:
        result = await crawler.crawl('https://example.com')
        print(result['markdown'])

asyncio.run(crawl_page())
```

### Crawl Multiple URLs
```python
async def crawl_many():
    config = CrawlerConfig(headless=True)
    urls = ['https://example.com', 'https://httpbin.org/html']
    
    async with WebCrawler(config) as crawler:
        results = await crawler.crawl_multiple(urls)
        for r in results:
            if r['success']:
                print(f"✓ {r['url']}: {len(r['html'])} bytes")
            else:
                print(f"✗ {r['url']}: {r['error_message']}")

asyncio.run(crawl_many())
```

### Extract Specific Content (CSS Selector)
```python
async def extract_headers():
    config = CrawlerConfig(headless=True)
    
    async with WebCrawler(config) as crawler:
        result = await crawler.crawl(
            'https://example.com',
            css_selector='h1, h2, h3'
        )
        print(result['cleaned_html'])

asyncio.run(extract_headers())
```

### Take Screenshot
```python
import base64

async def capture_page():
    config = CrawlerConfig(headless=True)
    
    async with WebCrawler(config) as crawler:
        result = await crawler.crawl(
            'https://example.com',
            screenshot=True
        )
        
        if result['screenshot']:
            with open('page.png', 'wb') as f:
                f.write(base64.b64decode(result['screenshot']))
            print("Screenshot saved to page.png")

asyncio.run(capture_page())
```

### Custom Configuration
```python
config = CrawlerConfig(
    headless=True,
    browser_type="chromium",  # or "firefox", "webkit"
    viewport_width=1920,
    viewport_height=1080,
    page_timeout=60000,  # 60 seconds
    use_stealth_mode=False,  # Set True for anti-detection
    user_agent="Mozilla/5.0 ...",
    extra_headers={'Authorization': 'Bearer token'}
)
```

### Wait for Element
```python
async def wait_for_content():
    config = CrawlerConfig(headless=True)
    
    async with WebCrawler(config) as crawler:
        result = await crawler.crawl(
            'https://example.com',
            wait_for='#content'  # CSS selector to wait for
        )
        print(result['html'])

asyncio.run(wait_for_content())
```

## 📊 Result Object Structure

```python
result = {
    'success': bool,           # True if crawl succeeded
    'url': str,                # Final URL (after redirects)
    'html': str,               # Raw HTML content
    'markdown': str,           # Markdown version
    'cleaned_html': str,       # Cleaned HTML
    'media': dict,             # Images, videos, etc.
    'links': dict,             # All extracted links
    'metadata': dict,          # Page metadata (title, description, etc.)
    'screenshot': str | None,  # Base64 screenshot if requested
    'status_code': int | None, # HTTP status code
    'error_message': str | None # Error if failed
}
```

## ⚙️ Configuration Options

```python
CrawlerConfig(
    # Browser Settings
    headless=True,              # Run browser in headless mode
    browser_type="chromium",    # chromium, firefox, or webkit
    viewport_width=1920,        # Browser viewport width
    viewport_height=1080,       # Browser viewport height
    
    # Performance
    page_timeout=30000,         # Page load timeout (ms)
    wait_for_network_idle=True, # Wait for network idle
    
    # Extraction
    remove_overlay_elements=True, # Remove popups/overlays
    bypass_cache=False,          # Bypass cache
    
    # Anti-Detection
    use_stealth_mode=False,      # Use Patchright for stealth
    
    # Customization
    user_agent=None,             # Custom user agent
    extra_headers=None,          # Dict of extra headers
    
    # Screenshots
    take_screenshot=False,       # Enable screenshots
    screenshot_wait_for=0.5,     # Wait before screenshot (seconds)
)
```

## 🔍 Common Patterns

### Retry Failed Requests
```python
async def crawl_with_retry(url, max_retries=3):
    config = CrawlerConfig(headless=True)
    
    async with WebCrawler(config) as crawler:
        for attempt in range(max_retries):
            result = await crawler.crawl(url, bypass_cache=True)
            if result['success']:
                return result
            print(f"Attempt {attempt + 1} failed, retrying...")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return result
```

### Extract Structured Data
```python
async def get_article_data(url):
    config = CrawlerConfig(headless=True)
    
    async with WebCrawler(config) as crawler:
        result = await crawler.crawl(url)
        
        if result['success']:
            return {
                'title': result['metadata'].get('title'),
                'description': result['metadata'].get('description'),
                'content': result['markdown'],
                'images': result['media'].get('images', []),
                'links': result['links']
            }
```

### Batch Processing
```python
async def batch_crawl(urls, batch_size=5):
    config = CrawlerConfig(headless=True)
    results = []
    
    async with WebCrawler(config) as crawler:
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            batch_results = await crawler.crawl_multiple(batch)
            results.extend(batch_results)
            print(f"Completed batch {i // batch_size + 1}")
    
    return results
```

## 🐛 Debugging Tips

### Enable Verbose Logging
Set environment variable:
```bash
set CRAWL4AI_VERBOSE=True
```

### Run Browser in Headed Mode
```python
config = CrawlerConfig(headless=False)
```

### Increase Timeout
```python
config = CrawlerConfig(page_timeout=60000)  # 60 seconds
```

### Check Result Details
```python
result = await crawler.crawl(url)
print(f"Success: {result['success']}")
print(f"Status: {result['status_code']}")
print(f"Error: {result['error_message']}")
print(f"HTML length: {len(result['html'])}")
```

## 📦 Installation (if needed)

```bash
pip install -r requirements.txt
C:\Users\haiwa\AppData\Roaming\Python\Python313\Scripts\crawl4ai-setup.exe
```

## 🔗 Useful Links

- [Crawl4AI Documentation](https://docs.crawl4ai.com/)
- [Playwright Docs](https://playwright.dev/)
- [CSS Selectors Reference](https://www.w3schools.com/cssref/css_selectors.asp)
