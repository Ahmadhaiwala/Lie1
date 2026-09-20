"""
LLM Client for OpenRouter API
"""
import asyncio
from typing import Optional, List, Dict, Any, AsyncGenerator
import json
from openai import AsyncOpenAI
from llm.llm_config import LLMConfig


class LLMClient:
    """Client for interacting with LLMs via OpenRouter"""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM client
        
        Args:
            config: LLMConfig instance with API settings
        """
        self.config = config or LLMConfig.from_env()
        
        # Initialize OpenAI client with OpenRouter endpoint
        self.client = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            default_headers={
                "HTTP-Referer": self.config.site_url or "http://localhost",
                "X-Title": self.config.app_name or "Crawl4AI-Backend",
            },
            timeout=self.config.timeout,
            max_retries=self.config.max_retries,
        )
    
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> str:
        """
        Get a completion from the LLM
        
        Args:
            prompt: User prompt/question
            system_prompt: Optional system prompt
            model: Model to use (overrides config)
            temperature: Temperature (overrides config)
            max_tokens: Max tokens (overrides config)
            json_mode: Whether to request JSON output
            
        Returns:
            LLM response as string
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        kwargs = {
            "model": model or self.config.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
        }
        
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        
        response = await self.client.chat.completions.create(**kwargs)
        
        return response.choices[0].message.content
    
    async def complete_with_context(
        self,
        prompt: str,
        context: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Get completion with additional context (e.g., crawled content)
        
        Args:
            prompt: User question/instruction
            context: Additional context (e.g., webpage content)
            system_prompt: Optional system prompt
            **kwargs: Additional arguments for complete()
            
        Returns:
            LLM response
        """
        full_prompt = f"""Context:
{context}

Question/Instruction:
{prompt}"""
        
        return await self.complete(
            prompt=full_prompt,
            system_prompt=system_prompt,
            **kwargs
        )
    
    async def extract_structured_data(
        self,
        content: str,
        schema: Dict[str, Any],
        instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract structured data from content using a schema
        
        Args:
            content: Content to extract from (e.g., HTML/Markdown)
            schema: JSON schema describing desired structure
            instructions: Optional additional instructions
            
        Returns:
            Extracted data as dictionary
        """
        system_prompt = """You are a data extraction expert. Extract information from the provided content according to the schema.
Return ONLY valid JSON matching the schema. Do not include any explanations or markdown formatting."""
        
        prompt = f"""Extract data from the following content according to this schema:

Schema:
{json.dumps(schema, indent=2)}

{f"Instructions: {instructions}" if instructions else ""}

Content:
{content[:10000]}  # Limit to first 10k chars

Return the extracted data as JSON."""
        
        response = await self.complete(
            prompt=prompt,
            system_prompt=system_prompt,
            json_mode=True,
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Failed to parse JSON response: {response}")
    
    async def summarize(
        self,
        content: str,
        max_length: int = 200,
        style: str = "concise",
    ) -> str:
        """
        Summarize content
        
        Args:
            content: Content to summarize
            max_length: Maximum length of summary in words
            style: Summary style (concise, detailed, bullet-points)
            
        Returns:
            Summary text
        """
        system_prompt = "You are an expert at creating clear, informative summaries."
        
        style_instructions = {
            "concise": "Create a brief, concise summary.",
            "detailed": "Create a comprehensive summary covering all key points.",
            "bullet-points": "Create a summary using bullet points for key information.",
        }
        
        prompt = f"""{style_instructions.get(style, style_instructions['concise'])}
Maximum length: {max_length} words

Content:
{content[:15000]}

Summary:"""
        
        return await self.complete(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.5,
        )
    
    async def answer_question(
        self,
        question: str,
        context: str,
        include_sources: bool = True,
    ) -> str:
        """
        Answer a question based on provided context
        
        Args:
            question: Question to answer
            context: Context/content to answer from
            include_sources: Whether to include source references
            
        Returns:
            Answer to the question
        """
        system_prompt = """You are a helpful assistant that answers questions based on provided context.
Only use information from the context. If the answer is not in the context, say so."""
        
        if include_sources:
            system_prompt += " Include references to relevant parts of the context in your answer."
        
        return await self.complete_with_context(
            prompt=question,
            context=context,
            system_prompt=system_prompt,
        )
    
    async def stream_complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream completion tokens as they're generated
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional arguments
            
        Yields:
            Token strings as they're generated
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        stream = await self.client.chat.completions.create(
            model=kwargs.get('model', self.config.model),
            messages=messages,
            temperature=kwargs.get('temperature', self.config.temperature),
            max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
            stream=True,
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def batch_complete(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """
        Complete multiple prompts in parallel
        
        Args:
            prompts: List of prompts
            system_prompt: Optional system prompt for all
            **kwargs: Additional arguments
            
        Returns:
            List of responses
        """
        tasks = [
            self.complete(prompt, system_prompt, **kwargs)
            for prompt in prompts
        ]
        
        return await asyncio.gather(*tasks)
    
    async def test_connection(self) -> bool:
        """
        Test if the API connection is working
        
        Returns:
            True if connection successful
        """
        try:
            response = await self.complete(
                prompt="Say 'OK' if you can read this.",
                max_tokens=10,
            )
            return 'ok' in response.lower()
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
