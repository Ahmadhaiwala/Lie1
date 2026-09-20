"""
LLM Configuration
"""
from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMConfig:
    """Configuration for LLM interactions"""
    
    # API Configuration
    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"
    
    # Model Settings
    model: str = "meta-llama/llama-3.2-3b-instruct"
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    
    # OpenRouter Specific
    site_url: Optional[str] = None
    app_name: Optional[str] = "Crawl4AI-Backend"
    
    # Retry Settings
    max_retries: int = 3
    timeout: int = 60
    
    @classmethod
    def from_env(cls) -> 'LLMConfig':
        """Create config from environment variables"""
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        
        return cls(
            api_key=api_key,
            model=os.getenv('DEFAULT_MODEL', 'meta-llama/llama-3.2-3b-instruct'),
            temperature=float(os.getenv('LLM_TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('LLM_MAX_TOKENS', '4096')),
        )
    
    def to_dict(self) -> dict:
        """Convert config to dictionary"""
        return {
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p,
        }


# Available FREE models on OpenRouter
AVAILABLE_FREE_MODELS = {
    # Meta LLaMA (Free)
    'llama-3.2-3b': 'meta-llama/llama-3.2-3b-instruct:free',
    'llama-3.2-1b': 'meta-llama/llama-3.2-1b-instruct:free',
    'llama-3.1-8b': 'meta-llama/llama-3.1-8b-instruct:free',
    
    # Google Gemini (Free)
    'gemini-flash-1.5': 'google/gemini-flash-1.5:free',
    'gemini-2.0-flash-exp': 'google/gemini-2.0-flash-exp:free',
    
    # Mistral (Free)
    'mistral-7b': 'mistralai/mistral-7b-instruct:free',
    
    # Microsoft Phi (Free)
    'phi-3-mini': 'microsoft/phi-3-mini-128k-instruct:free',
    'phi-3-medium': 'microsoft/phi-3-medium-128k-instruct:free',
    
    # Qwen (Free)
    'qwen-2-7b': 'qwen/qwen-2-7b-instruct:free',
}

# Available PAID models on OpenRouter (for reference)
AVAILABLE_PAID_MODELS = {
    # Anthropic
    'claude-3.5-sonnet': 'anthropic/claude-3.5-sonnet',
    'claude-3-opus': 'anthropic/claude-3-opus',
    'claude-3-sonnet': 'anthropic/claude-3-sonnet',
    'claude-3-haiku': 'anthropic/claude-3-haiku',
    
    # OpenAI
    'gpt-4-turbo': 'openai/gpt-4-turbo',
    'gpt-4': 'openai/gpt-4',
    'gpt-3.5-turbo': 'openai/gpt-3.5-turbo',
    
    # Google
    'gemini-pro': 'google/gemini-pro',
    'gemini-pro-1.5': 'google/gemini-pro-1.5',
    
    # Meta
    'llama-3-70b': 'meta-llama/llama-3-70b-instruct',
    'llama-3.1-405b': 'meta-llama/llama-3.1-405b-instruct',
}
