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
  const hasGsap = Boolean(window.gsap);
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const apiUrl = root.dataset.apiUrl;
  const stateUrl = root.dataset.stateUrl;
  const welcomeMessage = root.dataset.welcomeMessage || "Hello. How can I assist you today?";
  const voiceEnabled = root.dataset.voiceEnabled === "true";
  const assistantName = root.dataset.assistantName || "TechNest AI";
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

  function animatePanel(opening) {
    if (!hasGsap || prefersReducedMotion || !panel) return;
    if (opening) {
      window.gsap.fromTo(
        panel,
        { opacity: 0, y: 24, scale: 0.96, transformOrigin: "100% 100%" },
        { opacity: 1, y: 0, scale: 1, duration: 0.38, ease: "power3.out", clearProps: "transform" }
      );
    } else {
      window.gsap.to(panel, {
        opacity: 0,
        y: 18,
        scale: 0.96,
        duration: 0.24,
        ease: "power2.in",
        onComplete: () => {
          panel.hidden = true;
        },
      });
    }
  }

  function animateMessage(wrapper, bubble, productContainer) {
    if (!hasGsap || prefersReducedMotion) return;
    const productChildren = productContainer?.children?.length ? Array.from(productContainer.children) : [];
    window.gsap.fromTo(
      wrapper,
      { opacity: 0, y: 14, scale: 0.985 },
      { opacity: 1, y: 0, scale: 1, duration: 0.36, ease: "power3.out" }
    );
    window.gsap.fromTo(
      bubble,
      { opacity: 0, y: 10, filter: "blur(4px)" },
      { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.32, delay: 0.04, ease: "power2.out" }
    );
    if (productChildren.length) {
      window.gsap.fromTo(
        productChildren,
        { opacity: 0, y: 12, scale: 0.98 },
        { opacity: 1, y: 0, scale: 1, duration: 0.3, stagger: 0.05, delay: 0.08, ease: "power2.out" }
      );
    }
  }

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
    if (hasGsap && !prefersReducedMotion && muteBtn) {
      window.gsap.fromTo(muteBtn, { scale: 1 }, { scale: 1.06, duration: 0.16, yoyo: true, repeat: 1, ease: "power2.out" });
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

  // Simple Markdown Parser
  function parseMarkdown(text) {
    let html = text
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") // sanitize
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>") // bold
      .replace(/\*(.*?)\*/g, "<em>$1</em>") // italic
      .replace(/`([^`]+)`/g, "<code>$1</code>") // inline code
      .replace(/```([\s\S]*?)```/g, "<pre><code>$1</code></pre>") // code blocks
      .replace(/\n/g, "<br>"); // newlines
    
    // Quick lists handling
    html = html.replace(/(?:^|<br>)- (.*?)(?=<br>|$)/g, "<li>$1</li>");
    html = html.replace(/(<li>.*<\/li>)/g, "<ul>$1</ul>");
    html = html.replace(/<\/ul><ul>/g, ""); // merge lists
    
    return `<div class="ai-prose">${html}</div>`;
  }

  function csrfToken() {
    const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  }

  function setTyping(visible) {
    if (typingEl) {
      typingEl.hidden = !visible;
      if (visible && hasGsap && !prefersReducedMotion) {
        window.gsap.fromTo(typingEl, { opacity: 0, y: 4 }, { opacity: 1, y: 0, duration: 0.2, ease: "power2.out" });
      }
    }
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

  function createMessageNode(sender, text, products, createdAt, status) {
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

    const meta = document.createElement("div");
    meta.className = "ai-message__meta";
    meta.innerHTML = `
      <span class="ai-timestamp">${formatTime(createdAt || new Date().toISOString())}</span>
      <span class="ai-status"><i class="fa-solid fa-circle-check"></i> ${formatStatus(status, sender)}</span>
    `;
    
    contentWrapper.appendChild(meta);
    wrapper.appendChild(avatar);
    wrapper.appendChild(contentWrapper);

    return { wrapper, bubble, productContainer };
  }

  async function streamText(element, htmlContent, productContainer, wrapper) {
    state.isStreaming = true;
    
    // Instead of complex streaming which can break HTML structure, 
    // we instantly render but animate opacity for a smooth fade-in reveal like Claude.
    element.innerHTML = htmlContent; 
    element.style.opacity = 0;
    element.style.animation = "aiMessageIn 0.4s ease forwards";
    
    if (productContainer.childNodes.length > 0) {
      wrapper.appendChild(productContainer);
    }

    animateMessage(wrapper, element, productContainer);
    
    scrollToBottom();
    state.isStreaming = false;
  }

  function appendMessage(message, stream = false) {
    const empty = root.querySelector("[data-assistant-empty]");
    if (empty) empty.remove();
    
    const { wrapper, bubble, productContainer } = createMessageNode(
      message.sender,
      message.content,
      message.products,
      message.created_at,
      message.status
    );
    
    messagesEl.appendChild(wrapper);
    
    if (stream && message.sender === "assistant") {
      streamText(bubble, parseMarkdown(message.content), productContainer, wrapper);
    } else {
      bubble.innerHTML = parseMarkdown(message.content);
      if (productContainer.childNodes.length > 0) {
        wrapper.appendChild(productContainer);
      }
      animateMessage(wrapper, bubble, productContainer);
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
    animatePanel(true);
    setTimeout(() => input?.focus(), 100);
  }

  function closePanel() {
    root.classList.remove("is-open", "is-minimized");
    if (hasGsap && !prefersReducedMotion) {
      animatePanel(false);
    } else {
      panel.hidden = true;
    }
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
      } else if (payload.assistant) {
        msg = {
          sender: "assistant",
          content: payload.assistant.content,
          products: payload.assistant.products || []
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

  toggle.addEventListener("click", () => {
    panel.hidden ? openPanel() : closePanel();
  });

  closeBtn?.addEventListener("click", closePanel);
  minimizeBtn?.addEventListener("click", () => {
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
      appendMessage({ sender: "assistant", content: payload.assistant.content }, true);
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
      if (hasGsap && !prefersReducedMotion && voiceBtn) {
        window.gsap.to(voiceBtn, { scale: 1.12, boxShadow: "0 0 0 8px rgba(239,68,68,.08)", duration: 0.25, ease: "power2.out" });
      }
    };
    
    state.recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      if (input) input.value = text;
      sendMessage(text);
    };
    
    state.recognition.onerror = () => {
      state.recording = false;
      if (voiceBtn) voiceBtn.classList.remove("is-recording");
      if (input) input.placeholder = "Message TechNest AI...";
    };
    
    state.recognition.onend = () => {
      state.recording = false;
      if (voiceBtn) voiceBtn.classList.remove("is-recording");
      if (input) input.placeholder = "Message TechNest AI...";
      if (hasGsap && !prefersReducedMotion && voiceBtn) {
        window.gsap.to(voiceBtn, { scale: 1, boxShadow: "", duration: 0.3, ease: "power2.out" });
      }
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
