"""Utilities for LLM interactions."""

from typing import List, Dict, Any, Optional
import logging
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from src.config import settings


logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with LLM providers."""
    
    def __init__(self):
        """Initialize LLM clients."""
        self.openai_client = None
        self.anthropic_client = None
        
        if settings.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        if settings.anthropic_api_key:
            self.anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        provider: str = "openai"
    ) -> str:
        """Generate text using LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            model: Model name (optional, uses default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            provider: LLM provider (openai or anthropic)
            
        Returns:
            Generated text
        """
        model = model or settings.llm_model
        temperature = temperature or settings.temperature
        max_tokens = max_tokens or settings.max_tokens
        
        try:
            if provider == "openai" and self.openai_client:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = await self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            elif provider == "anthropic" and self.anthropic_client:
                response = await self.anthropic_client.messages.create(
                    model=model if "claude" in model else "claude-3-5-sonnet-20241022",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt or "",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            else:
                raise ValueError(f"Provider {provider} not configured or invalid")
        
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """Generate embeddings for texts.
        
        Args:
            texts: List of texts to embed
            model: Embedding model name
            
        Returns:
            List of embedding vectors
        """
        model = model or settings.embedding_model
        
        try:
            if self.openai_client:
                response = await self.openai_client.embeddings.create(
                    model=model,
                    input=texts
                )
                return [item.embedding for item in response.data]
            else:
                raise ValueError("OpenAI client not configured")
        
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise


# Global LLM client instance
llm_client = LLMClient()

