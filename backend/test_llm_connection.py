"""
Quick test script to verify LLM connection with free models
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from llm import LLMClient, LLMConfig, AVAILABLE_FREE_MODELS


async def test_default_model():
    """Test the default configured model"""
    print("=" * 60)
    print("Testing Default Model")
    print("=" * 60)
    
    try:
        config = LLMConfig.from_env()
        print(f"✓ Config loaded")
        print(f"  Model: {config.model}")
        print(f"  Temperature: {config.temperature}")
        print(f"  Max Tokens: {config.max_tokens}")
        
        client = LLMClient(config)
        print(f"✓ Client initialized")
        
        # Test connection
        print(f"\n🔄 Testing connection...")
        is_connected = await client.test_connection()
        
        if is_connected:
            print(f"✅ Connection successful!\n")
        else:
            print(f"❌ Connection failed\n")
            return False
        
        # Test simple completion
        print(f"🔄 Testing completion...")
        response = await client.complete(
            prompt="What is 2+2? Answer with just the number.",
            max_tokens=10,
        )
        print(f"✅ Response: {response}\n")
        
        # Test with system prompt
        print(f"🔄 Testing with system prompt...")
        response = await client.complete(
            prompt="Say hello in a friendly way.",
            system_prompt="You are a helpful assistant.",
            max_tokens=50,
        )
        print(f"✅ Response: {response}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_free_models():
    """Test multiple free models"""
    print("\n" + "=" * 60)
    print("Testing Available Free Models")
    print("=" * 60)
    
    test_models = [
        'meta-llama/llama-3.2-3b-instruct:free',
        'google/gemini-flash-1.5:free',
        'mistralai/mistral-7b-instruct:free',
    ]
    
    for model in test_models:
        print(f"\n📋 Testing: {model}")
        print("-" * 60)
        
        try:
            config = LLMConfig.from_env()
            config.model = model
            client = LLMClient(config)
            
            response = await client.complete(
                prompt="What is AI? Answer in one short sentence.",
                max_tokens=50,
            )
            
            print(f"✅ Success!")
            print(f"   Response: {response}")
            
        except Exception as e:
            print(f"❌ Failed: {e}")


async def test_data_extraction():
    """Test structured data extraction"""
    print("\n" + "=" * 60)
    print("Testing Data Extraction")
    print("=" * 60)
    
    try:
        client = LLMClient()
        
        content = """
        Product: iPhone 15 Pro
        Price: $999
        Color: Natural Titanium
        Storage: 256GB
        """
        
        schema = {
            "type": "object",
            "properties": {
                "product": {"type": "string"},
                "price": {"type": "number"},
                "color": {"type": "string"},
                "storage": {"type": "string"},
            }
        }
        
        print(f"🔄 Extracting structured data...")
        result = await client.extract_structured_data(
            content=content,
            schema=schema,
        )
        
        print(f"✅ Extraction successful!")
        import json
        print(json.dumps(result, indent=2))
        
        return True
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return False


async def show_available_models():
    """Display all available free models"""
    print("\n" + "=" * 60)
    print("Available Free Models")
    print("=" * 60)
    
    print("\n📦 Models you can use without any cost:\n")
    
    for name, model_id in AVAILABLE_FREE_MODELS.items():
        print(f"  • {name}")
        print(f"    {model_id}")
        print()


async def main():
    """Run all tests"""
    print("\n" + "🚀" * 30)
    print("LLM Connection Test Suite")
    print("🚀" * 30 + "\n")
    
    # Show available models
    await show_available_models()
    
    # Test default model
    success = await test_default_model()
    
    if not success:
        print("\n⚠️  Default model test failed. Please check:")
        print("   1. Your OPENROUTER_API_KEY in .env file")
        print("   2. Your internet connection")
        print("   3. OpenRouter API status")
        return
    
    # Test data extraction
    await test_data_extraction()
    
    # Optional: Test other free models
    print("\n❓ Would you like to test other free models? (This will take a minute)")
    print("   Comment/uncomment in the script to enable.")
    # await test_free_models()
    
    print("\n" + "=" * 60)
    print("✅ All Tests Completed!")
    print("=" * 60)
    print("\nYou're all set to use the LLM integration!")
    print("Check FREE_MODELS.md for more information about available models.\n")


if __name__ == '__main__':
    asyncio.run(main())
