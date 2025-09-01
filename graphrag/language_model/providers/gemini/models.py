# Copyright (c) 2025 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing Gemini model provider definitions."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

import google.generativeai as genai

from graphrag.language_model.response.base import (
    BaseModelOutput,
    BaseModelResponse,
    ModelResponse,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from graphrag.cache.pipeline_cache import PipelineCache
    from graphrag.callbacks.workflow_callbacks import WorkflowCallbacks
    from graphrag.config.models.language_model_config import (
        LanguageModelConfig,
    )

logger = logging.getLogger(__name__)


class GeminiChatProvider:
    """A Gemini Chat Model provider using Google's Generative AI library."""

    def __init__(
        self,
        *,
        name: str,
        config: LanguageModelConfig,
        callbacks: WorkflowCallbacks | None = None,
        cache: PipelineCache | None = None,
    ) -> None:
        """Initialize the Gemini provider."""
        # Configure the Gemini API
        genai.configure(api_key=config.api_key)
        
        # Set up the model (use gemini-1.5-flash by default, which is more widely available)
        model_name = config.model or "gemini-1.5-flash"
        self.model = genai.GenerativeModel(model_name)
        
        # Override encoding_model to avoid tiktoken issues
        config.encoding_model = "cl100k_base"  # Use a default encoding that works
        
        self.config = config
        self.callbacks = callbacks
        self.cache = cache
        self.name = name
        
        logger.info(f"Initialized Gemini provider with model: {model_name}")

    async def achat(
        self, prompt: str, history: list | None = None, **kwargs
    ) -> ModelResponse:
        """
        Chat with the Gemini model using the given prompt.

        Args:
            prompt: The prompt to chat with.
            history: Optional conversation history.
            kwargs: Additional arguments to pass to the model.

        Returns
        -------
            The response from the model.
        """
        try:
            # If history is provided, we need to format it for Gemini
            if history:
                # Convert history to Gemini format
                chat = self.model.start_chat(history=self._convert_history(history))
                response = await asyncio.to_thread(chat.send_message, prompt, **kwargs)
            else:
                # Simple generation without history
                response = await asyncio.to_thread(
                    self.model.generate_content, prompt, **kwargs
                )
            
            # Extract the text content
            content = response.text if hasattr(response, 'text') else str(response)
            
            return BaseModelResponse(
                output=BaseModelOutput(
                    content=content,
                    full_response={"response": content, "model": self.config.model},
                ),
                parsed_response=None,
                history=history or [],
                cache_hit=False,  # Gemini doesn't expose cache info directly
                tool_calls=None,
                metrics=None,
            )
            
        except Exception as e:
            logger.error(f"Error in Gemini chat: {e}")
            raise

    async def achat_stream(
        self, prompt: str, history: list | None = None, **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream Chat with the Gemini model using the given prompt.

        Args:
            prompt: The prompt to chat with.
            history: Optional conversation history.
            kwargs: Additional arguments to pass to the model.

        Returns
        -------
            A generator that yields strings representing the response.
        """
        try:
            if history:
                chat = self.model.start_chat(history=self._convert_history(history))
                response = await asyncio.to_thread(
                    chat.send_message, prompt, stream=True, **kwargs
                )
            else:
                response = await asyncio.to_thread(
                    self.model.generate_content, prompt, stream=True, **kwargs
                )
            
            for chunk in response:
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Error in Gemini stream chat: {e}")
            raise

    def chat(self, prompt: str, history: list | None = None, **kwargs) -> ModelResponse:
        """
        Synchronous chat with the Gemini model.

        Args:
            prompt: The prompt to chat with.
            history: Optional conversation history.
            kwargs: Additional arguments to pass to the model.

        Returns
        -------
            The response from the model.
        """
        return asyncio.run(self.achat(prompt, history=history, **kwargs))

    def chat_stream(
        self, prompt: str, history: list | None = None, **kwargs
    ) -> Generator[str, None]:
        """
        Synchronous stream chat with the Gemini model.

        Args:
            prompt: The prompt to chat with.
            history: Optional conversation history.
            kwargs: Additional arguments to pass to the model.

        Returns
        -------
            A generator that yields strings representing the response.
        """
        async def _async_generator():
            async for chunk in self.achat_stream(prompt, history=history, **kwargs):
                yield chunk
        
        # Convert async generator to sync
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async_gen = _async_generator()
            while True:
                try:
                    yield loop.run_until_complete(async_gen.__anext__())
                except StopAsyncIteration:
                    break
        finally:
            loop.close()

    def _convert_history(self, history: list) -> list:
        """
        Convert GraphRAG history format to Gemini format.
        
        Args:
            history: History in GraphRAG format
            
        Returns:
            History in Gemini format
        """
        gemini_history = []
        for entry in history:
            if isinstance(entry, dict):
                role = entry.get("role", "user")
                content = entry.get("content", "")
                
                # Map roles to Gemini format
                if role == "assistant":
                    gemini_role = "model"
                else:
                    gemini_role = "user"
                
                gemini_history.append({
                    "role": gemini_role,
                    "parts": [content]
                })
            else:
                # If it's just a string, treat as user message
                gemini_history.append({
                    "role": "user", 
                    "parts": [str(entry)]
                })
        
        return gemini_history


class GeminiEmbeddingProvider:
    """A Gemini Embedding Model provider using Google's Generative AI library."""

    def __init__(
        self,
        *,
        name: str,
        config: LanguageModelConfig,
        callbacks: WorkflowCallbacks | None = None,
        cache: PipelineCache | None = None,
    ) -> None:
        """Initialize the Gemini embedding provider."""
        # Configure the Gemini API
        genai.configure(api_key=config.api_key)
        
        # Use embedding model (text-embedding-004 or similar)
        self.model_name = config.model or "models/text-embedding-004"
        
        # Override encoding_model to avoid tiktoken issues
        config.encoding_model = "cl100k_base"  # Use a default encoding that works
        
        self.config = config
        self.callbacks = callbacks
        self.cache = cache
        self.name = name
        
        logger.info(f"Initialized Gemini embedding provider with model: {self.model_name}")

    async def aembed_batch(self, text_list: list[str], **kwargs) -> list[list[float]]:
        """
        Embed a batch of texts using the Gemini model.

        Args:
            text_list: List of texts to embed.
            kwargs: Additional arguments to pass to the model.

        Returns
        -------
            List of embeddings for each text.
        """
        try:
            embeddings = []
            for text in text_list:
                result = await asyncio.to_thread(
                    genai.embed_content,
                    model=self.model_name,
                    content=text,
                    **kwargs
                )
                embeddings.append(result['embedding'])
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error in Gemini batch embedding: {e}")
            raise

    async def aembed(self, text: str, **kwargs) -> list[float]:
        """
        Embed a single text using the Gemini model.

        Args:
            text: The text to embed.
            kwargs: Additional arguments to pass to the model.

        Returns
        -------
            The embedding vector for the text.
        """
        try:
            result = await asyncio.to_thread(
                genai.embed_content,
                model=self.model_name,
                content=text,
                **kwargs
            )
            return result['embedding']
            
        except Exception as e:
            logger.error(f"Error in Gemini embedding: {e}")
            raise

    def embed_batch(self, text_list: list[str], **kwargs) -> list[list[float]]:
        """
        Synchronously embed a batch of texts.

        Args:
            text_list: List of texts to embed.
            kwargs: Additional arguments to pass to the model.

        Returns
        -------
            List of embeddings for each text.
        """
        return asyncio.run(self.aembed_batch(text_list, **kwargs))

    def embed(self, text: str, **kwargs) -> list[float]:
        """
        Synchronously embed a single text.

        Args:
            text: The text to embed.
            kwargs: Additional arguments to pass to the model.

        Returns
        -------
            The embedding vector for the text.
        """
        return asyncio.run(self.aembed(text, **kwargs))
