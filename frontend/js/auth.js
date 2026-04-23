// Authentication Module
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    async init() {
        // Check if user is already logged in
        if (api.getToken()) {
            try {
                await this.loadCurrentUser();
                app.showMainApp();
            } catch (error) {
                console.error('Failed to load current user:', error);
                api.removeToken();
                this.showAuth();
            }
        } else {
            this.showAuth();
        }
    }

    async loadCurrentUser() {
        this.currentUser = await api.getCurrentUser();
        this.updateUserProfile();
        return this.currentUser;
    }

    updateUserProfile() {
        if (!this.currentUser) return;

        const nameEl = document.getElementById('current-user-name');
        const emailEl = document.getElementById('current-user-email');
        const avatarEl = document.getElementById('current-user-avatar');

        if (nameEl) {
            nameEl.textContent = this.currentUser.username || this.currentUser.email;
        }

        if (emailEl) {
            emailEl.textContent = this.currentUser.email;
        }

        if (avatarEl) {
            const initial = (this.currentUser.username || this.currentUser.email)[0].toUpperCase();
            avatarEl.innerHTML = `<i class="fas fa-user"></i>`;
            avatarEl.style.background = `linear-gradient(135deg, ${this.getRandomColor()} 0%, ${this.getRandomColor()} 100%)`;
        }
    }

    getRandomColor() {
        const colors = ['#6366f1', '#ec4899', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    showAuth() {
        document.getElementById('loading-screen').classList.add('hidden');
        document.getElementById('auth-container').classList.remove('hidden');
        document.getElementById('app-container').classList.add('hidden');
        this.setupAuthForms();
    }

    setupAuthForms() {
        // Login form
        const loginForm = document.getElementById('login-form');
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleLogin();
        });

        // Register form
        const registerForm = document.getElementById('register-form');
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleRegister();
        });

        // Forgot password form
        const forgotPasswordForm = document.getElementById('forgot-password-form');
        forgotPasswordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleForgotPassword();
        });

        // Form switching
        document.getElementById('show-register').addEventListener('click', (e) => {
            e.preventDefault();
            this.switchForm('register');
        });

        document.getElementById('show-login').addEventListener('click', (e) => {
            e.preventDefault();
            this.switchForm('login');
        });

        document.getElementById('show-forgot-password').addEventListener('click', (e) => {
            e.preventDefault();
            this.switchForm('forgot-password');
        });

        document.getElementById('back-to-login').addEventListener('click', (e) => {
            e.preventDefault();
            this.switchForm('login');
        });
    }

    switchForm(formName) {
        const forms = ['login', 'register', 'forgot-password'];
        forms.forEach(f => {
            document.getElementById(`${f}-form`).classList.add('hidden');
        });
        document.getElementById(`${formName}-form`).classList.remove('hidden');
    }

    async handleLogin() {
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        try {
            const btn = document.querySelector('#login-form button[type="submit"]');
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing in...';

            await api.login(email, password);
            await this.loadCurrentUser();
            
            app.showToast('Welcome back!', 'success');
            app.showMainApp();
        } catch (error) {
            app.showToast(error.message, 'error');
        } finally {
            const btn = document.querySelector('#login-form button[type="submit"]');
            btn.disabled = false;
            btn.innerHTML = 'Sign In';
        }
    }

    async handleRegister() {
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        const confirmPassword = document.getElementById('register-confirm').value;

        // Validation
        if (password !== confirmPassword) {
            app.showToast('Passwords do not match', 'error');
            return;
        }

        if (password.length < 8) {
            app.showToast('Password must be at least 8 characters', 'error');
            return;
        }

        try {
            const btn = document.querySelector('#register-form button[type="submit"]');
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating account...';

            await api.register({ username, email, password });
            
            app.showToast('Account created! Please check your email to verify.', 'success');
            this.switchForm('login');
        } catch (error) {
            app.showToast(error.message, 'error');
        } finally {
            const btn = document.querySelector('#register-form button[type="submit"]');
            btn.disabled = false;
            btn.innerHTML = 'Create Account';
        }
    }

    async handleForgotPassword() {
        const email = document.getElementById('reset-email').value;

        try {
            const btn = document.querySelector('#forgot-password-form button[type="submit"]');
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';

            await api.requestPasswordReset(email);
            
            app.showToast('Password reset link sent to your email', 'success');
            this.switchForm('login');
        } catch (error) {
            app.showToast(error.message, 'error');
        } finally {
            const btn = document.querySelector('#forgot-password-form button[type="submit"]');
            btn.disabled = false;
            btn.innerHTML = 'Send Reset Link';
        }
    }

    async logout() {
        try {
            await api.logout();
            this.currentUser = null;
            app.showToast('Logged out successfully', 'success');
            this.showAuth();
        } catch (error) {
            // Even if API call fails, clear local state
            api.removeToken();
            this.currentUser = null;
            this.showAuth();
        }
    }

    isAuthenticated() {
        return !!api.getToken() && !!this.currentUser;
    }
}

// Create singleton instance
const auth = new AuthManager();
