/**
 * AI Assistant - Frontend logic
 *
 * Handles:
 * - Sending user messages to /api/chat
 * - Displaying user and assistant messages
 * - Loading conversation history on page load
 * - Error handling and loading states
 */

(function () {
  "use strict";

  // ---- DOM elements ----
  const chatForm = document.getElementById("chatForm");
  const userInput = document.getElementById("userInput");
  const sendBtn = document.getElementById("sendBtn");
  const messagesContainer = document.getElementById("messages");
  const welcomeEl = document.getElementById("welcome");
  const statusEl = document.getElementById("status");

  // ---- State ----
  let isWaitingForResponse = false;

  /**
   * Announce to screen readers (e.g. "Message sent", "Error occurred")
   */
  function announceStatus(text) {
    if (statusEl) {
      statusEl.textContent = text;
      setTimeout(function () {
        statusEl.textContent = "";
      }, 1000);
    }
  }

  /**
   * Add a message bubble to the chat UI.
   * @param {string} role - "user" or "assistant" or "error"
   * @param {string} content - Plain text content to display
   */
  function appendMessage(role, content) {
    const wrap = document.createElement("div");
    wrap.className = "message message--" + role;
    wrap.setAttribute("data-role", role);

    const roleLabel = document.createElement("div");
    roleLabel.className = "message__role";
    roleLabel.textContent = role === "user" ? "You" : role === "assistant" ? "Assistant" : "Error";

    const contentEl = document.createElement("p");
    contentEl.className = "message__content";
    contentEl.textContent = content;

    wrap.appendChild(roleLabel);
    wrap.appendChild(contentEl);
    messagesContainer.appendChild(wrap);

    // Scroll to bottom
    wrap.scrollIntoView({ behavior: "smooth", block: "end" });
  }

  /**
   * Show a "typing" indicator while waiting for the API.
   * @returns {HTMLElement} The typing element so we can remove it later
   */
  function showTyping() {
    const wrap = document.createElement("div");
    wrap.className = "typing";
    wrap.setAttribute("aria-live", "polite");
    wrap.innerHTML = '<div class="typing__dots"><span></span><span></span><span></span></div>';
    messagesContainer.appendChild(wrap);
    wrap.scrollIntoView({ behavior: "smooth", block: "end" });
    return wrap;
  }

  /**
   * Load conversation history from the server and render it.
   * Called once on page load so refresh keeps history.
   */
  function loadHistory() {
    fetch("/api/history", { method: "GET" })
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        if (data.error) {
          console.warn("Could not load history:", data.error);
          return;
        }
        var messages = data.messages || [];
        if (messages.length > 0) {
          welcomeEl.classList.add("hidden");
        }
        messages.forEach(function (msg) {
          var role = msg.role === "human" ? "user" : msg.role;
          appendMessage(role, msg.content || "");
        });
      })
      .catch(function (err) {
        console.warn("Failed to load history:", err);
      });
  }

  /**
   * Send the user message to the API and handle the response.
   * @param {string} message - User input text
   */
  function sendMessage(message) {
    if (isWaitingForResponse || !message.trim()) return;

    isWaitingForResponse = true;
    sendBtn.disabled = true;
    userInput.disabled = true;

    // Show user message and hide welcome
    appendMessage("user", message.trim());
    welcomeEl.classList.add("hidden");

    var typingEl = showTyping();
    announceStatus("Sending message…");

    fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: message.trim() }),
    })
      .then(function (res) {
        return res.json().then(function (data) {
          return { ok: res.ok, status: res.status, data: data };
        });
      })
      .then(function (result) {
        typingEl.remove();

        if (result.ok && result.data.response != null) {
          appendMessage("assistant", result.data.response);
          announceStatus("Reply received.");
        } else {
          var errorMsg = result.data && result.data.error ? result.data.error : "Something went wrong.";
          appendMessage("error", errorMsg);
          announceStatus("Error: " + errorMsg);
        }
      })
      .catch(function (err) {
        typingEl.remove();
        appendMessage("error", "Network or server error. Please try again.");
        announceStatus("Error occurred.");
        console.error(err);
      })
      .finally(function () {
        isWaitingForResponse = false;
        sendBtn.disabled = false;
        userInput.disabled = false;
        userInput.value = "";
        userInput.focus();
      });
  }

  // ---- Event listeners ----

  chatForm.addEventListener("submit", function (e) {
    e.preventDefault();
    var text = userInput.value.trim();
    if (text) sendMessage(text);
  });

  // Optional: auto-resize textarea
  userInput.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = Math.min(this.scrollHeight, 160) + "px";
  });

  // Load any existing conversation history on page load
  loadHistory();
})();
