"""
Test cases for LLM Client
"""
import pytest
import asyncio
import json
from llm import LLMClient, LLMConfig, PromptTemplates


class TestLLMClient:
    """Test suite for LLMClient"""
    
    @pytest.mark.asyncio
    async def test_llm_initialization(self):
        """Test LLM client can be initialized"""
        config = LLMConfig.from_env()
        client = LLMClient(config)
        
        assert client.config.api_key is not None
        assert client.client is not None
    
    @pytest.mark.asyncio
    async def test_connection(self):
        """Test API connection works"""
        client = LLMClient()
        result = await client.test_connection()
        
        assert result == True
    
    @pytest.mark.asyncio
    async def test_simple_completion(self):
        """Test basic completion"""
        client = LLMClient()
        
        response = await client.complete(
            prompt="What is 2+2? Answer with just the number.",
            max_tokens=10,
        )
        
        assert response is not None
        assert len(response) > 0
        assert '4' in response
    
    @pytest.mark.asyncio
    async def test_completion_with_system_prompt(self):
        """Test completion with system prompt"""
        client = LLMClient()
        
        response = await client.complete(
            prompt="Say hello",
            system_prompt="You are a friendly assistant.",
            max_tokens=50,
        )
        
        assert response is not None
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_completion_with_context(self):
        """Test completion with additional context"""
        client = LLMClient()
        
        context = "The capital of France is Paris. It is known for the Eiffel Tower."
        question = "What is the capital of France?"
        
        response = await client.complete_with_context(
            prompt=question,
            context=context,
            max_tokens=50,
        )
        
        assert 'paris' in response.lower()
    
    @pytest.mark.asyncio
    async def test_extract_structured_data(self):
        """Test structured data extraction"""
        client = LLMClient()
        
        content = """
        Product: iPhone 15 Pro
        Price: $999
        Features: 
        - A17 Pro chip
        - Titanium design
        - USB-C port
        Rating: 4.5/5
        """
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "price": {"type": "number"},
                "features": {"type": "array", "items": {"type": "string"}},
                "rating": {"type": "number"},
            }
        }
        
        result = await client.extract_structured_data(
            content=content,
            schema=schema,
        )
        
        assert isinstance(result, dict)
        assert 'name' in result or 'price' in result
    
    @pytest.mark.asyncio
    async def test_summarize(self):
        """Test content summarization"""
        client = LLMClient()
        
        content = """
        Artificial Intelligence (AI) is transforming industries worldwide. 
        From healthcare to finance, AI systems are being deployed to automate 
        tasks, provide insights, and enhance decision-making. Machine learning, 
        a subset of AI, enables systems to learn from data without explicit 
        programming. Deep learning, using neural networks, has achieved 
        remarkable results in image recognition, natural language processing, 
        and game playing.
        """
        
        summary = await client.summarize(
            content=content,
            max_length=50,
            style="concise",
        )
        
        assert summary is not None
        assert len(summary) < len(content)
        assert len(summary) > 10
    
    @pytest.mark.asyncio
    async def test_answer_question(self):
        """Test question answering"""
        client = LLMClient()
        
        context = """
        Python is a high-level programming language created by Guido van Rossum 
        and first released in 1991. It emphasizes code readability and allows 
        developers to write clear, logical code.
        """
        
        answer = await client.answer_question(
            question="When was Python first released?",
            context=context,
        )
        
        assert '1991' in answer
    
    @pytest.mark.asyncio
    async def test_batch_complete(self):
        """Test batch completions"""
        client = LLMClient()
        
        prompts = [
            "What is 1+1?",
            "What is 2+2?",
            "What is 3+3?",
        ]
        
        responses = await client.batch_complete(
            prompts=prompts,
            max_tokens=10,
        )
        
        assert len(responses) == 3
        assert all(len(r) > 0 for r in responses)


class TestLLMConfig:
    """Test suite for LLMConfig"""
    
    def test_config_from_env(self):
        """Test creating config from environment"""
        config = LLMConfig.from_env()
        
        assert config.api_key is not None
        assert config.base_url == "https://openrouter.ai/api/v1"
        assert config.model is not None
    
    def test_config_to_dict(self):
        """Test converting config to dict"""
        config = LLMConfig.from_env()
        config_dict = config.to_dict()
        
        assert 'model' in config_dict
        assert 'temperature' in config_dict
        assert 'max_tokens' in config_dict


class TestPromptTemplates:
    """Test suite for PromptTemplates"""
    
    def test_system_prompts_exist(self):
        """Test that all system prompts are accessible"""
        prompts = [
            PromptTemplates.web_content_analyzer(),
            PromptTemplates.data_extractor(),
            PromptTemplates.article_summarizer(),
            PromptTemplates.qa_assistant(),
        ]
        
        assert all(isinstance(p, str) and len(p) > 0 for p in prompts)
    
    def test_schema_templates_exist(self):
        """Test that schema templates are valid"""
        schemas = [
            PromptTemplates.product_info_extractor(),
            PromptTemplates.article_metadata_extractor(),
            PromptTemplates.contact_info_extractor(),
            PromptTemplates.job_posting_extractor(),
            PromptTemplates.event_info_extractor(),
        ]
        
        assert all(isinstance(s, dict) for s in schemas)
        assert all('type' in s for s in schemas)
        assert all('properties' in s for s in schemas)
    
    def test_create_extraction_prompt(self):
        """Test prompt creation"""
        schema = PromptTemplates.product_info_extractor()
        content = "iPhone 15 costs $999"
        
        prompt = PromptTemplates.create_extraction_prompt(
            content=content,
            schema=schema,
        )
        
        assert isinstance(prompt, str)
        assert 'Schema' in prompt
        assert 'Content' in prompt
        assert content in prompt
