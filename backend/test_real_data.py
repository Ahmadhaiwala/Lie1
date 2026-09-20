"""
Test script to verify SerpAPI integration works with real data
"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from crawler.web_crawler import WebCrawler


async def test_real_search():
    """Test searching for real businesses"""
    print("\n" + "="*60)
    print("TESTING REAL DATA - SerpAPI Integration")
    print("="*60 + "\n")
    
    print("Query: Cloth shops in Ahmedabad, India")
    print("Expected: Real businesses from Google search\n")
    
    async with WebCrawler() as crawler:
        print("Searching real Google data...")
        results = await crawler.search_google(
            query="cloth shops",
            location="Ahmedabad, India",
            num_results=10
        )
        
        print(f"\n✓ Found {len(results)} businesses\n")
        
        if results:
            for i, business in enumerate(results[:5], 1):
                print(f"{i}. {business.get('name', 'Unknown')}")
                print(f"   Website: {business.get('website', 'N/A')}")
                print(f"   Source: {business.get('source', 'unknown')}")
                print()
        else:
            print("No results found (might be API limit or network issue)")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_real_search())
