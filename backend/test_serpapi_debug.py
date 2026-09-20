"""Debug SerpAPI integration"""
import asyncio
import os
import logging
from crawler.web_crawler import WebCrawler

logging.basicConfig(level=logging.INFO)

async def test():
    async with WebCrawler() as crawler:
        print(f'Crawler type: {crawler.crawler_type}')
        print(f'API key available: {bool(crawler.serpapi_key)}')
        
        if crawler.serpapi_key:
            print(f'API key starts with: {crawler.serpapi_key[:10]}...')
        
        results = await crawler.search_google(
            query='cloth shops',
            location='Ahmedabad',
            num_results=5
        )
        print(f'\nFound {len(results)} results')
        for r in results[:3]:
            print(f'  - {r.get("name", "N/A")}')

asyncio.run(test())
