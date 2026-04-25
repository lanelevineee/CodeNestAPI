// Admin Dashboard JavaScript

class AdminDashboard {
    constructor() {
        this.currentPage = 'dashboard';
        this.api = api;
        this.init();
    }

    init() {
        this.setupNavigation();
        this.setupEventListeners();
        this.loadDashboardData();
        this.startAutoRefresh();
    }

    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item[data-page]');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const page = item.dataset.page;
                this.navigateTo(page);
            });
        });

        // Handle hash navigation
        window.addEventListener('hashchange', () => {
            const hash = window.location.hash.slice(1);
            if (hash && document.getElementById(`${hash}Page`)) {
                this.navigateTo(hash);
            }
        });

        // Check initial hash
        const initialHash = window.location.hash.slice(1);
        if (initialHash && document.getElementById(`${initialHash}Page`)) {
            this.navigateTo(initialHash);
        }
    }

    navigateTo(page) {
        // Update nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.page === page) {
                item.classList.add('active');
            }
        });

        // Update page content
        document.querySelectorAll('.page-content').forEach(content => {
            content.classList.remove('active');
        });
        const targetPage = document.getElementById(`${page}Page`);
        if (targetPage) {
            targetPage.classList.add('active');
        }

        // Update page title
        const titles = {
            dashboard: 'Dashboard',
            users: 'User Management',
            rooms: 'Room Management',
            messages: 'Message Monitoring',
            analytics: 'Analytics Overview',
            settings: 'System Settings',
            monitoring: 'Server Monitoring'
        };
        document.getElementById('pageTitle').textContent = titles[page] || 'Dashboard';

        this.currentPage = page;

        // Load page-specific data
        this.loadPageData(page);
    }

    setupEventListeners() {
        // Menu toggle for mobile
        const menuToggle = document.getElementById('menuToggle');
        const sidebar = document.querySelector('.admin-sidebar');
        if (menuToggle && sidebar) {
            menuToggle.addEventListener('click', () => {
                sidebar.classList.toggle('open');
            });
        }

        // Logout button
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.handleLogout());
        }

        // Global search
        const globalSearch = document.getElementById('globalSearch');
        if (globalSearch) {
            globalSearch.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.handleGlobalSearch(globalSearch.value);
                }
            });
        }

        // Refresh metrics button
        const refreshMetrics = document.getElementById('refreshMetrics');
        if (refreshMetrics) {
            refreshMetrics.addEventListener('click', () => this.refreshMetrics());
        }

        // User and room filters
        const userSearch = document.getElementById('userSearch');
        if (userSearch) {
            userSearch.addEventListener('input', () => this.filterUsers());
        }

        const roomSearch = document.getElementById('roomSearch');
        if (roomSearch) {
            roomSearch.addEventListener('input', () => this.filterRooms());
        }
    }

    async loadDashboardData() {
        try {
            await Promise.all([
                this.loadStats(),
                this.loadRecentUsers(),
                this.loadActivity()
            ]);
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async loadStats() {
        try {
            // Load users count
            const users = await this.api.getUsers({ limit: 1 });
            document.getElementById('totalUsers').textContent = users.count || 0;

            // Load rooms count
            const rooms = await this.api.getRooms({ limit: 1 });
            document.getElementById('totalRooms').textContent = rooms.count || 0;

            // Mock messages and sessions (would need backend endpoints)
            document.getElementById('totalMessages').textContent = Math.floor(Math.random() * 500) + 100;
            document.getElementById('activeSessions').textContent = Math.floor(Math.random() * 50) + 10;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    async loadRecentUsers() {
        try {
            const users = await this.api.getUsers({ limit: 5, ordering: '-date_joined' });
            const tbody = document.querySelector('#recentUsersTable tbody');
            if (tbody && users.results) {
                tbody.innerHTML = users.results.map(user => `
                    <tr>
                        <td>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div class="avatar" style="width: 32px; height: 32px; font-size: 12px;">
                                    ${(user.first_name || user.username || 'U')[0].toUpperCase()}
                                </div>
                                <span>${user.first_name || user.username || 'Unknown'}</span>
                            </div>
                        </td>
                        <td>${user.email || '-'}</td>
                        <td><span class="badge badge-success">Active</span></td>
                        <td>${new Date(user.date_joined).toLocaleDateString()}</td>
                    </tr>
                `).join('');
            }
        } catch (error) {
            console.error('Error loading recent users:', error);
        }
    }

    async loadActivity() {
        // Mock activity data - would come from backend in production
        const activities = [
            { icon: '👤', text: 'New user registered', time: '2 minutes ago' },
            { icon: '🏠', text: 'Room created: "Python Developers"', time: '5 minutes ago' },
            { icon: '💬', text: 'Message sent in "General Chat"', time: '10 minutes ago' },
            { icon: '🔐', text: 'User logged in: admin@codensest.com', time: '15 minutes ago' },
            { icon: '⚙️', text: 'System settings updated', time: '1 hour ago' }
        ];

        const activityList = document.getElementById('activityList');
        if (activityList) {
            activityList.innerHTML = activities.map(activity => `
                <div class="activity-item">
                    <span class="activity-icon">${activity.icon}</span>
                    <div class="activity-content">
                        <p>${activity.text}</p>
                        <small>${activity.time}</small>
                    </div>
                </div>
            `).join('');
        }
    }

    async loadPageData(page) {
        switch (page) {
            case 'users':
                await this.loadUsers();
                break;
            case 'rooms':
                await this.loadRooms();
                break;
            case 'messages':
                await this.loadMessages();
                break;
            case 'monitoring':
                await this.refreshMetrics();
                break;
        }
    }

    async loadUsers() {
        try {
            const users = await this.api.getUsers({ limit: 20 });
            const tbody = document.querySelector('#usersTable tbody');
            if (tbody && users.results) {
                tbody.innerHTML = users.results.map(user => `
                    <tr>
                        <td>#${user.id}</td>
                        <td>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div class="avatar" style="width: 32px; height: 32px; font-size: 12px;">
                                    ${(user.first_name || user.username || 'U')[0].toUpperCase()}
                                </div>
                                <span>${user.first_name || user.username || 'Unknown'}</span>
                            </div>
                        </td>
                        <td>${user.email || '-'}</td>
                        <td><span class="badge badge-success">Active</span></td>
                        <td>${user.is_staff ? 'Admin' : 'User'}</td>
                        <td>${new Date(user.date_joined).toLocaleDateString()}</td>
                        <td>
                            <div class="action-btns">
                                <button class="action-btn view" onclick="admin.viewUser(${user.id})">View</button>
                                <button class="action-btn edit" onclick="admin.editUser(${user.id})">Edit</button>
                                ${!user.is_staff ? `<button class="action-btn delete" onclick="admin.deleteUser(${user.id})">Delete</button>` : ''}
                            </div>
                        </td>
                    </tr>
                `).join('');
            }
        } catch (error) {
            console.error('Error loading users:', error);
        }
    }

    async loadRooms() {
        try {
            const rooms = await this.api.getRooms({ limit: 20 });
            const tbody = document.querySelector('#roomsTable tbody');
            if (tbody && rooms.results) {
                tbody.innerHTML = rooms.results.map(room => `
                    <tr>
                        <td>#${room.id}</td>
                        <td><strong>${room.name}</strong></td>
                        <td>${room.creator?.username || 'Unknown'}</td>
                        <td>${room.member_count || 0}</td>
                        <td><span class="badge ${room.is_private ? 'badge-warning' : 'badge-info'}">${room.is_private ? 'Private' : 'Public'}</span></td>
                        <td><span class="badge badge-success">Active</span></td>
                        <td>${new Date(room.created_at).toLocaleDateString()}</td>
                        <td>
                            <div class="action-btns">
                                <button class="action-btn view" onclick="admin.viewRoom(${room.id})">View</button>
                                <button class="action-btn edit" onclick="admin.editRoom(${room.id})">Edit</button>
                                <button class="action-btn delete" onclick="admin.deleteRoom(${room.id})">Delete</button>
                            </div>
                        </td>
                    </tr>
                `).join('');
            }
        } catch (error) {
            console.error('Error loading rooms:', error);
        }
    }

    async loadMessages() {
        try {
            // Get conversations as proxy for messages
            const conversations = await this.api.getConversations();
            const messageList = document.getElementById('messageList');
            
            // Mock message counts
            document.getElementById('totalMsgCount').textContent = Math.floor(Math.random() * 5000) + 1000;
            document.getElementById('todayMsgCount').textContent = Math.floor(Math.random() * 200) + 50;
            document.getElementById('avgMsgCount').textContent = Math.floor(Math.random() * 150) + 80;

            if (messageList && conversations.results) {
                messageList.innerHTML = conversations.results.slice(0, 10).map(conv => `
                    <div class="activity-item">
                        <span class="activity-icon">💬</span>
                        <div class="activity-content">
                            <p><strong>${conv.participant?.username || 'Unknown'}</strong>: ${conv.last_message?.content || 'No messages'}</p>
                            <small>${new Date(conv.last_message?.timestamp || Date.now()).toLocaleString()}</small>
                        </div>
                    </div>
                `).join('');
            }
        } catch (error) {
            console.error('Error loading messages:', error);
        }
    }

    async refreshMetrics() {
        // Simulate real-time metrics update
        const metrics = {
            cpu: Math.floor(Math.random() * 60) + 20,
            memory: Math.floor(Math.random() * 40) + 40,
            disk: Math.floor(Math.random() * 30) + 20,
            responseTime: Math.floor(Math.random() * 80) + 20,
            requestsPerSec: Math.floor(Math.random() * 50) + 10,
            errorRate: (Math.random() * 0.5).toFixed(1),
            dbConnections: Math.floor(Math.random() * 30) + 5,
            queryTime: Math.floor(Math.random() * 20) + 5,
            slowQueries: Math.floor(Math.random() * 5),
            cacheHitRate: Math.floor(Math.random() * 10) + 85,
            cacheMemory: `${Math.floor(Math.random() * 100) + 200}MB`,
            cacheKeys: Math.floor(Math.random() * 1000) + 1000
        };

        // Update DOM elements
        const updates = {
            'cpuUsage': `${metrics.cpu}%`,
            'memoryUsage': `${metrics.memory}%`,
            'diskUsage': `${metrics.disk}%`,
            'responseTime': `${metrics.responseTime}ms`,
            'requestsPerSec': metrics.requestsPerSec.toString(),
            'errorRate': `${metrics.errorRate}%`,
            'monitorCpu': `${metrics.cpu}%`,
            'monitorMemory': `${(metrics.memory / 100 * 4).toFixed(1)}GB / 4GB`,
            'monitorDisk': `${(metrics.disk / 100 * 500).toFixed(0)}GB / 500GB`,
            'dbConnections': metrics.dbConnections.toString(),
            'queryTime': `${metrics.queryTime}ms`,
            'slowQueries': metrics.slowQueries.toString(),
            'cacheHitRate': `${metrics.cacheHitRate}%`,
            'cacheMemory': metrics.cacheMemory,
            'cacheKeys': metrics.cacheKeys.toLocaleString()
        };

        Object.entries(updates).forEach(([id, value]) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        });

        // Update progress bars
        const progressBars = {
            'cpuUsage': metrics.cpu,
            'memoryUsage': metrics.memory,
            'diskUsage': metrics.disk
        };

        Object.entries(progressBars).forEach(([id, value]) => {
            const el = document.getElementById(id);
            if (el && el.parentElement.classList.contains('progress-bar')) {
                el.parentElement.querySelector('.progress-fill').style.width = `${value}%`;
            }
        });
    }

    handleGlobalSearch(query) {
        if (!query.trim()) return;
        
        // Search both users and rooms
        Promise.all([
            this.api.searchUsers(query),
            this.api.searchRooms(query)
        ]).then(([users, rooms]) => {
            alert(`Found ${users.length} users and ${rooms.length} rooms matching "${query}"`);
            // In production, show results in a modal or dedicated results page
        }).catch(error => {
            console.error('Search error:', error);
        });
    }

    filterUsers() {
        const searchTerm = document.getElementById('userSearch').value.toLowerCase();
        const statusFilter = document.getElementById('userStatusFilter').value;
        
        const rows = document.querySelectorAll('#usersTable tbody tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const matchesSearch = !searchTerm || text.includes(searchTerm);
            const matchesStatus = !statusFilter || row.innerHTML.includes(statusFilter);
            
            row.style.display = (matchesSearch && matchesStatus) ? '' : 'none';
        });
    }

    filterRooms() {
        const searchTerm = document.getElementById('roomSearch').value.toLowerCase();
        const typeFilter = document.getElementById('roomTypeFilter').value;
        
        const rows = document.querySelectorAll('#roomsTable tbody tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const matchesSearch = !searchTerm || text.includes(searchTerm);
            const matchesType = !typeFilter || row.innerHTML.toLowerCase().includes(typeFilter.toLowerCase());
            
            row.style.display = (matchesSearch && matchesType) ? '' : 'none';
        });
    }

    handleLogout() {
        if (confirm('Are you sure you want to logout?')) {
            this.api.logout().then(() => {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '../index.html';
            }).catch(() => {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '../index.html';
            });
        }
    }

    viewUser(id) {
        alert(`View user ${id}`);
        // Implement user detail view
    }

    editUser(id) {
        alert(`Edit user ${id}`);
        // Implement user edit modal
    }

    deleteUser(id) {
        if (confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
            // Implement user deletion
            alert('User deleted successfully');
        }
    }

    viewRoom(id) {
        alert(`View room ${id}`);
        // Implement room detail view
    }

    editRoom(id) {
        alert(`Edit room ${id}`);
        // Implement room edit modal
    }

    deleteRoom(id) {
        if (confirm('Are you sure you want to delete this room? This action cannot be undone.')) {
            // Implement room deletion
            alert('Room deleted successfully');
        }
    }

    startAutoRefresh() {
        // Refresh metrics every 30 seconds
        setInterval(() => {
            if (this.currentPage === 'monitoring' || this.currentPage === 'dashboard') {
                this.refreshMetrics();
            }
        }, 30000);

        // Reload dashboard data every 2 minutes
        setInterval(() => {
            if (this.currentPage === 'dashboard') {
                this.loadDashboardData();
            }
        }, 120000);
    }
}

// Initialize admin dashboard when DOM is ready
let admin;
document.addEventListener('DOMContentLoaded', () => {
    admin = new AdminDashboard();
});
