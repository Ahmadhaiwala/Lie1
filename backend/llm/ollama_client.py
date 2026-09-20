"""
Ollama LLM Client - Use local models via Ollama
Fallback when OpenRouter API fails
"""
import asyncio
import json
import logging
from typing import Optional
import aiohttp

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with local Ollama models"""
    
    def __init__(self, model: str = "phi4-mini", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client
        
        Args:
            model: Model name (e.g., 'phi4-mini', 'qwen2.5-coder:1.5b', 'llama3')
            base_url: Ollama server URL
        """
        self.model = model
        self.base_url = base_url
        self.endpoint = f"{base_url}/api/generate"
    
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """
        Get a completion from Ollama
        
        Args:
            prompt: User prompt/question
            system_prompt: Optional system prompt
            temperature: Temperature setting
            max_tokens: Maximum tokens in response
            
        Returns:
            LLM response as string
        """
        # Build full prompt with system context
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "temperature": temperature,
            "num_predict": max_tokens,
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=120)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.endpoint, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get("response", "").strip()
                        logger.info(f"✓ Ollama ({self.model}) generated response ({len(result)} chars)")
                        return result
                    else:
                        logger.error(f"Ollama error: {response.status}")
                        raise RuntimeError(f"Ollama request failed with status {response.status}")
        except asyncio.TimeoutError:
            logger.error("Ollama request timed out (120s)")
            raise RuntimeError("Ollama request timed out")
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            raise RuntimeError(f"Ollama connection failed: {e}")
    
    async def test_connection(self) -> bool:
        """
        Test if Ollama is running and model is available
        
        Returns:
            True if connection successful
        """
        try:
            response = await self.complete(
                prompt="Say 'OK' if you can read this.",
                max_tokens=10,
            )
            return "ok" in response.lower()
        except Exception as e:
            logger.error(f"Ollama connection test failed: {e}")
            return False
