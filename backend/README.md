# Crawl4AI Backend

A web crawler backend built with Crawl4AI for advanced web scraping and data extraction.

## Features

- 🚀 Async web crawling with Playwright/Patchright
- 🎯 CSS selector-based content extraction
- 📸 Screenshot capabilities
- 🔄 Concurrent URL crawling
- ⚙️ Configurable browser settings
- 🛡️ Stealth mode support for anti-detection
- 📝 Markdown and HTML output
- 🔗 Link and media extraction

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and adjust settings:

```bash
copy .env.example .env
```

### 3. Run Setup (if not done already)

```bash
C:\Users\haiwa\AppData\Roaming\Python\Python313\Scripts\crawl4ai-setup.exe
```

## Project Structure

```
backend/
├── crawler/
│   ├── __init__.py
│   ├── config.py          # Configuration classes
│   └── web_crawler.py     # Main crawler implementation
├── tests/
│   ├── __init__.py
│   └── test_crawler.py    # Test cases
├── examples/
│   └── basic_usage.py     # Usage examples
├── requirements.txt       # Python dependencies
├── pytest.ini            # Pytest configuration
└── README.md             # This file
```

## Usage

### Basic Example

```python
import asyncio
from crawler import WebCrawler, CrawlerConfig

async def main():
    config = CrawlerConfig(headless=True)
    
    async with WebCrawler(config) as crawler:
        result = await crawler.crawl('https://example.com')
        
        if result['success']:
            print(f"Title: {result['metadata']['title']}")
            print(f"Content: {result['markdown'][:200]}...")

asyncio.run(main())
```

### Run Examples

```bash
cd backend
python examples/basic_usage.py
```

## Testing

### Run All Tests

```bash
cd backend
pytest
```

### Run Specific Test

```bash
pytest tests/test_crawler.py::TestWebCrawler::test_simple_crawl
```

### Run with Coverage

```bash
pytest --cov=crawler --cov-report=html
```

## Configuration Options

### CrawlerConfig

- `headless` (bool): Run browser in headless mode (default: True)
- `browser_type` (str): Browser to use - chromium, firefox, webkit (default: chromium)
- `viewport_width` (int): Browser viewport width (default: 1920)
- `viewport_height` (int): Browser viewport height (default: 1080)
- `page_timeout` (int): Page load timeout in milliseconds (default: 30000)
- `use_stealth_mode` (bool): Use Patchright for anti-detection (default: False)
- `user_agent` (str): Custom user agent string
- `extra_headers` (dict): Additional HTTP headers

## API Reference

### WebCrawler

#### `async crawl(url, wait_for=None, css_selector=None, screenshot=False, bypass_cache=False)`

Crawl a single URL.

**Parameters:**
- `url` (str): URL to crawl
- `wait_for` (str, optional): CSS selector to wait for
- `css_selector` (str, optional): CSS selector to extract specific content
- `screenshot` (bool): Take screenshot (default: False)
- `bypass_cache` (bool): Bypass cache (default: False)

**Returns:** Dictionary with:
- `success` (bool): Whether crawl succeeded
- `url` (str): Final URL after redirects
- `html` (str): Raw HTML content
- `markdown` (str): Markdown version of content
- `cleaned_html` (str): Cleaned HTML
- `media` (dict): Extracted media (images, videos)
- `links` (dict): Extracted links
- `metadata` (dict): Page metadata
- `screenshot` (str, optional): Base64 encoded screenshot
- `status_code` (int): HTTP status code
- `error_message` (str, optional): Error message if failed

#### `async crawl_multiple(urls, **kwargs)`

Crawl multiple URLs concurrently.

**Parameters:**
- `urls` (List[str]): List of URLs to crawl
- `**kwargs`: Additional arguments passed to `crawl()`

**Returns:** List of result dictionaries

## Troubleshooting

### Browser Not Found

If you get browser-related errors, run the setup again:

```bash
C:\Users\haiwa\AppData\Roaming\Python\Python313\Scripts\crawl4ai-setup.exe
```

### Import Errors

Make sure you're in the backend directory and have installed dependencies:

```bash
cd backend
pip install -r requirements.txt
```

### Test Failures

Some tests require internet connectivity. Ensure you have a stable connection.

## Next Steps

- Add LLM integration for structured data extraction
- Implement proxy support
- Add rate limiting
- Create API endpoints (FastAPI/Flask)
- Add more extraction strategies
- Implement caching layer
