// Users Module
class UsersManager {
    constructor() {
        this.users = [];
        this.currentPage = 1;
        this.hasMore = true;
        this.loading = false;
    }

    async loadUsers(page = 1) {
        if (this.loading) return;
        
        this.loading = true;
        try {
            const data = await api.getUsers({ page });
            
            if (page === 1) {
                this.users = data.results || data;
            } else {
                this.users = [...this.users, ...(data.results || data)];
            }
            
            this.hasMore = !!data.next || (data.results && data.results.length > 0);
            this.currentPage = page;
            
            this.renderUsers();
        } catch (error) {
            app.showToast('Failed to load users', 'error');
            console.error('Error loading users:', error);
        } finally {
            this.loading = false;
        }
    }

    renderUsers() {
        const grid = document.getElementById('users-grid');
        const currentUserId = auth.currentUser?.id;
        
        // Filter out current user
        const filteredUsers = this.users.filter(u => u.id !== currentUserId);
        
        if (!filteredUsers || filteredUsers.length === 0) {
            grid.innerHTML = `
                <div class="empty-state" style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--gray-500);">
                    <i class="fas fa-users" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                    <h3>No users found</h3>
                    <p>Be the first to join!</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = filteredUsers.map(user => this.createUserCard(user)).join('');
        
        // Add click handlers for message buttons
        grid.querySelectorAll('.btn-message').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const userId = btn.dataset.userId;
                this.startConversation(userId);
            });
        });
    }

    createUserCard(user) {
        const initial = (user.username || user.email)[0].toUpperCase();
        const color = app.generateAvatarColor(user.id);
        
        return `
            <div class="user-card">
                <div class="avatar" style="background: linear-gradient(135deg, ${color} 0%, ${color} 100%); width: 80px; height: 80px; margin: 0 auto 1.5rem; font-size: 1.5rem;">
                    <i class="fas fa-user"></i>
                </div>
                <h3>${this.escapeHtml(user.username || user.email)}</h3>
                <p class="email">${this.escapeHtml(user.email)}</p>
                <div class="user-card-actions">
                    <button class="btn btn-primary btn-message" data-user-id="${user.id}">
                        <i class="fas fa-envelope"></i>
                        <span>Message</span>
                    </button>
                </div>
            </div>
        `;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async searchUsers(query) {
        try {
            const results = await api.searchUsers(query);
            this.users = results.results || results || [];
            this.renderUsers();
        } catch (error) {
            app.showToast('Search failed', 'error');
            console.error('Search error:', error);
        }
    }

    async startConversation(userId) {
        try {
            // Get user details
            const user = await api.getUser(userId);
            
            // Switch to messages view
            app.switchView('messages');
            
            // Small delay to ensure view is loaded
            setTimeout(() => {
                messages.openDirectChat(userId, user);
            }, 100);
            
            app.showToast('Conversation started', 'success');
        } catch (error) {
            app.showToast('Failed to start conversation', 'error');
            console.error('Error starting conversation:', error);
        }
    }
}

// Create singleton instance
const users = new UsersManager();
