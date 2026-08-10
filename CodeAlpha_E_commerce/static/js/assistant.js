(function () {
  const root = document.querySelector("[data-assistant-root]");
  if (!root) return;

  const panel = root.querySelector("[data-assistant-panel]");
  const toggle = root.querySelector("[data-assistant-toggle]");
  const minimizeBtn = root.querySelector("[data-assistant-minimize]");
  const closeBtn = root.querySelector("[data-assistant-close]");
  const form = root.querySelector("[data-assistant-form]");
  const input = root.querySelector("[data-assistant-input]"); 
  const messagesEl = root.querySelector("[data-assistant-messages]");
  const typingEl = root.querySelector("[data-assistant-typing]");
  const clearBtn = root.querySelector("[data-assistant-clear]");
  const historyBtn = root.querySelector("[data-assistant-history]");
  const muteBtn = root.querySelector("[data-assistant-mute-toggle]");
  const voiceBtn = root.querySelector("[data-assistant-voice]");
  const statusEl = root.querySelector("[data-assistant-status]");

  const apiUrl = root.dataset.apiUrl;
  const stateUrl = root.dataset.stateUrl;
  const welcomeMessage = root.dataset.welcomeMessage || "Hello. How can I assist you today?";
  const voiceEnabled = root.dataset.voiceEnabled === "true";
  const assistantName = root.dataset.assistantName || "CA-Tech AI";
  const storageKey = "technest-ai-conversation-id";
  
  const state = {
    conversationId: localStorage.getItem(storageKey) || "",
    loaded: false,
    recording: false,
    recognition: null,
    isStreaming: false,
    isSpeaking: false,
    isMuted: false
  };

  function stopTTS() {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      state.isSpeaking = false;
    }
  }

  function toggleMute() {
    state.isMuted = !state.isMuted;
    if (state.isMuted) {
      stopTTS();
      if (muteBtn) {
        muteBtn.querySelector("i").className = "fa-solid fa-volume-xmark";
        muteBtn.querySelector("span").textContent = "Unmute Audio";
      }
    } else {
      if (muteBtn) {
        muteBtn.querySelector("i").className = "fa-solid fa-volume-high";
        muteBtn.querySelector("span").textContent = "Mute Audio";
      }
    }
  }

  function playTTS(text, language) {
    if (!voiceEnabled || !window.speechSynthesis || state.isMuted) return;
    stopTTS();
    if (!text) return;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = (language === "ur" || language === "roman_ur" || language === "mixed") ? "ur-PK" : "en-US";
    
    state.isSpeaking = true;
    
    utterance.onend = () => { state.isSpeaking = false; };
    utterance.onerror = () => { state.isSpeaking = false; };
    
    window.speechSynthesis.speak(utterance);
  }

  // Enhanced Markdown Parser for natural AI chat bubbles
  function parseMarkdown(text = "") {
    let raw = String(text).trim();
    if (!raw) return "";

    let html = raw
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") // sanitize
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>") // bold
      .replace(/\*(.*?)\*/g, "<em>$1</em>") // italic
      .replace(/`([^`]+)`/g, "<code>$1</code>") // inline code
      .replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>"); // code blocks

    // Process bullet points and paragraphs
    let lines = html.split("\n");
    let result = [];
    let inList = false;

    lines.forEach(line => {
      let trimmed = line.trim();
      if (trimmed.startsWith("• ") || trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
        if (!inList) {
          result.push("<ul>");
          inList = true;
        }
        result.push(`<li>${trimmed.substring(2)}</li>`);
      } else {
        if (inList) {
          result.push("</ul>");
          inList = false;
        }
        if (trimmed) {
          result.push(`<p>${trimmed}</p>`);
        }
      }
    });

    if (inList) {
      result.push("</ul>");
    }

    return `<div class="ai-prose">${result.join("")}</div>`;
  }

  function csrfToken() {
    const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  }

  function setTyping(visible) {
    if (typingEl) typingEl.hidden = !visible;
    if (visible) scrollToBottom();
  }

  function scrollToBottom() {
    requestAnimationFrame(() => {
      messagesEl.scrollTop = messagesEl.scrollHeight;
    });
  }

  function clearMessages() {
    messagesEl.innerHTML = "";
  }

  function formatTime(value) {
    if (!value) return "";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "";
    return new Intl.DateTimeFormat(undefined, { hour: "numeric", minute: "2-digit" }).format(date);
  }

  function formatStatus(value, sender) {
    if (!value) return sender === "assistant" ? "Delivered" : "Sent";
    return String(value).replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
  }

  function createMessageNode(sender, text, products, actions, createdAt, status) {
    const wrapper = document.createElement("article");
    wrapper.className = `ai-message ai-message--${sender}`;

    const avatar = document.createElement("span");
    avatar.className = `ai-avatar ${sender === "assistant" ? "ai-avatar--assistant" : ""}`;
    avatar.innerHTML = sender === "assistant" 
      ? '<i class="fa-solid fa-sparkles" aria-hidden="true"></i>' 
      : '<i class="fa-solid fa-user" aria-hidden="true"></i>';

    const contentWrapper = document.createElement("div");
    contentWrapper.className = "ai-message__content-wrapper";

    const bubble = document.createElement("div");
    bubble.className = "ai-message__bubble";
    
    contentWrapper.appendChild(bubble);

    const productContainer = document.createElement("div");
    if (Array.isArray(products) && products.length) {
      productContainer.className = "ai-message__products";
      products.slice(0, 4).forEach((product) => {
        const chip = document.createElement("a");
        chip.className = "ai-product-chip";
        chip.href = product.url;
        const image = document.createElement("img");
        image.src = product.image || "";
        const textWrapper = document.createElement("span");
        const title = document.createElement("strong");
        title.textContent = product.name || "";
        const price = document.createElement("span");
        price.textContent = product.price_label || "";
        textWrapper.appendChild(title);
        textWrapper.appendChild(price);
        chip.appendChild(image);
        chip.appendChild(textWrapper);
        productContainer.appendChild(chip);
      });
    }

    const actionContainer = document.createElement("div");
    if (Array.isArray(actions) && actions.length) {
      actionContainer.className = "ai-message__actions";
      actions.slice(0, 4).forEach((action) => {
        if (!action || !action.url || !action.label) return;
        const link = document.createElement("a");
        link.className = action.type === "navigate" ? "ghost-btn compact" : "primary-btn compact";
        link.href = action.url;
        link.textContent = action.label;
        actionContainer.appendChild(link);
      });
    }

    const meta = document.createElement("div");
    meta.className = "ai-message__meta";
    meta.innerHTML = `
      <span class="ai-timestamp">${formatTime(createdAt || new Date().toISOString())}</span>
      <span class="ai-status"><i class="fa-solid fa-circle-check"></i> ${formatStatus(status, sender)}</span>
    `;
    
    contentWrapper.appendChild(meta);
    wrapper.appendChild(avatar);
    wrapper.appendChild(contentWrapper);

    return { wrapper, bubble, productContainer, actionContainer };
  }

  async function streamText(element, htmlContent, productContainer, actionContainer, wrapper) {
    state.isStreaming = true;
    
    // Instead of complex streaming which can break HTML structure, 
    // we instantly render but animate opacity for a smooth fade-in reveal like Claude.
    element.innerHTML = htmlContent; 
    element.style.opacity = 0;
    element.style.animation = "aiMessageIn 0.4s ease forwards";
    
    if (productContainer.childNodes.length > 0) {
      wrapper.appendChild(productContainer);
    }
    if (actionContainer.childNodes.length > 0) {
      wrapper.appendChild(actionContainer);
    }
    
    scrollToBottom();
    state.isStreaming = false;
  }

  function appendMessage(message, stream = false) {
    const empty = root.querySelector("[data-assistant-empty]");
    if (empty) empty.remove();
    
    const { wrapper, bubble, productContainer, actionContainer } = createMessageNode(
      message.sender,
      message.content,
      message.products,
      message.actions,
      message.created_at,
      message.status
    );
    
    messagesEl.appendChild(wrapper);
    
    if (stream && message.sender === "assistant") {
      streamText(bubble, parseMarkdown(message.content), productContainer, actionContainer, wrapper);
    } else {
      bubble.innerHTML = parseMarkdown(message.content);
      if (productContainer.childNodes.length > 0) {
        wrapper.appendChild(productContainer);
      }
      if (actionContainer.childNodes.length > 0) {
        wrapper.appendChild(actionContainer);
      }
    }
    
    scrollToBottom();
  }

  function renderConversation(payload) {
    state.loaded = true;
    if (payload.conversation_id) {
      state.conversationId = String(payload.conversation_id);
      localStorage.setItem(storageKey, state.conversationId);
    }

    clearMessages();
    const messages = Array.isArray(payload.messages) ? payload.messages : [];
    if (!messages.length) {
      const empty = document.createElement("div");
      empty.className = "ai-assistant__empty";
      empty.dataset.assistantEmpty = "true";
      empty.innerHTML = `
        <span class="ai-avatar ai-avatar--assistant large"><i class="fa-solid fa-sparkles" aria-hidden="true"></i></span>
        <strong>${assistantName}</strong>
        <p>${payload.welcome_message || welcomeMessage}</p>
      `;
      messagesEl.appendChild(empty);
      return;
    }

    messages.forEach((message) => appendMessage(message, false));
  }

  async function loadState() {
    if (!stateUrl) return;
    try {
      const url = new URL(stateUrl, window.location.origin);
      if (state.conversationId) url.searchParams.set("conversation_id", state.conversationId);
      const response = await fetch(url.toString(), {
        headers: { "X-Requested-With": "XMLHttpRequest" }
      });
      if (response.ok) renderConversation(await response.json());
    } catch (e) {
      // ignore
    }
  }

  function openPanel() {
    root.classList.add("is-open");
    root.classList.remove("is-minimized");
    panel.hidden = false;
    panel.setAttribute("aria-hidden", "false");
    if (!state.loaded) loadState();
    setTimeout(() => input?.focus(), 100);
  }

  function closePanel() {
    root.classList.remove("is-open", "is-minimized");
    panel.hidden = true;
    panel.setAttribute("aria-hidden", "true");
  }

  async function sendMessage(text) {
    if (state.isStreaming) return;
    const value = text.trim();
    if (!value || !apiUrl) return;

    appendMessage({ sender: "user", content: value });
    setTyping(true);
    
    input.value = "";
    input.style.height = "auto"; // reset size
    input.focus();

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken(),
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({
          conversation_id: state.conversationId || null,
          message: value
        }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error("Failed");
      
      if (payload.conversation_id) {
        state.conversationId = String(payload.conversation_id);
        localStorage.setItem(storageKey, state.conversationId);
      }
      
      setTyping(false);
      
      let msg = null;
      if (payload.conversation && payload.conversation.messages) {
        msg = payload.conversation.messages[payload.conversation.messages.length - 1];
        if (msg) msg.products = payload.assistant?.products || [];
        if (msg) msg.actions = payload.assistant?.actions || [];
      } else if (payload.assistant) {
        msg = {
          sender: "assistant",
          content: payload.assistant.content,
          products: payload.assistant.products || [],
          actions: payload.assistant.actions || []
        };
      }
      
      if (msg) {
        appendMessage(msg, true);
        if (payload.assistant && payload.assistant.voice_text) {
          playTTS(payload.assistant.voice_text, payload.assistant.language);
        }
      }
      
    } catch (error) {
      setTyping(false);
      appendMessage({ sender: "assistant", content: "Service unavailable." }, false);
    }
  }

  // Textarea auto resize
  if (input) {
    input.addEventListener("input", function() {
      this.style.height = "auto";
      this.style.height = (this.scrollHeight) + "px";
    });
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage(input.value);
      }
    });
  }

  form?.addEventListener("submit", (e) => {
    e.preventDefault();
    sendMessage(input.value);
  });

  toggle.addEventListener("click", (e) => {
    e.preventDefault();
    panel.hidden ? openPanel() : closePanel();
  });

  closeBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    closePanel();
  });

  minimizeBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    root.classList.add("is-minimized");
  });
  
  muteBtn?.addEventListener("click", toggleMute);

  clearBtn?.addEventListener("click", async () => {
    if (!apiUrl) return;
    setTyping(true);
    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken(),
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({ action: "clear", conversation_id: state.conversationId || null }),
      });
      const payload = await response.json();
      if (payload.conversation_id) localStorage.setItem(storageKey, payload.conversation_id);
      state.conversationId = payload.conversation_id;
      setTyping(false);
      clearMessages();
      appendMessage({ sender: "assistant", content: payload.assistant?.content || "Conversation cleared." }, true);
    } catch (e) {
      setTyping(false);
    }
  });
  
  historyBtn?.addEventListener("click", loadState);

  if (voiceEnabled && ("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    state.recognition = new SpeechRecognition();
    state.recognition.continuous = false;
    state.recognition.interimResults = false;
    
    state.recognition.onstart = () => {
      state.recording = true;
      if (voiceBtn) voiceBtn.classList.add("is-recording");
      if (input) input.placeholder = "Listening...";
    };
    
    state.recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      if (input) input.value = text;
      sendMessage(text);
    };
    
    state.recognition.onerror = () => {
      state.recording = false;
      if (voiceBtn) voiceBtn.classList.remove("is-recording");
      if (input) input.placeholder = "Message CA-Tech AI...";
    };
    
    state.recognition.onend = () => {
      state.recording = false;
      if (voiceBtn) voiceBtn.classList.remove("is-recording");
      if (input) input.placeholder = "Message CA-Tech AI...";
    };
    
    voiceBtn?.addEventListener("click", () => {
      if (state.recording) {
        state.recognition.stop();
      } else {
        state.recognition.start();
      }
    });
  } else if (voiceBtn) {
    voiceBtn.style.display = "none";
  }
  
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !panel.hidden) closePanel();
  });

  loadState();
})();
