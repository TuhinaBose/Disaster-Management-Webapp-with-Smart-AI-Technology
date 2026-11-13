/**
 * AI DISASTER ASSISTANT - CLIENT-SIDE SCRIPT
 * Multi-turn conversational history, session memory, clear chat, and animated interactions.
 */

document.addEventListener('DOMContentLoaded', () => {
    const launcher = document.getElementById('chatbot-launcher');
    const chatWindow = document.getElementById('chatbot-window');
    const closeBtn = document.getElementById('close-chatbot');
    const clearBtn = document.getElementById('clear-chatbot');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatBody = document.getElementById('chat-body');
    const chipsContainer = document.getElementById('chat-quick-chips');

    if (!launcher || !chatWindow) return;

    // In-memory conversation history for multi-turn conversational context
    let conversationHistory = [];

    const INITIAL_GREETING = "✨ Hello! I am your <strong>AI Disaster Assistant</strong>. I can assist you with emergency safety rules, finding nearby relief shelters and bed capacity, survival checklists, evacuation guidelines, and first aid. How can I help you today?";

    // Toggle Chat Visibility
    launcher.addEventListener('click', () => {
        const isHidden = chatWindow.classList.contains('d-none');
        if (isHidden) {
            chatWindow.classList.remove('d-none');
            chatWindow.classList.add('chat-window-open');
            setTimeout(() => chatInput.focus(), 250);
        } else {
            chatWindow.classList.remove('chat-window-open');
            chatWindow.classList.add('d-none');
        }
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            chatWindow.classList.remove('chat-window-open');
            chatWindow.classList.add('d-none');
        });
    }

    // Clear Chat Option
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            conversationHistory = [];
            chatBody.innerHTML = `
                <div class="chat-msg chat-msg-bot msg-animate-in">
                    ${INITIAL_GREETING}
                </div>
            `;
            chatInput.focus();
        });
    }

    // Quick Action Prompt Chips Click Handler
    if (chipsContainer) {
        chipsContainer.addEventListener('click', (e) => {
            const chip = e.target.closest('.chat-chip');
            if (!chip) return;
            const query = chip.getAttribute('data-query');
            if (query) {
                chatInput.value = query;
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    }

    // Form Submit Handler
    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const userMsg = chatInput.value.trim();
            if (!userMsg) return;

            // Append User Message to UI
            appendMessage(userMsg, 'user');
            chatInput.value = '';

            // Show Typing Indicator
            const typingMsg = appendTypingIndicator();

            try {
                const response = await fetch('/api/chatbot', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: userMsg,
                        history: conversationHistory
                    })
                });

                const data = await response.json();
                typingMsg.remove();

                const botReply = data.reply || "I am here to assist with disaster management and emergency safety guidelines.";
                appendMessage(botReply, 'bot');

                // Update Session History (Limit to last 10 messages for context efficiency)
                conversationHistory.push({ role: 'user', content: userMsg });
                conversationHistory.push({ role: 'model', content: botReply });
                if (conversationHistory.length > 12) {
                    conversationHistory = conversationHistory.slice(-10);
                }

            } catch (err) {
                typingMsg.remove();
                appendMessage("I am currently experiencing network latency. Please check your connection or explore our [Shelters](/shelters) and [Safety Tips](/safety) pages.", 'bot');
            }
        });
    }

    function appendTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-msg chat-msg-bot typing-indicator-msg msg-animate-in';
        typingDiv.innerHTML = `
            <div class="typing-dots">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </div>
            <span class="small text-muted ms-2 fst-italic" style="font-size: 0.78rem;">AI Assistant is thinking...</span>
        `;
        chatBody.appendChild(typingDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
        return typingDiv;
    }

    function appendMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-msg ${sender === 'user' ? 'chat-msg-user' : 'chat-msg-bot'} msg-animate-in`;

        // Markdown-style links, bold, code, bullets formatting
        let formattedText = text.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="fw-bold" style="color: #6D28D9; text-decoration: underline;" target="_blank">$1</a>');
        formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formattedText = formattedText.replace(/\*(.*?)\*/g, '<em>$1</em>');
        formattedText = formattedText.replace(/`([^`]+)`/g, '<code class="px-1 rounded" style="background: rgba(139, 92, 246, 0.1); color: #6D28D9;">$1</code>');
        formattedText = formattedText.replace(/\n/g, '<br>');

        msgDiv.innerHTML = formattedText;
        chatBody.appendChild(msgDiv);
        
        chatBody.scrollTo({
            top: chatBody.scrollHeight,
            behavior: 'smooth'
        });
        
        return msgDiv;
    }
});
