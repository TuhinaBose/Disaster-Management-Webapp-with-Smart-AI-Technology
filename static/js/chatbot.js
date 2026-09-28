/**
 * ASK GEMINI FLOATING CHATBOT WIDGET SCRIPT
 */

document.addEventListener('DOMContentLoaded', () => {
    const launcher = document.getElementById('chatbot-launcher');
    const chatWindow = document.getElementById('chatbot-window');
    const closeBtn = document.getElementById('close-chatbot');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatBody = document.getElementById('chat-body');

    if (!launcher || !chatWindow) return;

    // Toggle Chat Visibility
    launcher.addEventListener('click', () => {
        chatWindow.classList.toggle('d-none');
        if (!chatWindow.classList.contains('d-none')) {
            chatInput.focus();
        }
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            chatWindow.classList.add('d-none');
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

            // Show Typing Indicator
            const typingMsg = appendMessage('Ask Gemini is thinking...', 'bot', true);

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
                appendMessage("Sorry, Ask Gemini service is currently unreachable. Please try again later.", 'bot');
            }
        });
    }

    function appendMessage(text, sender, isTyping = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-msg ${sender === 'user' ? 'chat-msg-user' : 'chat-msg-bot'}`;
        if (isTyping) msgDiv.classList.add('fst-italic', 'opacity-75');

        // Markdown-style links and bold parsing
        let formattedText = text.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="text-info fw-bold">$1</a>');
        formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formattedText = formattedText.replace(/\n/g, '<br>');

        msgDiv.innerHTML = formattedText;
        chatBody.appendChild(msgDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
        return msgDiv;
    }
});
