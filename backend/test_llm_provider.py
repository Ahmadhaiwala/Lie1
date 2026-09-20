"""Test LLMProvider with OpenRouter and Ollama fallback"""
import asyncio
import logging
from llm.llm_provider import LLMProvider
from llm.llm_config import LLMConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    print("=" * 60)
    print("  LLMProvider Test - OpenRouter + Ollama Fallback")
    print("=" * 60)
    
    try:
        config = LLMConfig.from_env()
        print(f"\n📋 Configuration:")
        print(f"  OpenRouter Model: {config.model}")
        print(f"  Ollama Fallback: {config.use_ollama_fallback}")
        print(f"  Ollama Model: {config.ollama_model}")
        print(f"  Ollama URL: {config.ollama_url}")
        
        # Initialize provider
        provider = LLMProvider(config)
        print(f"\n✓ LLMProvider initialized")
        
        # Test all providers
        print(f"\n🔍 Testing all LLM providers...")
        status = await provider.test_all_providers()
        print(f"\n📊 Provider Status:")
        print(f"  OpenRouter: {'✅ Working' if status['openrouter'] else '❌ Not available'}")
        print(f"  Ollama: {'✅ Working' if status['ollama'] else '❌ Not available'}")
        print(f"  Active Provider: {status['active']}")
        
        if not status['active']:
            print(f"\n❌ ERROR: No LLM provider is available!")
            return
        
        # Test completion
        print(f"\n💬 Testing completion with {status['active']}...")
        prompt = "What is the capital of France? Answer in one word."
        result = await provider.complete(
            prompt=prompt,
            system_prompt="Answer briefly and directly.",
            max_tokens=50,
        )
        print(f"\nPrompt: {prompt}")
        print(f"Response: {result.strip()}")
        
        print(f"\n✅ SUCCESS: LLMProvider is working correctly!")
        print(f"   Using: {status['active']}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
