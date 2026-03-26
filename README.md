# AI Assistant Web App

A full-stack AI chat assistant using **Flask** and **LangChain** with an **API-based LLM provider** (OpenRouter or Groq). No local model downloads.

## Features

- **LangChain integration** – Chains and prompts with an API-backed LLM
- **API-based LLM** – Use OpenRouter *or* Groq (no local models)
- **Conversation memory** – Per-session history so the assistant remembers context
- **Chat interface** – Modern, responsive UI with message history
- **Modular structure** – Separate config, LLM, and routes
- **Environment-based config** – API keys and settings via `.env`
- **Error handling** – Clear errors in API and UI

## Tech Stack

- **Backend:** Python, Flask
- **LLM:** LangChain + OpenAI-compatible API (OpenRouter or Groq)
- **Frontend:** HTML, CSS, JavaScript (vanilla)

## Setup

1. **Clone or navigate to the project**
   ```bash
   cd ChatBot
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   # source venv/bin/activate   # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   - Copy `.env.example` to `.env`
   - Choose your provider and add the matching API key
   - Example for **OpenRouter**:
     ```
     LLM_PROVIDER=openrouter
     OPENROUTER_API_KEY=your_key_here
     OPENROUTER_MODEL=openai/gpt-4o-mini
     ```
   - Example for **Groq**:
     ```
     LLM_PROVIDER=groq
     GROQ_API_KEY=your_key_here
     GROQ_MODEL=llama-3.1-70b-versatile
     ```

5. **Run the app**
   ```bash
   python app.py
   ```
   Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Project Structure

```
ChatBot/
├── app.py              # Flask app entry point
├── config.py           # Loads settings from .env
├── requirements.txt
├── .env.example
├── llm/
│   ├── __init__.py
│   └── chain.py        # LangChain + OpenRouter + session memory
├── routes/
│   ├── __init__.py
│   └── chat.py         # POST /api/chat, GET /api/history, GET /api/health
├── static/
│   ├── css/style.css
│   └── js/app.js
└── templates/
    └── index.html
```

## API

- **POST /api/chat** – Send a message, get AI response. Body: `{"message": "your text"}`.
- **GET /api/history** – Get conversation history for the current session.
- **GET /api/health** – Health check.

## License

MIT.
