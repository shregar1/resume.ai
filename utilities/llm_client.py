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
        self._conversational_llm_model = conversational_llm_model
        self._embedding_llm_model = embedding_llm_model

    @property
    def conversational_llm_model(self):
        return self._conversational_llm_model

    @conversational_llm_model.setter
    def conversational_llm_model(self, value):
        self._conversational_llm_model = value

    @property
    def embedding_llm_model(self):
        return self._embedding_llm_model

    @embedding_llm_model.setter
    def embedding_llm_model(self, value):
        self._embedding_llm_model = value

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
        self.logger.info(f"Generating text with model={model}, temp={temperature}, max_tokens={max_tokens}")
        self.logger.debug(f"Prompt length: {len(prompt)} chars, System prompt: {'Yes' if system_prompt else 'No'}")
        
        try:
            # Combine system prompt with user prompt if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
                self.logger.debug(f"Combined full prompt length: {len(full_prompt)} chars")
            
            # Use Google client to generate text
            response = await self.google_client.generate(
                prompt=full_prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            self.logger.info(f"Generated text successfully. Response length: {len(response)} chars")
            return response
        
        except Exception as e:
            self.logger.error(f"Error generating text with Gemini: {e}", exc_info=True)
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
        self.logger.info(f"Generating embeddings for {len(texts)} texts")
        self.logger.debug(f"Average text length: {sum(len(t) for t in texts) / len(texts):.0f} chars")
        
        try:
            embeddings = await self.google_client.generate_embeddings(
                texts=texts,
                model=self.embedding_llm_model
            )
            self.logger.info(f"Successfully generated {len(embeddings)} embeddings")
            return embeddings
        
        except Exception as e:
            self.logger.error(f"Error generating embeddings with Gemini: {e}", exc_info=True)
            raise