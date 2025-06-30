# This package handles interactions with Large Language Models.
# Currently focused on a client for Ollama.

from .ollama_client import generate_text, OLLAMA_IS_AVAILABLE, get_default_model_name

__all__ = [
    "generate_text",
    "OLLAMA_IS_AVAILABLE",
    "get_default_model_name"
]
