"""
Mock Web Crawler for Testing
Simulates Crawl4AI without requiring browser automation.
Used when CRAWL4AI is not available or on systems with subprocess issues.
"""
import asyncio
from typing import Optional, Dict, Any, List


class MockWebCrawler:
    """Mock crawler that returns realistic website content"""
    
    def __init__(self, config=None):
        """Initialize mock crawler"""
        self.config = config
        self._crawler = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
        
    async def start(self):
        """Initialize the crawler"""
        self._crawler = True
        
    async def close(self):
        """Close the crawler"""
        self._crawler = None
            
    async def arun(self, url: str, config=None) -> 'MockCrawlResult':
        """
        Crawl using the same interface as Crawl4AI (arun method)
        
        Args:
            url: URL to crawl
            config: CrawlerRunConfig (ignored for mock)
            
        Returns:
            Mock crawl result object with same interface as Crawl4AI
        """
        if not self._crawler:
            raise RuntimeError("Crawler not started")
        
        # Simulate network delay
        await asyncio.sleep(0.5)
        
        # Generate realistic website content
        html_content = self._generate_mock_html(url)
        markdown_content = self._generate_mock_markdown(url)
        
        # Create a simple result object that mimics Crawl4AI's response
        class MockCrawlResult:
            def __init__(self, url, html, markdown):
                self.success = True
                self.url = url
                self.html = html
                self.markdown = markdown
                self.cleaned_html = html
                self.media = []
                self.links = [
                    {'href': 'https://example.com/about', 'text': 'About Us'},
                    {'href': 'https://example.com/services', 'text': 'Services'},
                    {'href': 'https://example.com/contact', 'text': 'Contact'},
                ]
                self.metadata = {
                    'title': 'Digital Marketing Agency',
                    'description': 'Professional digital marketing services'
                }
                self.screenshot = None
                self.status_code = 200
                self.error_message = None
        
        return MockCrawlResult(url, html_content, markdown_content)
    
    async def crawl(
        self,
        url: str,
        wait_for: Optional[str] = None,
        css_selector: Optional[str] = None,
        screenshot: bool = False,
        bypass_cache: bool = False,
    ) -> Dict[str, Any]:
        """
        Mock crawl a single URL - returns realistic website content
        
        Args:
            url: URL to crawl (used to generate mock content)
            wait_for: CSS selector to wait for
            css_selector: CSS selector to extract
            screenshot: Whether to take a screenshot
            bypass_cache: Whether to bypass cache
            
        Returns:
            Dictionary containing mock crawl results
        """
        if not self._crawler:
            raise RuntimeError("Crawler not started")
        
        # Simulate network delay
        await asyncio.sleep(0.5)
        
        # Generate realistic website content based on URL
        html_content = self._generate_mock_html(url)
        markdown_content = self._generate_mock_markdown(url)
        
        return {
            'success': True,
            'url': url,
            'html': html_content,
            'markdown': markdown_content,
            'cleaned_html': html_content,
            'media': [],
            'links': [
                {'href': 'https://example.com/about', 'text': 'About Us'},
                {'href': 'https://example.com/services', 'text': 'Services'},
                {'href': 'https://example.com/contact', 'text': 'Contact'},
            ],
            'metadata': {
                'title': 'Digital Marketing Agency',
                'description': 'Professional digital marketing services'
            },
            'screenshot': None,
            'status_code': 200,
            'error_message': None,
        }
    
    async def crawl_multiple(
        self,
        urls: List[str],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Mock crawl multiple URLs
        
        Args:
            urls: List of URLs to crawl
            **kwargs: Additional arguments
            
        Returns:
            List of crawl results
        """
        tasks = [self.crawl(url, **kwargs) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
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
        Mock extract structured data from URL
        
        Args:
            url: URL to crawl
            schema: JSON schema for data extraction
            
        Returns:
            Extracted structured data
        """
        result = await self.crawl(url)
        
        if not result['success']:
            return {'success': False, 'error': result.get('error_message')}
        
        return {
            'success': True,
            'url': url,
            'data': result,
            'schema': schema,
        }
    
    def _generate_mock_html(self, url: str) -> str:
        """Generate realistic mock HTML content"""
        company_name = url.split('.')[1].replace('-', ' ').title()
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>{company_name} - Digital Marketing Agency</title>
    <meta name="description" content="Professional digital marketing services for your business">
</head>
<body>
    <header>
        <h1>{company_name}</h1>
        <nav>
            <a href="/about">About Us</a>
            <a href="/services">Services</a>
            <a href="/contact">Contact</a>
        </nav>
    </header>
    
    <section class="services">
        <h2>Our Services</h2>
        <ul>
            <li>Search Engine Optimization (SEO)</li>
            <li>Pay-Per-Click (PPC) Advertising</li>
            <li>Social Media Marketing</li>
            <li>Content Marketing</li>
            <li>Web Design & Development</li>
            <li>Email Marketing</li>
            <li>Conversion Rate Optimization</li>
        </ul>
    </section>
    
    <section class="about">
        <h2>About {company_name}</h2>
        <p>
            We are a full-service digital marketing agency specializing in helping businesses grow online.
            With over 10 years of experience, we've helped hundreds of clients achieve their digital goals.
        </p>
        <p><strong>Location:</strong> New York, NY</p>
        <p><strong>Team Size:</strong> 25+ professionals</p>
        <p><strong>Founded:</strong> 2014</p>
    </section>
    
    <section class="contact">
        <h2>Get In Touch</h2>
        <p><strong>Email:</strong> hello@{url.split('//')[1]}</p>
        <p><strong>Phone:</strong> +1-212-555-0100</p>
        <p><strong>Address:</strong> 123 Madison Ave, New York, NY 10016</p>
    </section>
    
    <footer>
        <p>&copy; 2024 {company_name}. All rights reserved.</p>
    </footer>
</body>
</html>
        """
    
    def _generate_mock_markdown(self, url: str) -> str:
        """Generate realistic mock Markdown content"""
        company_name = url.split('.')[1].replace('-', ' ').title()
        
        return f"""
# {company_name} - Digital Marketing Agency

## About Us

We are a full-service digital marketing agency specializing in helping businesses grow online. With over 10 years of experience, we've helped hundreds of clients achieve their digital goals.

- **Location:** New York, NY
- **Team Size:** 25+ professionals
- **Founded:** 2014
- **Founded:** Founded in 2014

## Services We Offer

1. **Search Engine Optimization (SEO)**
   - Technical SEO
   - Link Building
   - Local SEO
   - SEO Audits

2. **Pay-Per-Click (PPC) Advertising**
   - Google Ads Management
   - Facebook Ads
   - LinkedIn Ads
   - Display Advertising

3. **Social Media Marketing**
   - Strategy & Planning
   - Content Creation
   - Community Management
   - Influencer Partnerships

4. **Content Marketing**
   - Blog Writing
   - Whitepaper Development
   - Video Scripts
   - Infographics

5. **Web Design & Development**
   - Responsive Design
   - E-Commerce Solutions
   - Custom Development
   - CMS Implementation

6. **Email Marketing**
   - Campaign Strategy
   - Automation Setup
   - List Management
   - Analytics & Reporting

7. **Conversion Rate Optimization**
   - A/B Testing
   - Landing Page Optimization
   - User Experience Analysis
   - Performance Tracking

## Contact Information

- **Email:** hello@{url.split('//')[1]}
- **Phone:** +1-212-555-0100
- **Address:** 123 Madison Ave, New York, NY 10016
- **Website:** {url}
- **Hours:** Monday-Friday, 9AM-6PM EST

## Why Choose {company_name}?

- ✓ 10+ years of industry experience
- ✓ Certified Google Partner
- ✓ Data-driven approach
- ✓ Transparent reporting
- ✓ Dedicated account managers
- ✓ Custom solutions for every business
"""
