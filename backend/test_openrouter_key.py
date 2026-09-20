"""Test OpenRouter API key validity"""
import asyncio
import os
from llm.llm_client import LLMClient
from llm.llm_config import LLMConfig

async def test():
    try:
        config = LLMConfig.from_env()
        print(f"✓ API Key loaded: {config.api_key[:20]}...")
        print(f"✓ Model: {config.model}")
        print(f"✓ Base URL: {config.base_url}")
        
        client = LLMClient(config)
        print("\n🔍 Testing connection...")
        
        result = await client.test_connection()
        if result:
            print("✅ OpenRouter API is working!")
        else:
            print("❌ OpenRouter API connection failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())
