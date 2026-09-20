"""
LLM Provider - Unified interface supporting OpenRouter and Ollama fallback
"""
import logging
from typing import Optional
from llm.llm_client import LLMClient
from llm.ollama_client import OllamaClient
from llm.llm_config import LLMConfig

logger = logging.getLogger(__name__)


class LLMProvider:
    """
    Unified LLM provider that tries OpenRouter first, falls back to Ollama
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize LLM provider with fallback support"""
        self.config = config or LLMConfig.from_env()
        self.primary_client = None
        self.fallback_client = None
        self.active_provider = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize both clients but don't test yet"""
        # Always initialize OpenRouter as primary
        self.primary_client = LLMClient(self.config)
        logger.info(f"✓ OpenRouter client initialized (model: {self.config.model})")
        
        # Initialize Ollama as fallback if enabled
        if self.config.use_ollama_fallback:
            self.fallback_client = OllamaClient(
                model=self.config.ollama_model,
                base_url=self.config.ollama_url
            )
            logger.info(f"✓ Ollama fallback initialized (model: {self.config.ollama_model})")
    
    async def _test_primary(self) -> bool:
        """Test OpenRouter connection"""
        try:
            logger.info("Testing OpenRouter connection...")
            result = await self.primary_client.test_connection()
            if result:
                logger.info("✅ OpenRouter is working")
                self.active_provider = "openrouter"
                return True
            logger.warning("⚠️ OpenRouter test failed")
            return False
        except Exception as e:
            logger.warning(f"⚠️ OpenRouter error: {e}")
            return False
    
    async def _test_fallback(self) -> bool:
        """Test Ollama connection"""
        if not self.fallback_client:
            return False
        try:
            logger.info("Testing Ollama fallback...")
            result = await self.fallback_client.test_connection()
            if result:
                logger.info("✅ Ollama is working")
                self.active_provider = "ollama"
                return True
            logger.warning("⚠️ Ollama test failed")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Ollama error: {e}")
            return False
    
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Get completion with automatic fallback
        
        Tries OpenRouter first, falls back to Ollama if needed
        """
        # If no active provider yet, test both
        if not self.active_provider:
            if not await self._test_primary():
                if not await self._test_fallback():
                    raise RuntimeError("No LLM provider available (OpenRouter and Ollama both failed)")
        
        # Try active provider
        try:
            if self.active_provider == "openrouter":
                return await self.primary_client.complete(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    **kwargs
                )
            else:
                return await self.fallback_client.complete(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=kwargs.get('temperature', 0.7),
                    max_tokens=kwargs.get('max_tokens', 1024),
                )
        except Exception as e:
            logger.warning(f"Active provider ({self.active_provider}) failed: {e}")
            
            # Try to switch to fallback if currently on primary
            if self.active_provider == "openrouter" and self.fallback_client:
                logger.info("Switching to Ollama fallback...")
                if await self._test_fallback():
                    return await self.fallback_client.complete(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=kwargs.get('temperature', 0.7),
                        max_tokens=kwargs.get('max_tokens', 1024),
                    )
            
            raise RuntimeError(f"LLM completion failed: {e}")
    
    async def test_all_providers(self) -> dict:
        """Test all available providers and return status"""
        status = {
            "openrouter": False,
            "ollama": False,
            "active": None
        }
        
        if await self._test_primary():
            status["openrouter"] = True
            status["active"] = "openrouter"
        
        if await self._test_fallback():
            status["ollama"] = True
            if not status["active"]:
                status["active"] = "ollama"
        
        return status
