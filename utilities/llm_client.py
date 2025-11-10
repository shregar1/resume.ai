"""Utilities for Google Gemini LLM interactions."""
from typing import List, Optional

from abstractions.utility import IUtility

class LLMClientUtility(IUtility):
    """Client for interacting with Google Gemini."""

    def __init__(
        self,
        urn: str = None,
        user_urn: str = None,
        api_name: str = None,
        user_id: str = None,
        conversational_llm_model: str = None,
        embedding_llm_model: str = None
    ) -> None:
        super().__init__(urn, user_urn, api_name, user_id)
        self.conversational_llm_model = conversational_llm_model
        self.embedding_llm_model = embedding_llm_model

    @property
    def conversational_llm_model(self):
        return self.conversational_llm_model

    @conversational_llm_model.setter
    def conversational_llm_model(self, value):
        self.conversational_llm_model = value

    @property
    def embedding_llm_model(self):
        return self.embedding_llm_model

    @embedding_llm_model.setter
    def embedding_llm_model(self, value):
        self.embedding_llm_model = value

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = 0.7,
        max_tokens: Optional[int] = 4096
    ) -> str:
        """Generate text using Google Gemini.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (prepended to user prompt)
            model: Model name (optional, uses default)
            temperature: Sampling temperature (default: 0.7)
            max_tokens: Maximum tokens to generate (default: 4096)
            
        Returns:
            Generated text
        """
        model = model or self._conversational_llm_model
        
        try:
            # Combine system prompt with user prompt if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Use Google client to generate text
            response = await self.google_client.generate(
                prompt=full_prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response
        
        except Exception as e:
            self.logger.error(f"Error generating text with Gemini: {e}")
            raise
    
    async def generate_embeddings(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """Generate embeddings for texts using Google Gemini.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """

        try:
            return await self.google_client.generate_embeddings(
                texts=texts,
                model=self.embedding_llm_model
            )
        
        except Exception as e:
            self.logger.error(f"Error generating embeddings with Gemini: {e}")
            raise