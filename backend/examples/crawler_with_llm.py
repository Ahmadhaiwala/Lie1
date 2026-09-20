"""
Examples of using Crawler with LLM for intelligent data extraction
"""
import asyncio
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from crawler import WebCrawler, CrawlerConfig
from llm import LLMClient, PromptTemplates


async def example_extract_article_info():
    """Example: Crawl a webpage and extract article information"""
    print("\n=== Article Information Extraction ===")
    
    crawler_config = CrawlerConfig(headless=True)
    llm_client = LLMClient()
    
    async with WebCrawler(crawler_config) as crawler:
        # Crawl an article
        result = await crawler.crawl('https://example.com')
        
        if result['success']:
            print(f"✓ Crawled: {result['url']}")
            
            # Extract structured data using LLM
            schema = PromptTemplates.article_metadata_extractor()
            article_data = await llm_client.extract_structured_data(
                content=result['markdown'],
                schema=schema,
            )
            
            print(f"\nExtracted Article Data:")
            print(json.dumps(article_data, indent=2))
        else:
            print(f"✗ Failed to crawl: {result['error_message']}")


async def example_summarize_webpage():
    """Example: Crawl and summarize a webpage"""
    print("\n=== Webpage Summarization ===")
    
    crawler_config = CrawlerConfig(headless=True)
    llm_client = LLMClient()
    
    async with WebCrawler(crawler_config) as crawler:
        result = await crawler.crawl('https://example.com')
        
        if result['success']:
            print(f"✓ Crawled: {result['url']}")
            
            # Generate summary
            summary = await llm_client.summarize(
                content=result['markdown'],
                max_length=100,
                style="concise",
            )
            
            print(f"\nSummary:\n{summary}")
        else:
            print(f"✗ Failed: {result['error_message']}")


async def example_qa_from_webpage():
    """Example: Answer questions about webpage content"""
    print("\n=== Q&A from Webpage ===")
    
    crawler_config = CrawlerConfig(headless=True)
    llm_client = LLMClient()
    
    async with WebCrawler(crawler_config) as crawler:
        result = await crawler.crawl('https://example.com')
        
        if result['success']:
            print(f"✓ Crawled: {result['url']}")
            
            questions = [
                "What is this webpage about?",
                "What is the main purpose of this domain?",
            ]
            
            for question in questions:
                answer = await llm_client.answer_question(
                    question=question,
                    context=result['markdown'],
                )
                print(f"\nQ: {question}")
                print(f"A: {answer}")
        else:
            print(f"✗ Failed: {result['error_message']}")


async def example_extract_custom_data():
    """Example: Extract custom structured data"""
    print("\n=== Custom Data Extraction ===")
    
    crawler_config = CrawlerConfig(headless=True)
    llm_client = LLMClient()
    
    # Define custom schema
    custom_schema = {
        "type": "object",
        "properties": {
            "page_title": {"type": "string"},
            "main_message": {"type": "string"},
            "links_mentioned": {"type": "array", "items": {"type": "string"}},
            "domain_purpose": {"type": "string"},
        }
    }
    
    async with WebCrawler(crawler_config) as crawler:
        result = await crawler.crawl('https://example.com')
        
        if result['success']:
            print(f"✓ Crawled: {result['url']}")
            
            extracted = await llm_client.extract_structured_data(
                content=result['markdown'],
                schema=custom_schema,
                instructions="Extract information about the webpage's purpose and content.",
            )
            
            print(f"\nExtracted Custom Data:")
            print(json.dumps(extracted, indent=2))


async def example_multi_page_analysis():
    """Example: Crawl multiple pages and analyze them"""
    print("\n=== Multi-Page Analysis ===")
    
    crawler_config = CrawlerConfig(headless=True)
    llm_client = LLMClient()
    
    urls = [
        'https://example.com',
        'https://www.iana.org',
    ]
    
    async with WebCrawler(crawler_config) as crawler:
        results = await crawler.crawl_multiple(urls)
        
        summaries = []
        for result in results:
            if result['success']:
                print(f"✓ Crawled: {result['url']}")
                
                summary = await llm_client.summarize(
                    content=result['markdown'],
                    max_length=50,
                    style="concise",
                )
                
                summaries.append({
                    'url': result['url'],
                    'summary': summary,
                })
        
        print(f"\n📊 Analysis Results:")
        for item in summaries:
            print(f"\n🔗 {item['url']}")
            print(f"   {item['summary']}")


async def example_intelligent_content_filter():
    """Example: Use LLM to filter relevant content"""
    print("\n=== Intelligent Content Filtering ===")
    
    crawler_config = CrawlerConfig(headless=True)
    llm_client = LLMClient()
    
    async with WebCrawler(crawler_config) as crawler:
        result = await crawler.crawl('https://example.com')
        
        if result['success']:
            print(f"✓ Crawled: {result['url']}")
            
            # Ask LLM to identify main content
            response = await llm_client.complete_with_context(
                prompt="Identify and extract only the main content from this page, excluding navigation, ads, and boilerplate.",
                context=result['markdown'],
                system_prompt=PromptTemplates.web_content_analyzer(),
            )
            
            print(f"\nMain Content Identified:")
            print(response)


async def example_stream_analysis():
    """Example: Stream analysis results in real-time"""
    print("\n=== Streaming Analysis ===")
    
    crawler_config = CrawlerConfig(headless=True)
    llm_client = LLMClient()
    
    async with WebCrawler(crawler_config) as crawler:
        result = await crawler.crawl('https://example.com')
        
        if result['success']:
            print(f"✓ Crawled: {result['url']}\n")
            print("Streaming analysis:")
            
            async for token in llm_client.stream_complete(
                prompt=f"Analyze this content and provide key insights:\n\n{result['markdown'][:2000]}",
                system_prompt=PromptTemplates.web_content_analyzer(),
                max_tokens=200,
            ):
                print(token, end='', flush=True)
            
            print("\n")


async def main():
    """Run all examples"""
    print("=" * 60)
    print("Crawler + LLM Integration Examples")
    print("=" * 60)
    
    try:
        # Test LLM connection first
        llm_client = LLMClient()
        if await llm_client.test_connection():
            print("✓ LLM connection successful\n")
        else:
            print("✗ LLM connection failed\n")
            return
        
        # Run examples
        await example_summarize_webpage()
        await example_qa_from_webpage()
        await example_extract_article_info()
        await example_extract_custom_data()
        # await example_multi_page_analysis()  # Uncomment to test
        # await example_intelligent_content_filter()  # Uncomment to test
        # await example_stream_analysis()  # Uncomment to test
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
