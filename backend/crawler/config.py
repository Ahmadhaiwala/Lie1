"""
Crawler Configuration
"""
from dataclasses import dataclass
from typing import Optional, List
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class CrawlerConfig:
    """Configuration for the web crawler"""
    
    # Browser settings
    headless: bool = True
    browser_type: str = "chromium"  # chromium, firefox, webkit
    viewport_width: int = 1920
    viewport_height: int = 1080
    
    # Performance settings
    page_timeout: int = 30000  # milliseconds
    wait_for_network_idle: bool = True
    
    # Extraction settings
    remove_overlay_elements: bool = True
    bypass_cache: bool = False
    
    # Anti-detection (use patchright)
    use_stealth_mode: bool = False
    
    # Optional headers
    user_agent: Optional[str] = None
    extra_headers: Optional[dict] = None
    
    # Screenshot settings
    take_screenshot: bool = False
    screenshot_wait_for: float = 0.5
    
    @classmethod
    def from_env(cls):
        """Create config from environment variables"""
        return cls(
            headless=os.getenv('BROWSER_HEADLESS', 'True').lower() == 'true',
            page_timeout=int(os.getenv('BROWSER_TIMEOUT', '30000')),
        )
    
    def to_dict(self) -> dict:
        """Convert config to dictionary for crawl4ai"""
        config = {
            'headless': self.headless,
            'browser_type': self.browser_type,
            'viewport_width': self.viewport_width,
            'viewport_height': self.viewport_height,
            'page_timeout': self.page_timeout,
        }
        
        if self.user_agent:
            config['user_agent'] = self.user_agent
        
        if self.extra_headers:
            config['headers'] = self.extra_headers
            
        return config
