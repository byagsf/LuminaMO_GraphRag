# Copyright (c) 2025 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing utils for Gemini provider."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from graphrag.callbacks.workflow_callbacks import WorkflowCallbacks
    from graphrag.config.models.language_model_config import (
        LanguageModelConfig,
    )
    from graphrag.index.typing.error_handler import ErrorHandlerFn

logger = logging.getLogger(__name__)


def validate_gemini_config(config: LanguageModelConfig) -> None:
    """
    Validate Gemini configuration.
    
    Args:
        config: The language model configuration
        
    Raises:
        ValueError: If configuration is invalid
    """
    if not config.api_key:
        msg = "Gemini API key is required"
        raise ValueError(msg)
    
    # Validate model name if provided
    if config.model and not config.model.startswith(("gemini-", "models/")):
        logger.warning(f"Model name '{config.model}' may not be valid for Gemini")


def create_error_handler(callbacks: WorkflowCallbacks | None = None) -> ErrorHandlerFn:
    """
    Create an error handler for Gemini operations.
    
    Args:
        callbacks: Optional workflow callbacks
        
    Returns:
        Error handler function
    """
    def on_error(
        error: BaseException | None = None,
        stack: str | None = None,
        details: dict | None = None,
    ) -> None:
        logger.error(
            "Error in Gemini provider",
            exc_info=error,
            extra={"stack": stack, "details": details},
        )
        
        # If callbacks are provided, use them
        if callbacks and hasattr(callbacks, 'on_error'):
            callbacks.on_error(error, stack, details)

    return on_error


def get_gemini_model_parameters(config: LanguageModelConfig) -> dict[str, Any]:
    """
    Extract Gemini-specific model parameters from config.
    
    Args:
        config: The language model configuration
        
    Returns:
        Dictionary of Gemini model parameters
    """
    params = {}
    
    # Map common parameters to Gemini equivalents
    if hasattr(config, 'temperature') and config.temperature is not None:
        params['temperature'] = config.temperature
    
    if hasattr(config, 'max_tokens') and config.max_tokens is not None:
        params['max_output_tokens'] = config.max_tokens
    
    if hasattr(config, 'top_p') and config.top_p is not None:
        params['top_p'] = config.top_p
    
    if hasattr(config, 'top_k') and config.top_k is not None:
        params['top_k'] = config.top_k
    
    # Add any other Gemini-specific parameters
    if hasattr(config, 'candidate_count') and config.candidate_count is not None:
        params['candidate_count'] = config.candidate_count
    
    if hasattr(config, 'stop_sequences') and config.stop_sequences is not None:
        params['stop_sequences'] = config.stop_sequences
    
    return params


def format_gemini_prompt(prompt: str, system_message: str | None = None) -> str:
    """
    Format a prompt for Gemini, optionally including a system message.
    
    Args:
        prompt: The main prompt
        system_message: Optional system message to prepend
        
    Returns:
        Formatted prompt string
    """
    if system_message:
        return f"{system_message}\n\n{prompt}"
    return prompt
