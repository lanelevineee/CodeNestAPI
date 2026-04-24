// API Configuration and Utilities
const API_CONFIG = {
    baseURL: 'http://localhost:8000/api/v1',
    version: 'v1',
    timeout: 10000,
};

// API Service Class
class APIService {
    constructor() {
        this.baseURL = API_CONFIG.baseURL;
        this.token = localStorage.getItem('access_token');
    }

    // Get authentication token
    getToken() {
        return this.token || localStorage.getItem('access_token');
    }

    // Set authentication token
    setToken(token) {
        this.token = token;
        localStorage.setItem('access_token', token);
    }

    // Remove authentication token
    removeToken() {
        this.token = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }

    // Build headers with authentication
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
        };

        if (includeAuth && this.getToken()) {
            headers['Authorization'] = `Bearer ${this.getToken()}`;
        }

        return headers;
    }

    // Generic request handler
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: this.getHeaders(options.includeAuth !== false),
        };

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);

            const response = await fetch(url, {
                ...config,
                signal: controller.signal,
            });

            clearTimeout(timeoutId);

            // Handle token expiration
            if (response.status === 401) {
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    config.headers = this.getHeaders();
                    const retryResponse = await fetch(url, config);
                    return await this.handleResponse(retryResponse);
                }
                throw new Error('Authentication required');
            }

            return await this.handleResponse(response);
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }

    // Handle response
    async handleResponse(response) {
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || error.message || 'Request failed');
        }

        // Handle no content responses
        if (response.status === 204) {
            return null;
        }

        return await response.json();
    }

    // Refresh access token
    async refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            return false;
        }

        try {
            const response = await fetch(`${this.baseURL}/token/refresh/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh: refreshToken }),
            });

            if (response.ok) {
                const data = await response.json();
                this.setToken(data.access);
                return true;
            }

            return false;
        } catch (error) {
            console.error('Token refresh failed:', error);
            return false;
        }
    }

    // Authentication endpoints
    async login(email, password) {
        const response = await this.request('/login/', {
            method: 'POST',
            includeAuth: false,
            body: JSON.stringify({ email, password }),
        });

        if (response.access) {
            this.setToken(response.access);
            if (response.refresh) {
                localStorage.setItem('refresh_token', response.refresh);
            }
        }

        return response;
    }

    async register(userData) {
        return await this.request('/register/', {
            method: 'POST',
            includeAuth: false,
            body: JSON.stringify(userData),
        });
    }

    async logout() {
        try {
            await this.request('/logout/', {
                method: 'POST',
            });
        } finally {
            this.removeToken();
        }
    }

    async getCurrentUser() {
        return await this.request('/user/');
    }

    // Rooms endpoints
    async getRooms(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`/rooms/${queryString ? `?${queryString}` : ''}`);
    }

    async getRoom(id) {
        return await this.request(`/rooms/${id}/`);
    }

    async createRoom(roomData) {
        return await this.request('/rooms/', {
            method: 'POST',
            body: JSON.stringify(roomData),
        });
    }

    async updateRoom(id, roomData) {
        return await this.request(`/rooms/${id}/`, {
            method: 'PATCH',
            body: JSON.stringify(roomData),
        });
    }

    async deleteRoom(id) {
        return await this.request(`/rooms/${id}/`, {
            method: 'DELETE',
        });
    }

    async joinRoom(id) {
        return await this.request(`/rooms/${id}/join/`, {
            method: 'POST',
        });
    }

    async leaveRoom(id) {
        return await this.request(`/rooms/${id}/leave/`, {
            method: 'POST',
        });
    }

    // Messages endpoints
    async getMessages(roomId, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`/rooms/${roomId}/messages/${queryString ? `?${queryString}` : ''}`);
    }

    async sendMessage(roomId, content) {
        return await this.request(`/rooms/${roomId}/messages/`, {
            method: 'POST',
            body: JSON.stringify({ content }),
        });
    }

    async getConversations() {
        return await this.request('/messages/conversations/');
    }

    async getUserMessages(userId, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`/messages/${userId}/${queryString ? `?${queryString}` : ''}`);
    }

    async sendDirectMessage(userId, content) {
        return await this.request(`/messages/${userId}/`, {
            method: 'POST',
            body: JSON.stringify({ content }),
        });
    }

    // Users endpoints
    async getUsers(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return await this.request(`/users/${queryString ? `?${queryString}` : ''}`);
    }

    async getUser(id) {
        return await this.request(`/users/${id}/`);
    }

    async searchUsers(query) {
        return await this.request(`/users/search/?query=${encodeURIComponent(query)}`);
    }

    async searchRooms(query) {
        return await this.request(`/rooms/search/?query=${encodeURIComponent(query)}`);
    }

    // Password reset
    async requestPasswordReset(email) {
        return await this.request('/password-reset/', {
            method: 'POST',
            includeAuth: false,
            body: JSON.stringify({ email }),
        });
    }

    async confirmPasswordReset(token, uid, newPassword) {
        return await this.request('/password-reset/confirm/', {
            method: 'POST',
            includeAuth: false,
            body: JSON.stringify({ token, uid, new_password: newPassword }),
        });
    }
}

// Create singleton instance
const api = new APIService();
