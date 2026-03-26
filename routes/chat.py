"""
Chat API routes - accept user input, call LangChain, return response.

Uses session-based conversation memory keyed by Flask session ID.
"""

import uuid
from flask import Blueprint, request, jsonify, session, current_app

from llm.chain import get_chain_for_session, get_history

chat_bp = Blueprint("chat", __name__, url_prefix="/api")


def _get_or_create_session_id() -> str:
    """Use Flask session to persist a session ID for this browser."""
    if "chat_session_id" not in session:
        session["chat_session_id"] = str(uuid.uuid4())
    return session["chat_session_id"]


@chat_bp.route("/chat", methods=["POST"])
def chat():
    """
    POST /api/chat
    Body: { "message": "user input text" }
    Returns: { "response": "AI reply", "error": null } or { "response": null, "error": "..." }
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        user_message = (data.get("message") or "").strip()

        if not user_message:
            return jsonify({
                "response": None,
                "error": "Message cannot be empty.",
            }), 400

        # Get config from app (set in app factory)
        config_obj = current_app.config.get("LLM_CONFIG")
        if not config_obj:
            return jsonify({
                "response": None,
                "error": "Server configuration error: LLM not configured.",
            }), 500

        session_id = _get_or_create_session_id()
        chain, config = get_chain_for_session(
            session_id=session_id,
            api_key=config_obj["api_key"],
            model=config_obj["model"],
            base_url=config_obj.get("base_url", "https://openrouter.ai/api/v1"),
            temperature=config_obj.get("temperature", 0.7),
            default_headers=config_obj.get("default_headers"),
        )

        # Invoke LangChain: pass user input and session config for memory
        result = chain.invoke(
            {"input": user_message},
            config=config,
        )

        # result is an AIMessage; extract content
        response_text = result.content if hasattr(result, "content") else str(result)

        return jsonify({
            "response": response_text,
            "error": None,
        })

    except ValueError as e:
        # e.g. missing API key from config
        return jsonify({"response": None, "error": str(e)}), 500
    except Exception as e:
        current_app.logger.exception("Chat request failed")
        return jsonify({
            "response": None,
            "error": f"Something went wrong: {str(e)}",
        }), 500


@chat_bp.route("/history", methods=["GET"])
def history():
    """GET /api/history - return conversation history for the current session."""
    try:
        session_id = _get_or_create_session_id()
        messages = get_history(session_id)
        return jsonify({"messages": messages, "error": None})
    except Exception as e:
        current_app.logger.exception("History request failed")
        return jsonify({"messages": [], "error": str(e)}), 500


@chat_bp.route("/health", methods=["GET"])
def health():
    """Simple health check for the API."""
    return jsonify({"status": "ok"})
