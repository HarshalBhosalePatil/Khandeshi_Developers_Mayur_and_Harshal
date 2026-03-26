"""
Flask application entry point for the AI Assistant.

Creates the app, loads configuration from environment variables,
registers blueprints, and serves the chat UI.
"""

import os
from flask import Flask, render_template

from config import Config
from routes.chat import chat_bp


def create_app() -> Flask:
    """Application factory: create and configure the Flask app."""
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Load config from Config class (which reads .env)
    app.config.from_object(Config)
    # Ensure secret key is set for session encryption
    if not app.config.get("SECRET_KEY") or app.config["SECRET_KEY"] == "dev-secret-change-in-production":
        app.config["SECRET_KEY"] = os.urandom(24).hex()

    # Build LLM config for routes based on provider
    provider = (Config.LLM_PROVIDER or "openrouter").lower()
    app.config["LLM_PROVIDER"] = provider

    if provider == "groq":
        if Config.GROQ_API_KEY:
            app.config["LLM_CONFIG"] = {
                "api_key": Config.GROQ_API_KEY,
                "model": Config.GROQ_MODEL,
                "base_url": Config.GROQ_BASE_URL,
                "temperature": 0.7,
                # Groq doesn't need OpenRouter-specific headers
                "default_headers": None,
            }
        else:
            app.config["LLM_CONFIG"] = None
            app.logger.warning(
                "LLM_PROVIDER=groq but GROQ_API_KEY is not set. "
                "Copy .env.example to .env and add your Groq key. "
                "Chat will return an error until then."
            )
    else:
        # Default to OpenRouter
        if Config.OPENROUTER_API_KEY:
            app.config["LLM_CONFIG"] = {
                "api_key": Config.OPENROUTER_API_KEY,
                "model": Config.OPENROUTER_MODEL,
                "base_url": Config.OPENROUTER_BASE_URL,
                "temperature": 0.7,
                # Optional headers used by OpenRouter for rankings/analytics
                "default_headers": {
                    "HTTP-Referer": "https://github.com/your-repo/chatbot",
                    "X-Title": "AI Assistant",
                },
            }
        else:
            app.config["LLM_CONFIG"] = None
            app.logger.warning(
                "LLM_PROVIDER=openrouter but OPENROUTER_API_KEY is not set. "
                "Copy .env.example to .env and add your OpenRouter key. "
                "Chat will return an error until then."
            )

    # Register the chat API blueprint
    app.register_blueprint(chat_bp)

    # Serve the single-page chat UI
    @app.route("/")
    def index():
        """Serve the main chat interface."""
        return render_template("index.html")

    return app


# Create the app instance for run/debug
app = create_app()

if __name__ == "__main__":
    # Run with: python app.py (development only)
    app.run(host="0.0.0.0", port=5500, debug=Config.DEBUG)
