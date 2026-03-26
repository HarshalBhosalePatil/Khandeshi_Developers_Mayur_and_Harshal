"""
Configuration module - loads settings from environment variables.
Uses python-dotenv to load .env file for local development.
"""

import os
from dotenv import load_dotenv

# Load .env file if it exists (no error if missing)
load_dotenv()


def get_env(key: str, default: str = None, required: bool = False) -> str:
    """
    Get an environment variable with optional default and required check.
    
    Args:
        key: Environment variable name
        default: Default value if not set
        required: If True, raises ValueError when not set
        
    Returns:
        The environment variable value
    """
    value = os.getenv(key, default)
    if required and not value:
        raise ValueError(f"Missing required environment variable: {key}")
    return value or ""


# Application configuration
class Config:
    """Central configuration for the Flask app and LLM."""
    
    # Which provider to use: "openrouter" or "groq"
    LLM_PROVIDER = get_env("LLM_PROVIDER", default="openrouter").strip().lower()

    # OpenRouter API - set in .env; app will show error if missing when chat is used
    OPENROUTER_API_KEY = get_env("OPENROUTER_API_KEY", default="")
    OPENROUTER_MODEL = get_env("OPENROUTER_MODEL", default="openai/gpt-4o-mini")
    
    # OpenRouter API base URL (OpenAI-compatible endpoint)
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

    # Groq API - OpenAI-compatible endpoint
    GROQ_API_KEY = get_env("GROQ_API_KEY", default="")
    GROQ_MODEL = get_env("GROQ_MODEL", default="llama-3.1-70b-versatile")
    GROQ_BASE_URL = "https://api.groq.com/openai/v1"
    
    # Flask
    SECRET_KEY = get_env("FLASK_SECRET_KEY", default="dev-secret-change-in-production")
    DEBUG = get_env("FLASK_DEBUG", default="0").lower() in ("1", "true", "yes")
