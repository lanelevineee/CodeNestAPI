// Main Application Module
class App {
    constructor() {
        this.currentView = 'rooms';
        this.init();
    }

    init() {
        // Wait for auth to initialize
        setTimeout(() => {
            this.setupEventListeners();
        }, 100);
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const view = item.dataset.view;
                this.switchView(view);
            });
        });

        // Mobile menu toggle
        document.getElementById('menu-toggle').addEventListener('click', () => {
            document.querySelector('.sidebar').classList.add('active');
        });

        document.getElementById('close-sidebar').addEventListener('click', () => {
            document.querySelector('.sidebar').classList.remove('active');
        });

        // Logout
        document.getElementById('logout-btn').addEventListener('click', () => {
            auth.logout();
        });

        // Create room button
        document.getElementById('create-room-btn').addEventListener('click', () => {
            this.openModal('create-room-modal');
        });

        // Close modal buttons
        document.querySelectorAll('.close-modal').forEach(btn => {
            btn.addEventListener('click', () => {
                this.closeModal('create-room-modal');
            });
        });

        // Modal overlay click
        document.querySelectorAll('.modal-overlay').forEach(overlay => {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    this.closeModal('create-room-modal');
                }
            });
        });

        // Create room form
        document.getElementById('create-room-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await rooms.createRoom();
        });

        // Global search
        let searchTimeout;
        document.getElementById('global-search').addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.handleSearch(e.target.value);
            }, 500);
        });

        // Message input
        document.getElementById('message-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                messages.sendMessage();
            }
        });

        document.getElementById('send-message').addEventListener('click', () => {
            messages.sendMessage();
        });
    }

    switchView(viewName) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.view === viewName) {
                item.classList.add('active');
            }
        });

        // Update views
        document.querySelectorAll('.view').forEach(view => {
            view.classList.add('hidden');
            view.classList.remove('active');
        });

        const targetView = document.getElementById(`${viewName}-view`);
        targetView.classList.remove('hidden');
        targetView.classList.add('active');

        this.currentView = viewName;

        // Load data for the view
        this.loadViewData(viewName);

        // Close mobile sidebar
        document.querySelector('.sidebar').classList.remove('active');
    }

    async loadViewData(viewName) {
        switch (viewName) {
            case 'rooms':
                await rooms.loadRooms();
                break;
            case 'messages':
                await messages.loadConversations();
                break;
            case 'users':
                await users.loadUsers();
                break;
        }
    }

    handleSearch(query) {
        if (!query.trim()) {
            if (this.currentView === 'rooms') {
                rooms.loadRooms();
            } else if (this.currentView === 'users') {
                users.loadUsers();
            }
            return;
        }

        if (this.currentView === 'rooms') {
            rooms.searchRooms(query);
        } else if (this.currentView === 'users') {
            users.searchUsers(query);
        }
    }

    showMainApp() {
        document.getElementById('loading-screen').classList.add('hidden');
        document.getElementById('auth-container').classList.add('hidden');
        document.getElementById('app-container').classList.remove('hidden');
        
        // Load initial view
        this.loadViewData(this.currentView);
    }

    // Modal management
    openModal(modalId) {
        document.getElementById(modalId).classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    closeModal(modalId) {
        document.getElementById(modalId).classList.add('hidden');
        document.body.style.overflow = '';
        
        // Reset form
        if (modalId === 'create-room-modal') {
            document.getElementById('create-room-form').reset();
        }
    }

    // Toast notifications
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };

        toast.innerHTML = `
            <i class="fas ${icons[type]} toast-icon"></i>
            <span class="toast-message">${message}</span>
            <button class="toast-close">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Close button
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.removeToast(toast);
        });

        container.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            this.removeToast(toast);
        }, 5000);
    }

    removeToast(toast) {
        toast.style.animation = 'toastSlideIn 0.3s ease reverse';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }

    // Utility functions
    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (days === 0) {
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } else if (days === 1) {
            return 'Yesterday';
        } else if (days < 7) {
            return date.toLocaleDateString([], { weekday: 'short' });
        } else {
            return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
        }
    }

    getInitials(name) {
        if (!name) return '?';
        return name.split(' ')
            .map(n => n[0])
            .join('')
            .toUpperCase()
            .slice(0, 2);
    }

    generateAvatarColor(id) {
        const colors = [
            '#6366f1', '#ec4899', '#06b6d4', '#10b981',
            '#f59e0b', '#ef4444', '#8b5cf6', '#3b82f6'
        ];
        const index = id ? id.toString().charCodeAt(0) % colors.length : 0;
        return colors[index];
    }
}

// Create singleton instance
const app = new App();
