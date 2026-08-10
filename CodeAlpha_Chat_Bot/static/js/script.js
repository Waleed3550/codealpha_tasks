const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const clearBtn = document.getElementById('clear-btn');
const exportBtn = document.getElementById('export-btn');
const themeToggle = document.getElementById('theme-toggle');
const micBtn = document.getElementById('mic-btn');
const charCount = document.getElementById('char-count');
const typingIndicator = document.getElementById('typing-indicator');
const micStatus = document.getElementById('mic-status');

const msgTemplate = document.getElementById('message-template');
const dateTemplate = document.getElementById('date-separator-template');
const csrfNode = document.querySelector('[name=csrfmiddlewaretoken]');
const csrfToken = csrfNode ? csrfNode.value : '';

// Icons for avatars
const botIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>`;
const userIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`;

let messages = [];

// Initialize
function init() {
    try { initTheme(); } catch (e) { console.error('Error initializing theme:', e); }
    try { loadMessages(); } catch (e) { console.error('Error loading messages:', e); }
    try { setupEventListeners(); } catch (e) { console.error('Error setting up event listeners:', e); }
    try { setupSpeechRecognition(); } catch (e) { console.error('Error setting up speech recognition:', e); }
}

function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    showToast('Theme Changed');
}

function saveMessages() {
    // Legacy function, backend handles saving automatically now.
}

async function loadMessages() {
    try {
        const res = await fetch('/get-messages/');
        const data = await res.json();
        if (data.messages) {
            messages = data.messages;
            renderAllMessages();
        }
    } catch(e) {
        console.error('Error loading messages from backend:', e);
        messages = [];
    }
    
    try {
        const res2 = await fetch('/chat-history/');
        const data2 = await res2.json();
        if(data2.conversations) {
            updateRecentChats(data2.conversations);
        }
    } catch(e) {
        console.error('Error loading recent chats:', e);
    }
}

async function searchChats(query) {
    try {
        const res = await fetch(`/search-chats/?q=${encodeURIComponent(query)}`);
        const data = await res.json();
        if(data.conversations) {
            updateRecentChats(data.conversations);
        }
    } catch(e) {
        console.error('Error searching chats:', e);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.querySelector('.search-box input');
    if (searchInput) {
        let timeout = null;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                searchChats(e.target.value);
            }, 300);
        });
    }
    
    // Override the inline onclick for both buttons
    const newChatBtns = document.querySelectorAll('.new-chat-btn');
    newChatBtns.forEach(btn => {
        btn.onclick = (e) => {
            e.preventDefault();
            startNewChat();
        };
    });
    
    const clearBtn = document.getElementById('clear-btn');
    if (clearBtn) {
        clearBtn.onclick = (e) => {
            e.preventDefault();
            deleteCurrentChat();
        };
    }
});

function updateRecentChats(conversations) {
    const navSections = document.querySelectorAll('.nav-section');
    let recentUl = null;
    navSections.forEach(sec => {
        const h3 = sec.querySelector('h3');
        if (h3 && h3.textContent.includes('Recent')) {
            recentUl = sec.querySelector('.nav-list');
        }
    });
    
    if (recentUl) {
        recentUl.innerHTML = '';
        conversations.forEach(conv => {
            const li = document.createElement('li');
            li.style.cursor = 'pointer';
            li.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg> ${conv.title}`;
            li.onclick = () => loadChat(conv.id);
            recentUl.appendChild(li);
        });
    }
}

async function loadChat(convId) {
    try {
        const res = await fetch(`/conversation/${convId}/`);
        const data = await res.json();
        if (data.messages) {
            messages = data.messages;
            renderAllMessages();
            const sidebar = document.getElementById('app-sidebar');
            if(sidebar && window.innerWidth <= 768) {
                sidebar.classList.remove('mobile-open');
            }
        }
    } catch(e) {
        console.error('Error switching chat:', e);
    }
}

function renderAllMessages() {
    if (!chatMessages) return;
    
    Array.from(chatMessages.children).forEach(child => {
        if (child.id !== 'typing-indicator') {
            child.remove();
        }
    });
    
    let lastDate = null;
    
    messages.forEach(msg => {
        const msgDate = new Date(msg.timestamp).toLocaleDateString();
        if (msgDate !== lastDate) {
            appendDateSeparator(msgDate);
            lastDate = msgDate;
        }
        appendMessageElement(msg);
    });
    scrollToBottom();
}

function appendDateSeparator(dateStr) {
    if (!dateTemplate || !chatMessages || !typingIndicator) return;
    const clone = dateTemplate.content.cloneNode(true);
    const dateTextElem = clone.querySelector('.date-text');
    if (dateTextElem) dateTextElem.textContent = dateStr;
    chatMessages.insertBefore(clone, typingIndicator);
}

function addMessageToState(text, sender) {
    const msg = {
        id: Date.now().toString() + Math.random().toString(36).substring(2, 9),
        text: text,
        sender: sender,
        timestamp: Date.now()
    };
    messages.push(msg);
    saveMessages();
    
    const msgDate = new Date(msg.timestamp).toLocaleDateString();
    const lastMsg = messages[messages.length - 2];
    const lastDate = lastMsg ? new Date(lastMsg.timestamp).toLocaleDateString() : null;
    
    if (msgDate !== lastDate) {
        appendDateSeparator(msgDate);
    }
    
    appendMessageElement(msg);
    scrollToBottom();
}

function appendMessageElement(msg) {
    const clone = msgTemplate.content.cloneNode(true);
    const group = clone.querySelector('.message-group');
    const avatarWrapper = clone.querySelector('.avatar-wrapper');
    const content = clone.querySelector('.message-content');
    const timeSpan = clone.querySelector('.time');
    const copyBtn = clone.querySelector('.copy-btn');
    const deleteBtn = clone.querySelector('.delete-btn');
    
    if (group) {
        group.classList.add(msg.sender);
        group.dataset.id = msg.id;
    }
    
    if (avatarWrapper) {
        avatarWrapper.classList.add(msg.sender === 'bot' ? 'bot-avatar' : 'user-avatar');
        avatarWrapper.innerHTML = msg.sender === 'bot' ? botIcon : userIcon;
    }
    
    // Basic Markdown Parser (Pure JS)
    let safeText = msg.text.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    safeText = safeText.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>"); // Bold
    safeText = safeText.replace(/\*(.*?)\*/g, "<em>$1</em>"); // Italic
    safeText = safeText.replace(/`([^`]+)`/g, "<code>$1</code>"); // Inline code
    safeText = safeText.replace(/\[(.*?)\]\((.*?)\)/g, "<a href='$2' target='_blank'>$1</a>"); // Links
    safeText = safeText.replace(/\n/g, "<br>"); // Newlines
    
    if (content) content.innerHTML = safeText;
    if (timeSpan) timeSpan.textContent = new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    // Handle Confidence Badge
    const confidenceBadge = clone.querySelector('.confidence-badge');
    if (confidenceBadge) {
        if (msg.sender === 'bot') {
            confidenceBadge.style.display = 'inline-block';
            // Randomize confidence for demo purposes (High, Medium, Low)
            const rand = Math.random();
            if (rand > 0.8) {
                confidenceBadge.textContent = 'Low';
                confidenceBadge.style.color = '#ef4444';
            } else if (rand > 0.5) {
                confidenceBadge.textContent = 'Medium';
                confidenceBadge.style.color = '#f59e0b';
            } else {
                confidenceBadge.textContent = 'High';
                confidenceBadge.style.color = '#10b981';
            }
        } else {
            confidenceBadge.style.display = 'none';
        }
    }
    
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(msg.text);
            showToast('Copied to clipboard');
            copyBtn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" width="14" height="14"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
            setTimeout(() => {
                copyBtn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
            }, 2000);
        });
    }
    
    // Handle Delete & Regenerate
    if (deleteBtn) {
        deleteBtn.addEventListener('click', () => {
            const idx = messages.indexOf(msg);
            if (idx > -1) messages.splice(idx, 1);
            saveMessages();
            const containerGroup = deleteBtn.closest('.message-group');
            if(containerGroup) containerGroup.remove();
            showToast('Message Deleted');
        });
    }

    const regenBtn = clone.querySelector('.regenerate-btn');
    if (regenBtn) {
        if (msg.sender === 'bot') {
            regenBtn.addEventListener('click', () => {
                const idx = messages.indexOf(msg);
                let prevUser = "Hello";
                if (idx > 0 && messages[idx - 1].sender === 'user') {
                    prevUser = messages[idx - 1].text;
                }
                if (idx > -1) messages.splice(idx, 1);
                saveMessages();
                const containerGroup = regenBtn.closest('.message-group');
                if(containerGroup) containerGroup.remove();
                // Show typing indicator & send
                document.getElementById('typing-indicator').style.display = 'flex';
                document.getElementById('user-input').value = prevUser;
                handleSend();
                showToast('Regenerating Response');
            });
        } else {
            regenBtn.style.display = 'none';
        }
    }

    // Add Suggestion Chips for Bot
    if (msg.sender === 'bot') {
        const chips = document.createElement('div');
        chips.className = 'suggestion-chips';
        const suggestions = ["Tell me more", "Give an example", "Why is that?"];
        suggestions.forEach(text => {
            const btn = document.createElement('button');
            btn.className = 'chip';
            btn.textContent = text;
            btn.addEventListener('click', () => {
                document.getElementById('user-input').value = text;
                handleSend();
            });
            chips.appendChild(btn);
        });
        const msgBody = clone.querySelector('.message-body');
        if(msgBody) msgBody.appendChild(chips);
    }
    
    if (chatMessages && typingIndicator) chatMessages.insertBefore(group, typingIndicator);
}

function scrollToBottom() {
    if (chatMessages) chatMessages.scrollTo({ top: chatMessages.scrollHeight, behavior: 'smooth' });
}

async function handleSend() {
    const text = userInput.value.trim();
    if (!text) return;

    userInput.value = '';
    updateInputState();
    
    addMessageToState(text, 'user');
    
    typingIndicator.style.display = 'block';
    scrollToBottom();

    try {
        const response = await fetch('/get-response/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ message: text })
        });
        
        if (!response.ok) throw new Error('Server error');
        const data = await response.json();
        
        typingIndicator.style.display = 'none';
        addMessageToState(data.response, 'bot');
    } catch (error) {
        typingIndicator.style.display = 'none';
        addMessageToState('Sorry, there was an error connecting to the server.', 'bot');
    }
}

function updateInputState() {
    if (!userInput) return;
    const len = userInput.value.length;
    if (charCount) charCount.textContent = len;
    
    userInput.style.height = 'auto';
    userInput.style.height = (userInput.scrollHeight) + 'px';
    
    if (sendBtn) {
        if (len > 0 && len <= 2000) {
            sendBtn.disabled = false;
        } else {
            sendBtn.disabled = true;
        }
    }
}

window.clearChat = function() {
    // This overrides the inline HTML onclick to prevent conflicts.
    // The actual behavior is handled by DOMContentLoaded event listeners.
};

async function startNewChat() {
    try {
        await fetch('/new-chat/', {method: 'POST', headers: {'X-CSRFToken': csrfToken}});
    } catch(e) {
        console.error('Error starting new chat:', e);
    }
    messages = [];
    renderAllMessages();
    showToast('New Chat Started');
    loadMessages(); // Refresh sidebar
}

async function deleteCurrentChat() {
    if(confirm('Are you sure you want to delete this conversation?')) {
        try {
            // Find current active conversation id from the active list if we had one.
            // Since we don't store conv_id in JS, we can rely on a quick GET or just hit a specific endpoint.
            // The cleanest way is to use the server's session via a dedicated clear endpoint.
            // But since the user requested DELETE /conversation/<id>/ we must pass ID.
            // Let's first get the recent chat from session. 
            // Workaround: We'll just fetch a new chat which clears session, then refresh. 
            // Or better, let's just use the server's active session.
            const curr = await fetch('/chat-history/').then(r => r.json());
            if(curr.conversations && curr.conversations.length > 0) {
                await fetch(`/conversation/${curr.conversations[0].id}/`, {
                    method: 'DELETE',
                    headers: {'X-CSRFToken': csrfToken}
                });
            }
        } catch(e) {
            console.error('Error deleting chat:', e);
        }
        messages = [];
        renderAllMessages();
        showToast('Chat Deleted');
        loadMessages(); // Refresh sidebar
    }
}

function exportChat() {
    let txt = "Nexus AI - Conversation Export\n\n";
    messages.forEach(m => {
        const date = new Date(m.timestamp).toLocaleString();
        const sender = m.sender === 'bot' ? 'Nexus AI' : 'You';
        txt += `[${date}] ${sender}:\n${m.text}\n\n`;
    });
    
    const blob = new Blob([txt], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `nexus_chat_${new Date().getTime()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Chat Exported');
}

// Speech Recognition
let recognition;
let isListening = false;

function setupSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        
        recognition.onstart = () => {
            isListening = true;
            if(micBtn) micBtn.classList.add('listening');
            if(micStatus) micStatus.style.display = 'block';
            showToast('Voice Activated');
        };
        
        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }
            
            if (finalTranscript && userInput) {
                const currentVal = userInput.value;
                userInput.value = currentVal + (currentVal ? ' ' : '') + finalTranscript;
                updateInputState();
            }
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error', event.error);
            stopListening();
            if(event.error === 'not-allowed') {
                alert('Microphone permission denied.');
            }
        };
        
        recognition.onend = () => {
            stopListening();
        };
    }
}

function stopListening() {
    isListening = false;
    if(micBtn) micBtn.classList.remove('listening');
    if(micStatus) micStatus.style.display = 'none';
    if(recognition) recognition.stop();
    showToast('Voice Stopped');
}

function toggleListening() {
    if (!recognition) {
        alert('Speech recognition is not supported in this browser.');
        return;
    }
    
    if (isListening) {
        stopListening();
    } else {
        userInput.value = '';
        recognition.start();
    }
}

function setupEventListeners() {
    if (themeToggle) themeToggle.addEventListener('click', toggleTheme);
    if (sendBtn) sendBtn.addEventListener('click', handleSend);
    if (clearBtn) clearBtn.addEventListener('click', clearChat);
    if (exportBtn) exportBtn.addEventListener('click', exportChat);
    if (micBtn) micBtn.addEventListener('click', toggleListening);
    
    if (userInput) {
        userInput.addEventListener('input', updateInputState);
        userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if(!sendBtn.disabled) handleSend();
            }
        });
    }
}

// Splash Screen Logic
function initSplashScreen() {
    const revealApp = () => {
        const appLayout = document.querySelector('.app-layout');
        if (appLayout) {
            appLayout.style.display = 'flex';
            appLayout.style.visibility = 'visible';
            appLayout.style.opacity = '1';
            appLayout.style.pointerEvents = 'auto';
        }
    };

    // Failsafe backup to guarantee removal
    const maxWait = setTimeout(() => {
        const splash = document.getElementById('splash-screen');
        if (splash) splash.remove();
        revealApp();
    }, 3000);

    setTimeout(() => {
        const splash = document.getElementById('splash-screen');
        if (splash) {
            splash.style.opacity = '0';
            setTimeout(() => {
                splash.style.visibility = 'hidden';
                splash.remove();
                clearTimeout(maxWait);
                revealApp();
            }, 500);
        }
    }, 2500);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSplashScreen);
} else {
    initSplashScreen();
}

// Mouse Glow Logic
try {
    document.addEventListener('mousemove', (e) => {
        const mouseGlow = document.getElementById('mouse-glow');
        if (mouseGlow) {
            mouseGlow.style.left = e.clientX + 'px';
            mouseGlow.style.top = e.clientY + 'px';
        }
    });
} catch (e) { console.error('Error initializing mouse glow:', e); }

// Ripple Effect Logic
function createRipple(event) {
    const button = event.currentTarget;
    
    // Ensure button is position relative to contain the ripple
    if (getComputedStyle(button).position === 'static') {
        button.style.position = 'relative';
    }
    button.style.overflow = 'hidden';

    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;

    const rect = button.getBoundingClientRect();
    
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - rect.left - radius}px`;
    circle.style.top = `${event.clientY - rect.top - radius}px`;
    circle.classList.add('ripple');

    const ripple = button.getElementsByClassName('ripple')[0];
    if (ripple) {
        ripple.remove();
    }

    button.appendChild(circle);
    setTimeout(() => circle.remove(), 600);
}

function showToast(message) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = 'toast';
    
    // Checkmark icon for toast
    const icon = `<svg viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" width="18" height="18"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
    toast.innerHTML = `${icon} <span>${message}</span>`;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}

function attachRipples() {
    const buttons = document.querySelectorAll('.action-btn, .icon-btn, .suggestion-card, .new-chat-btn, .footer-btn');
    buttons.forEach(btn => {
        btn.addEventListener('mousedown', createRipple);
    });
}

// Current Time Updater
function updateCurrentTime() {
    const timeElem = document.getElementById('current-time');
    if(timeElem) {
        const now = new Date();
        timeElem.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
}
setInterval(updateCurrentTime, 60000);

// Advanced Modals & Settings Logic
const cmdPalette = document.getElementById('cmd-palette');
const shortcutsDialog = document.getElementById('shortcuts-dialog');
const settingsDrawer = document.getElementById('settings-drawer');
const cmdInput = document.getElementById('cmd-input');
const cmdList = document.getElementById('cmd-list');

function openModal(modal) {
    if(!modal) return;
    modal.classList.remove('hide');
    if(modal === cmdPalette) {
        cmdInput.value = '';
        cmdInput.focus();
        filterCommands('');
    }
}

function closeModal(modal) {
    if(!modal) return;
    modal.classList.add('hide');
}

function filterCommands(query) {
    const items = cmdList.querySelectorAll('li');
    query = query.toLowerCase();
    let firstVisible = true;
    items.forEach(item => {
        item.classList.remove('active');
        if(item.textContent.toLowerCase().includes(query)) {
            item.style.display = 'flex';
            if(firstVisible) {
                item.classList.add('active');
                firstVisible = false;
            }
        } else {
            item.style.display = 'none';
        }
    });
}

function executeCommand(action) {
    closeModal(cmdPalette);
    switch(action) {
        case 'new-chat': clearChat(); break;
        case 'clear-chat': clearChat(); break;
        case 'toggle-theme': toggleTheme(); break;
        case 'export-chat': document.getElementById('export-btn').click(); break;
        case 'copy-chat': 
            const chatText = messages.map(m => `${m.sender.toUpperCase()}: ${m.text}`).join('\n\n');
            navigator.clipboard.writeText(chatText);
            showToast('Chat Copied to Clipboard');
            break;
        case 'open-settings': openModal(settingsDrawer); break;
        case 'focus-input': userInput.focus(); break;
    }
}

// Global Keyboard Shortcuts
document.addEventListener('keydown', (e) => {
    // Check if user is typing in the main chat input
    const isTyping = document.activeElement === userInput;
    
    if (e.key === 'Escape') {
        closeModal(cmdPalette);
        closeModal(shortcutsDialog);
        closeModal(settingsDrawer);
        return;
    }
    
    if (e.ctrlKey && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        openModal(cmdPalette);
    } else if (e.key === '?' && !isTyping && document.activeElement !== cmdInput) {
        e.preventDefault();
        openModal(shortcutsDialog);
    } else if (e.ctrlKey && e.key.toLowerCase() === 'n') {
        e.preventDefault(); clearChat();
    } else if (e.ctrlKey && e.key.toLowerCase() === 'l') {
        e.preventDefault(); clearChat();
    } else if (e.ctrlKey && e.key.toLowerCase() === 'd') {
        e.preventDefault(); toggleTheme();
    } else if (e.ctrlKey && e.key === ',') {
        e.preventDefault(); openModal(settingsDrawer);
    } else if (e.key === '/' && !isTyping && document.activeElement !== cmdInput) {
        e.preventDefault(); userInput.focus();
    }
});

// Command Palette Interactions
try {
    if(cmdInput) {
        cmdInput.addEventListener('input', (e) => filterCommands(e.target.value));
        cmdInput.addEventListener('keydown', (e) => {
            const items = Array.from(cmdList.querySelectorAll('li')).filter(i => i.style.display !== 'none');
            const activeIdx = items.findIndex(i => i.classList.contains('active'));
            
            if(e.key === 'ArrowDown') {
                e.preventDefault();
                if(activeIdx < items.length - 1) {
                    items[activeIdx]?.classList.remove('active');
                    items[activeIdx + 1].classList.add('active');
                }
            } else if(e.key === 'ArrowUp') {
                e.preventDefault();
                if(activeIdx > 0) {
                    items[activeIdx]?.classList.remove('active');
                    items[activeIdx - 1].classList.add('active');
                }
            } else if(e.key === 'Enter') {
                e.preventDefault();
                if(activeIdx !== -1) executeCommand(items[activeIdx].dataset.action);
            }
        });
    }
    if(cmdList) {
        cmdList.addEventListener('click', (e) => {
            const li = e.target.closest('li');
            if(li) executeCommand(li.dataset.action);
        });
    }
} catch(e) { console.error('Error initializing command palette:', e); }

// Modal Close Triggers
try {
    document.querySelectorAll('.modal-overlay, .drawer-overlay').forEach(overlay => {
        overlay.addEventListener('mousedown', (e) => {
            if(e.target === overlay) closeModal(overlay);
        });
    });
    document.querySelectorAll('.close-modal-btn, .close-drawer-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            closeModal(e.target.closest('.modal-overlay, .drawer-overlay'));
        });
    });
} catch(e) { console.error('Error initializing modal triggers:', e); }
// Override alert for settings
window.alert = function(msg) {
    if(msg.includes('Settings')) {
        openModal(settingsDrawer);
    } else {
        showToast(msg);
    }
}

// Settings Drawer Logic (Dynamic Styling)
try {
    document.querySelectorAll('.color-dot').forEach(dot => {
        dot.addEventListener('click', (e) => {
            document.querySelectorAll('.color-dot').forEach(d => d.classList.remove('active'));
            dot.classList.add('active');
            const colorMap = {
                'blue': '#3b82f6',
                'green': '#10b981',
                'purple': '#8b5cf6',
                'orange': '#f59e0b'
            };
            document.documentElement.style.setProperty('--primary-color', colorMap[dot.dataset.color]);
            document.documentElement.style.setProperty('--primary-gradient', `linear-gradient(135deg, ${colorMap[dot.dataset.color]} 0%, #4338ca 100%)`);
            showToast('Accent Color Updated');
        });
    });

    const fontSelect = document.getElementById('setting-font');
    if(fontSelect) {
        fontSelect.addEventListener('change', (e) => {
            const sizes = { 'small': '14px', 'normal': '16px', 'large': '18px' };
            document.body.style.fontSize = sizes[e.target.value];
            showToast('Font Size Updated');
        });
    }

    const themeSelect = document.getElementById('setting-theme');
    if(themeSelect) {
        themeSelect.addEventListener('change', (e) => {
            document.documentElement.setAttribute('data-theme', e.target.value);
            localStorage.setItem('theme', e.target.value);
            showToast('Theme Updated');
        });
    }
} catch(e) { console.error('Error initializing settings drawer:', e); }

// Boot
try { attachRipples(); } catch (e) { console.error('Error attaching ripples:', e); }
try { updateCurrentTime(); } catch (e) { console.error('Error updating time:', e); }
try { init(); } catch (e) { console.error('Error during init:', e); }

