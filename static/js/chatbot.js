/**
 * ASK GEMINI FLOATING CHATBOT WIDGET SCRIPT
 * Enhanced with interactive prompt chips, bouncing typing indicator, and animated message transitions.
 */

document.addEventListener('DOMContentLoaded', () => {
    const launcher = document.getElementById('chatbot-launcher');
    const chatWindow = document.getElementById('chatbot-window');
    const closeBtn = document.getElementById('close-chatbot');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatBody = document.getElementById('chat-body');
    const chipsContainer = document.getElementById('chat-quick-chips');

    if (!launcher || !chatWindow) return;

    // Toggle Chat Visibility with smooth animation class
    launcher.addEventListener('click', () => {
        const isHidden = chatWindow.classList.contains('d-none');
        if (isHidden) {
            chatWindow.classList.remove('d-none');
            chatWindow.classList.add('chat-window-open');
            setTimeout(() => chatInput.focus(), 200);
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

    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const userMsg = chatInput.value.trim();
            if (!userMsg) return;

            // Append User Message
            appendMessage(userMsg, 'user');
            chatInput.value = '';

            // Show Animated Typing Indicator
            const typingMsg = appendTypingIndicator();

            try {
                const response = await fetch('/api/chatbot', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: userMsg })
                });
                const data = await response.json();

                typingMsg.remove();
                appendMessage(data.reply || "I am here to assist with disaster management and safety guidance.", 'bot');
            } catch (err) {
                typingMsg.remove();
                appendMessage("Sorry, Ask Gemini service is currently unreachable. Please verify your network or try again.", 'bot');
            }
        });
    }

    function appendTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-msg chat-msg-bot typing-indicator-msg';
        typingDiv.innerHTML = `
            <div class="typing-dots">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </div>
            <span class="small text-muted ms-2 fst-italic">Ask Gemini is thinking...</span>
        `;
        chatBody.appendChild(typingDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
        return typingDiv;
    }

    function appendMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-msg ${sender === 'user' ? 'chat-msg-user' : 'chat-msg-bot'} msg-animate-in`;

        // Markdown-style links and bold parsing
        let formattedText = text.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="text-cyan fw-bold text-decoration-underline" target="_blank">$1</a>');
        formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formattedText = formattedText.replace(/\*(.*?)\*/g, '<em>$1</em>');
        formattedText = formattedText.replace(/`([^`]+)`/g, '<code class="bg-dark px-1 text-info rounded">$1</code>');
        formattedText = formattedText.replace(/\n/g, '<br>');

        msgDiv.innerHTML = formattedText;
        chatBody.appendChild(msgDiv);
        
        // Smooth scroll to bottom
        chatBody.scrollTo({
            top: chatBody.scrollHeight,
            behavior: 'smooth'
        });
        
        return msgDiv;
    }
});
