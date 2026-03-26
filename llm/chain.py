"""
LangChain chain with OpenRouter LLM and per-session conversation memory.

Uses OpenAI-compatible API (ChatOpenAI) with OpenRouter base URL.
Memory is stored in-memory per session ID for conversation history.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
# In-memory store: session_id -> ChatMessageHistory
# For production, consider Redis or a database
_session_store: dict[str, BaseChatMessageHistory] = {}


def _get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Return chat history for a session. Creates one if it doesn't exist.
    Used by RunnableWithMessageHistory to inject memory into the chain.
    """
    if session_id not in _session_store:
        _session_store[session_id] = ChatMessageHistory()
    return _session_store[session_id]


def create_session_memory(session_id: str) -> None:
    """
    Ensure a session has a history entry (e.g. when user first connects).
    Optional; get_chain_for_session will create it on first use.
    """
    _get_session_history(session_id)


def get_history(session_id: str) -> list[dict]:
    """
    Return conversation history for a session as list of {role, content}.
    Used to display history on page load or for debugging.
    """
    history = _get_session_history(session_id)
    messages = []
    for msg in history.messages:
        role = "user" if msg.type == "human" else "assistant"
        messages.append({"role": role, "content": getattr(msg, "content", str(msg))})
    return messages


def get_chain_for_session(
    session_id: str,
    api_key: str,
    model: str,
    base_url: str = "https://openrouter.ai/api/v1",
    temperature: float = 0.7,
    default_headers: dict | None = None,
):
    """
    Build a LangChain chain with OpenRouter LLM and conversation memory.

    Args:
        session_id: Unique ID for this conversation (e.g. Flask session id)
        api_key: OpenRouter API key
        model: Model name (e.g. openai/gpt-4o-mini)
        base_url: OpenRouter API base URL
        temperature: LLM temperature (0 = deterministic, 1 = creative)

    Returns:
        A runnable chain that takes {"input": "user message"} and returns
        the AI response, with conversation history automatically included.
    """
    # OpenRouter and Groq both expose OpenAI-compatible APIs.
    #
    # IMPORTANT: With our installed `langchain-openai`, the correct parameter names are:
    # - model_name
    # - openai_api_key
    # - openai_api_base   (this is the base URL)
    #
    # If you pass the wrong key name (e.g. `api_key`) or the wrong base URL key
    # (e.g. `base_url`), the request is sent WITHOUT auth headers and you'll see:
    #   401 Missing Authentication header
    #
    # We choose parameter names based on what this ChatOpenAI version supports.
    common_kwargs: dict = {"temperature": temperature}
    if default_headers:
        common_kwargs["default_headers"] = default_headers

    supported = getattr(ChatOpenAI, "model_fields", {}) or {}
    if "openai_api_key" in supported and "openai_api_base" in supported:
        llm = ChatOpenAI(
            model_name=model,
            openai_api_key=api_key,
            openai_api_base=base_url,
            **common_kwargs,
        )
    else:
        # Fallback for older/newer variants (best effort).
        llm = ChatOpenAI(
            model=model,  # type: ignore[arg-type]
            openai_api_key=api_key,  # type: ignore[arg-type]
            base_url=base_url,  # type: ignore[arg-type]
            **common_kwargs,
        )

    # System message to set assistant behavior (optional)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful AI assistant. Answer concisely and clearly. "
                "If you don't know something, say so.",
            ),
            # Placeholder for conversation history (injected by RunnableWithMessageHistory)
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    # Chain: prompt -> LLM
    chain = prompt | llm

    # Wrap with message history so each request gets the right conversation context
    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history=_get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    # Config that tells the runnable which session we're in
    config = {"configurable": {"session_id": session_id}}

    return chain_with_history, config
