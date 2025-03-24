document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const resultContainer = document.getElementById('result-container');
    const mbtiResult = document.getElementById('mbti-result');
    
    // Connect to Socket.IO server
    const socket = io();
    
    // Initialize chat
    init();
    
    // Event Listeners
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Functions
    function init() {
        // Send empty message to get initial greeting
        socket.emit('message', { message: '' });
    }
    
    function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;
        
        // Add user message to chat
        addMessageToChat('user', message);
        
        // Clear input field
        userInput.value = '';
        
        // Disable input temporarily
        setInputState(false);
        
        // Send message to server
        socket.emit('message', { message });
    }
    
    function addMessageToChat(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
        
        // Handle markdown-like formatting for bot messages
        if (sender === 'bot' && content.includes('\n')) {
            content = formatBotMessage(content);
        }
        
        messageDiv.innerHTML = content;
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom of chat
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function formatBotMessage(content) {
        // Convert markdown-like syntax to HTML
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
            .replace(/\n\n/g, '<br><br>') // Double line breaks
            .replace(/\n-\s(.*)/g, '<br>• $1') // List items
            .replace(/\n/g, '<br>'); // Single line breaks
    }
    
    function setInputState(enabled) {
        userInput.disabled = !enabled;
        sendButton.disabled = !enabled;
        if (enabled) {
            userInput.focus();
        }
    }
    
    function showResults(resultContent) {
        mbtiResult.innerHTML = formatBotMessage(resultContent);
        document.querySelector('.chat-container').classList.add('hidden');
        resultContainer.classList.remove('hidden');
    }
    
    // Socket.IO Event Handlers
    socket.on('connect', () => {
        console.log('Connected to server');
    });
    
    socket.on('response', (data) => {
        if (data.is_complete && data.mbti_result) {
            // Test is complete, show results
            addMessageToChat('bot', 'Great! Your test is now complete. Here are your results...');
            showResults(data.message);
        } else {
            // Regular message, add to chat
            addMessageToChat('bot', data.message);
            
            // Re-enable input
            setInputState(true);
        }
    });
    
    socket.on('connect_error', (error) => {
        console.error('Connection Error:', error);
        addMessageToChat('bot', 'Sorry, there was an error connecting to the server. Please refresh the page and try again.');
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from server');
        addMessageToChat('bot', 'Disconnected from server. Please refresh the page to reconnect.');
    });
}); 