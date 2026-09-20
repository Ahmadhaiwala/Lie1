"""
Website Resolver
Finds and validates business websites
"""
import asyncio
import re
from typing import Optional, List
from urllib.parse import urlparse, urljoin

from crawler import WebCrawler, CrawlerConfig


class WebsiteResolver:
    """Resolves and validates business websites"""
    
    def __init__(self, crawler: Optional[WebCrawler] = None):
        """
        Initialize website resolver
        
        Args:
            crawler: Web crawler instance
        """
        self.crawler = crawler
        self._validation_cache: dict = {}
    
    async def resolve_website(
        self,
        business_name: str,
        location: Optional[str] = None,
        hints: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Find the website for a business
        
        Args:
            business_name: Name of the business
            location: Business location for context
            hints: Additional hints (phone, address, etc.)
            
        Returns:
            Website URL or None if not found
        """
        # Try common patterns first
        candidates = self._generate_website_candidates(business_name)
        
        # Check each candidate
        for url in candidates:
            if await self.validate_website(url):
                return url
        
        # If no luck with patterns, search for it
        # In production: Use search API
        return None
    
    def _generate_website_candidates(
        self,
        business_name: str
    ) -> List[str]:
        """
        Generate potential website URLs based on business name
        
        Args:
            business_name: Business name
            
        Returns:
            List of candidate URLs
        """
        # Normalize name
        name = business_name.lower()
        name = re.sub(r'[^a-z0-9]+', '', name)
        
        candidates = []
        
        # Common patterns
        patterns = [
            f"https://www.{name}.com",
            f"https://{name}.com",
            f"https://www.{name}.net",
            f"https://{name}.net",
            f"https://www.{name}.co",
            f"https://{name}.co",
        ]
        
        candidates.extend(patterns)
        
        # If name has multiple words, try with hyphens
        original_name = business_name.lower()
        if ' ' in original_name:
            hyphenated = original_name.replace(' ', '-')
            hyphenated = re.sub(r'[^a-z0-9-]+', '', hyphenated)
            
            candidates.extend([
                f"https://www.{hyphenated}.com",
                f"https://{hyphenated}.com",
            ])
        
        return candidates
    
    async def validate_website(
        self,
        url: str,
        check_content: bool = True
    ) -> bool:
        """
        Validate that a website exists and is accessible
        
        Args:
            url: Website URL to validate
            check_content: Whether to check content validity
            
        Returns:
            True if valid, False otherwise
        """
        # Check cache
        if url in self._validation_cache:
            return self._validation_cache[url]
        
        try:
            # Parse URL
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # If we have a crawler, try to fetch the page
            if self.crawler and check_content:
                result = await self.crawler.crawl(url)
                is_valid = result.get('success', False)
            else:
                # Mock validation for now
                # In production: Make a HEAD request
                is_valid = True
            
            # Cache result
            self._validation_cache[url] = is_valid
            return is_valid
            
        except Exception as e:
            self._validation_cache[url] = False
            return False
    
    async def extract_contact_info(
        self,
        url: str
    ) -> dict:
        """
        Extract contact information from a website
        
        Args:
            url: Website URL
            
        Returns:
            Dictionary with contact info (emails, phones, etc.)
        """
        if not self.crawler:
            return {}
        
        # Crawl the website
        result = await self.crawler.crawl(url)
        
        if not result.get('success'):
            return {}
        
        html = result.get('html', '')
        markdown = result.get('markdown', '')
        
        # Extract emails
        emails = self._extract_emails(html)
        
        # Extract phone numbers
        phones = self._extract_phones(html)
        
        # Extract social media
        social_media = self._extract_social_media(html)
        
        return {
            'emails': list(set(emails)),
            'phones': list(set(phones)),
            'social_media': social_media,
        }
    
    def _extract_emails(self, html: str) -> List[str]:
        """Extract email addresses from HTML"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(pattern, html)
        
        # Filter out common non-contact emails
        filtered = [
            email for email in emails
            if not any(skip in email.lower() for skip in ['example', 'test', 'noreply'])
        ]
        
        return filtered
    
    def _extract_phones(self, html: str) -> List[str]:
        """Extract phone numbers from HTML"""
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
            r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}',  # (123) 456-7890
            r'\d{3}[-.\s]\d{3}[-.\s]\d{4}',  # 123-456-7890
        ]
        
        phones = []
        for pattern in patterns:
            phones.extend(re.findall(pattern, html))
        
        return phones
    
    def _extract_social_media(self, html: str) -> dict:
        """Extract social media links from HTML"""
        social_platforms = {
            'facebook': r'facebook\.com/[\w.-]+',
            'twitter': r'twitter\.com/[\w.-]+',
            'linkedin': r'linkedin\.com/(?:company|in)/[\w.-]+',
            'instagram': r'instagram\.com/[\w.-]+',
            'youtube': r'youtube\.com/(?:c|channel|user)/[\w.-]+',
        }
        
        social_media = {}
        
        for platform, pattern in social_platforms.items():
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                # Get the first match and construct full URL
                social_media[platform] = f"https://{matches[0]}"
        
        return social_media
    
    def normalize_url(self, url: str) -> str:
        """
        Normalize URL to a standard format
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Parse and reconstruct
        parsed = urlparse(url)
        
        # Remove www. for consistency (optional)
        netloc = parsed.netloc.lower()
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        
        # Reconstruct
        normalized = f"{parsed.scheme}://{netloc}{parsed.path}"
        
        # Remove trailing slash
        if normalized.endswith('/'):
            normalized = normalized[:-1]
        
        return normalized
