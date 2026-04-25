// Messages Module
class MessagesManager {
    constructor() {
        this.conversations = [];
        this.currentChat = null;
        this.messages = [];
        this.currentPage = 1;
        this.hasMore = true;
        this.loading = false;
        this.pollingInterval = null;
    }

    async loadConversations() {
        try {
            const data = await api.getConversations();
            this.conversations = data.results || data || [];
            this.renderConversations();
        } catch (error) {
            console.error('Error loading conversations:', error);
            // Don't show error toast for empty conversations
            if (error.message !== 'Authentication required') {
                this.conversations = [];
                this.renderConversations();
            }
        }
    }

    renderConversations() {
        const container = document.getElementById('conversations');
        
        if (!this.conversations || this.conversations.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="padding: 2rem; text-align: center; color: var(--gray-500);">
                    <i class="fas fa-inbox" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                    <p>No conversations yet</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.conversations.map(conv => this.createConversationItem(conv)).join('');
        
        // Add click handlers
        container.querySelectorAll('.conversation-item').forEach(item => {
            item.addEventListener('click', () => {
                const userId = item.dataset.userId;
                const roomId = item.dataset.roomId;
                
                if (roomId) {
                    this.openRoomChat(roomId, conv);
                } else {
                    this.openDirectChat(userId, conv);
                }
            });
        });
    }

    createConversationItem(conv) {
        const user = conv.other_user || conv.user;
        const room = conv.room;
        const lastMessage = conv.last_message;
        const unreadCount = conv.unread_count || 0;
        
        const name = user ? (user.username || user.email) : (room ? room.name : 'Unknown');
        const avatar = user ? this.getUserAvatar(user) : this.getRoomAvatar(room);
        const messageText = lastMessage ? lastMessage.content : 'No messages yet';
        const timestamp = lastMessage ? app.formatDate(lastMessage.created_at) : '';
        
        return `
            <div class="conversation-item" data-user-id="${user?.id || ''}" data-room-id="${room?.id || ''}">
                <div class="conversation-avatar" style="background: ${avatar.color}">
                    ${avatar.content}
                </div>
                <div class="conversation-info">
                    <div class="conversation-header">
                        <span class="conversation-name">${this.escapeHtml(name)}</span>
                        <span class="conversation-time">${timestamp}</span>
                    </div>
                    <div class="conversation-last-message">
                        ${this.escapeHtml(messageText)}
                    </div>
                </div>
                ${unreadCount > 0 ? `<span class="unread-badge">${unreadCount}</span>` : ''}
            </div>
        `;
    }

    getUserAvatar(user) {
        const initial = (user.username || user.email)[0].toUpperCase();
        const color = app.generateAvatarColor(user.id);
        return {
            content: `<i class="fas fa-user"></i>`,
            color: `linear-gradient(135deg, ${color} 0%, ${color} 100%)`
        };
    }

    getRoomAvatar(room) {
        const color = app.generateAvatarColor(room?.id);
        return {
            content: `<i class="fas fa-hashtag"></i>`,
            color: `linear-gradient(135deg, ${color} 0%, ${color} 100%)`
        };
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async openRoomChat(roomId, room) {
        this.currentChat = { type: 'room', id: roomId, data: room };
        
        // Update chat header
        const headerName = document.getElementById('chat-name');
        const headerStatus = document.getElementById('chat-status');
        const headerAvatar = document.getElementById('chat-avatar');
        
        headerName.textContent = room.name;
        headerStatus.textContent = `${room.member_count || 0} members`;
        headerStatus.className = 'status';
        
        const color = app.generateAvatarColor(room.id);
        headerAvatar.style.background = `linear-gradient(135deg, ${color} 0%, ${color} 100%)`;
        headerAvatar.innerHTML = `<i class="fas fa-hashtag"></i>`;

        // Enable input
        this.enableChatInput();

        // Load messages
        await this.loadMessages(roomId);

        // Start polling for new messages
        this.startPolling(roomId);

        // Show chat area on mobile
        if (window.innerWidth <= 1024) {
            document.querySelector('.conversations-list').classList.add('active');
            document.querySelector('.chat-area').classList.add('active');
        }
    }

    async openDirectChat(userId, user) {
        this.currentChat = { type: 'user', id: userId, data: user };
        
        // Update chat header
        const headerName = document.getElementById('chat-name');
        const headerStatus = document.getElementById('chat-status');
        const headerAvatar = document.getElementById('chat-avatar');
        
        headerName.textContent = user.username || user.email;
        headerStatus.textContent = 'Direct Message';
        headerStatus.className = 'status';
        
        const color = app.generateAvatarColor(user.id);
        headerAvatar.style.background = `linear-gradient(135deg, ${color} 0%, ${color} 100%)`;
        headerAvatar.innerHTML = `<i class="fas fa-user"></i>`;

        // Enable input
        this.enableChatInput();

        // Load messages
        await this.loadDirectMessages(userId);

        // Start polling for new messages
        this.startPolling(null, userId);

        // Show chat area on mobile
        if (window.innerWidth <= 1024) {
            document.querySelector('.conversations-list').classList.add('active');
            document.querySelector('.chat-area').classList.add('active');
        }
    }

    enableChatInput() {
        const input = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-message');
        input.disabled = false;
        sendBtn.disabled = false;
    }

    disableChatInput() {
        const input = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-message');
        input.disabled = true;
        sendBtn.disabled = true;
    }

    async loadMessages(roomId) {
        if (this.loading) return;
        
        this.loading = true;
        try {
            const data = await api.getMessages(roomId, { page: this.currentPage });
            this.messages = data.results || data || [];
            this.hasMore = !!data.next;
            this.renderMessages();
        } catch (error) {
            console.error('Error loading messages:', error);
            this.messages = [];
            this.renderMessages();
        } finally {
            this.loading = false;
        }
    }

    async loadDirectMessages(userId) {
        if (this.loading) return;
        
        this.loading = true;
        try {
            const data = await api.getUserMessages(userId, { page: this.currentPage });
            this.messages = data.results || data || [];
            this.hasMore = !!data.next;
            this.renderMessages();
        } catch (error) {
            console.error('Error loading messages:', error);
            this.messages = [];
            this.renderMessages();
        } finally {
            this.loading = false;
        }
    }

    renderMessages() {
        const container = document.getElementById('chat-messages');
        
        if (!this.messages || this.messages.length === 0) {
            container.innerHTML = `
                <div class="empty-chat">
                    <i class="fas fa-comments"></i>
                    <p>No messages yet. Start the conversation!</p>
                </div>
            `;
            return;
        }

        const currentUserId = auth.currentUser?.id;
        
        container.innerHTML = this.messages.map(msg => {
            const isSent = msg.sender?.id === currentUserId;
            const sender = msg.sender || {};
            const avatarInitial = (sender.username || sender.email || '?')[0].toUpperCase();
            const avatarColor = app.generateAvatarColor(sender.id);
            
            return `
                <div class="message ${isSent ? 'sent' : ''}">
                    ${!isSent ? `
                        <div class="message-avatar" style="background: ${avatarColor}">
                            ${avatarInitial}
                        </div>
                    ` : ''}
                    <div class="message-content">
                        ${!isSent && this.currentChat?.type === 'room' ? `
                            <div style="font-size: 0.75rem; font-weight: 600; margin-bottom: 0.25rem;">
                                ${this.escapeHtml(sender.username || sender.email)}
                            </div>
                        ` : ''}
                        <div class="message-text">${this.escapeHtml(msg.content)}</div>
                        <div class="message-time">${app.formatDate(msg.created_at)}</div>
                    </div>
                </div>
            `;
        }).join('');

        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    }

    async sendMessage() {
        const input = document.getElementById('message-input');
        const content = input.value.trim();
        
        if (!content || !this.currentChat) return;

        try {
            input.value = '';
            
            if (this.currentChat.type === 'room') {
                await api.sendMessage(this.currentChat.id, content);
            } else {
                await api.sendDirectMessage(this.currentChat.id, content);
            }

            // Reload messages
            if (this.currentChat.type === 'room') {
                await this.loadMessages(this.currentChat.id);
            } else {
                await this.loadDirectMessages(this.currentChat.id);
            }
        } catch (error) {
            app.showToast('Failed to send message', 'error');
            console.error('Send message error:', error);
            // Restore message in input
            input.value = content;
        }
    }

    startPolling(roomId, userId) {
        // Clear existing polling
        this.stopPolling();

        // Poll every 5 seconds for new messages
        this.pollingInterval = setInterval(async () => {
            if (!this.currentChat) return;

            try {
                if (this.currentChat.type === 'room') {
                    await this.loadMessages(this.currentChat.id);
                } else {
                    await this.loadDirectMessages(this.currentChat.id);
                }
            } catch (error) {
                console.error('Polling error:', error);
            }
        }, 5000);
    }

    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }

    goBackToConversations() {
        if (window.innerWidth <= 1024) {
            document.querySelector('.chat-area').classList.remove('active');
            document.querySelector('.conversations-list').classList.remove('active');
        }
    }
}

// Create singleton instance
const messages = new MessagesManager();
