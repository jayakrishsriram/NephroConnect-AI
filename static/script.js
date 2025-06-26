class ChatInterface {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.baseUrl = 'http://localhost:8000'; // Backend server URL
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.patientInfo = document.getElementById('patientInfo');
        this.showLogsButton = document.getElementById('showLogsButton');
        this.logsContainer = document.getElementById('logsContainer');
        
        this.initializeEventListeners();
        this.updateTimestamp();
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    initializeEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        this.showLogsButton.addEventListener('click', () => this.toggleLogs());
    }
    
    updateTimestamp() {
        const timestampElement = document.getElementById('timestamp');
        if (timestampElement) {
            timestampElement.textContent = new Date().toLocaleTimeString();
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.setLoading(true);
        
        try {
            const response = await fetch(`${this.baseUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.addMessage(data.response, 'assistant');
                this.updatePatientInfo(data);
            } else {
                this.addMessage(data.error || 'Sorry, something went wrong.', 'assistant');
            }
        } catch (error) {
            console.error('Error:', error);
            this.addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        } finally {
            this.setLoading(false);
        }
    }
    
    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = `<strong>${sender === 'user' ? 'You' : 'Assistant'}:</strong> ${content}`;
        
        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'timestamp';
        timestampDiv.textContent = new Date().toLocaleTimeString();
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timestampDiv);
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    updatePatientInfo(data) {
        if (data.patient_name) {
            document.getElementById('patientName').textContent = `Patient: ${data.patient_name}`;
            document.getElementById('dischargeStatus').textContent = 
                data.has_discharge_report ? '✅ Discharge report found' : '❌ No discharge report';
            this.patientInfo.style.display = 'block';
        }
    }
    
    async toggleLogs() {
        if (this.logsContainer.style.display === 'none') {
            await this.loadLogs();
            this.logsContainer.style.display = 'block';
            this.showLogsButton.textContent = 'Hide Logs';
        } else {
            this.logsContainer.style.display = 'none';
            this.showLogsButton.textContent = 'View Interaction Log';
        }
    }
    
    async loadLogs() {
        try {
            const response = await fetch(`${this.baseUrl}/logs/${this.sessionId}`);
            const data = await response.json();
            
            if (response.ok) {
                this.displayLogs(data.logs);
            } else {
                document.getElementById('logsList').innerHTML = '<p>No logs available</p>';
            }
        } catch (error) {
            console.error('Error loading logs:', error);
            document.getElementById('logsList').innerHTML = '<p>Error loading logs</p>';
        }
    }
    
    displayLogs(logs) {
        const logsList = document.getElementById('logsList');
        logsList.innerHTML = '';
        
        logs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.innerHTML = `
                <strong>${log.agent}:</strong> ${log.action || log.query || 'N/A'}<br>
                <small>${new Date(log.timestamp).toLocaleString()}</small>
            `;
            logsList.appendChild(logEntry);
        });
    }
    
    setLoading(isLoading) {
        if (isLoading) {
            this.sendButton.disabled = true;
            this.sendButton.textContent = 'Sending...';
            this.messageInput.disabled = true;
        } else {
            this.sendButton.disabled = false;
            this.sendButton.textContent = 'Send';
            this.messageInput.disabled = false;
            this.messageInput.focus();
        }
    }
}

// Initialize the chat interface when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatInterface();
});
