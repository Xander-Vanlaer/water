/**
 * Authentication JavaScript - Handles login, registration, and token management
 */

const API_URL = 'http://localhost:8000';

// Token management
const TokenManager = {
    setTokens(accessToken, refreshToken) {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
    },
    
    getAccessToken() {
        return localStorage.getItem('access_token');
    },
    
    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    },
    
    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },
    
    isAuthenticated() {
        return !!this.getAccessToken();
    }
};

// API client with automatic token refresh
const apiClient = {
    async request(url, options = {}) {
        const token = TokenManager.getAccessToken();
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        try {
            const response = await fetch(`${API_URL}${url}`, {
                ...options,
                headers
            });
            
            // If unauthorized, try to refresh token
            if (response.status === 401 && TokenManager.getRefreshToken()) {
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    // Retry original request
                    headers['Authorization'] = `Bearer ${TokenManager.getAccessToken()}`;
                    const retryResponse = await fetch(`${API_URL}${url}`, {
                        ...options,
                        headers
                    });
                    return await this.handleResponse(retryResponse);
                }
            }
            
            return await this.handleResponse(response);
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },
    
    async handleResponse(response) {
        const data = await response.json().catch(() => ({}));
        
        if (!response.ok) {
            throw new Error(data.detail || 'Request failed');
        }
        
        return data;
    },
    
    async refreshToken() {
        try {
            const refreshToken = TokenManager.getRefreshToken();
            const response = await fetch(`${API_URL}/api/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken })
            });
            
            if (response.ok) {
                const data = await response.json();
                TokenManager.setTokens(data.access_token, data.refresh_token);
                return true;
            }
            
            // Refresh failed, clear tokens
            TokenManager.clearTokens();
            return false;
        } catch (error) {
            TokenManager.clearTokens();
            return false;
        }
    }
};

// Check authentication on page load
function checkAuth() {
    const isLoginPage = window.location.pathname.includes('login.html');
    
    if (!TokenManager.isAuthenticated() && !isLoginPage) {
        window.location.href = 'login.html';
    } else if (TokenManager.isAuthenticated() && isLoginPage) {
        window.location.href = 'index.html';
    }
}

// Initialize auth check
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkAuth);
} else {
    checkAuth();
}

// Login page functionality
if (window.location.pathname.includes('login.html')) {
    document.addEventListener('DOMContentLoaded', () => {
        const loginForm = document.getElementById('login-form');
        const registerForm = document.getElementById('register-form');
        const showRegisterLink = document.getElementById('show-register');
        const showLoginLink = document.getElementById('show-login');
        const loginCard = document.querySelector('.auth-card:first-child');
        const registerCard = document.getElementById('register-card');
        
        // Toggle between login and register
        showRegisterLink.addEventListener('click', (e) => {
            e.preventDefault();
            loginCard.style.display = 'none';
            registerCard.style.display = 'block';
        });
        
        showLoginLink.addEventListener('click', (e) => {
            e.preventDefault();
            registerCard.style.display = 'none';
            loginCard.style.display = 'block';
        });
        
        // Login form submission
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const totpCode = document.getElementById('totp-code').value;
            const errorDiv = document.getElementById('error-message');
            const totpGroup = document.getElementById('totp-group');
            
            errorDiv.style.display = 'none';
            
            try {
                if (!totpCode && totpGroup.style.display === 'none') {
                    // First login attempt
                    const response = await fetch(`${API_URL}/api/auth/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, password })
                    });
                    
                    const data = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(data.detail || 'Login failed');
                    }
                    
                    if (data.requires_2fa) {
                        // Show 2FA input
                        totpGroup.style.display = 'block';
                        errorDiv.textContent = 'Please enter your 2FA code';
                        errorDiv.className = 'success-message';
                        errorDiv.style.display = 'block';
                    } else {
                        // Login successful
                        TokenManager.setTokens(data.access_token, data.refresh_token);
                        window.location.href = 'index.html';
                    }
                } else if (totpCode) {
                    // 2FA verification
                    const response = await fetch(`${API_URL}/api/auth/verify-2fa`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, totp_code: totpCode })
                    });
                    
                    const data = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(data.detail || '2FA verification failed');
                    }
                    
                    TokenManager.setTokens(data.access_token, data.refresh_token);
                    window.location.href = 'index.html';
                }
            } catch (error) {
                errorDiv.textContent = error.message;
                errorDiv.className = 'error-message';
                errorDiv.style.display = 'block';
            }
        });
        
        // Register form submission
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('reg-username').value;
            const email = document.getElementById('reg-email').value;
            const password = document.getElementById('reg-password').value;
            const passwordConfirm = document.getElementById('reg-password-confirm').value;
            const errorDiv = document.getElementById('register-error');
            const successDiv = document.getElementById('register-success');
            
            errorDiv.style.display = 'none';
            successDiv.style.display = 'none';
            
            // Validate password match
            if (password !== passwordConfirm) {
                errorDiv.textContent = 'Passwords do not match';
                errorDiv.style.display = 'block';
                return;
            }
            
            try {
                const response = await fetch(`${API_URL}/api/auth/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.detail || 'Registration failed');
                }
                
                // Show pending account message
                successDiv.innerHTML = `
                    <strong>Account created!</strong><br>
                    You have limited access. Please contact an administrator at 
                    <a href="mailto:admin@example.com">admin@example.com</a> 
                    to activate your account.
                `;
                successDiv.style.display = 'block';
                registerForm.reset();
                
                // Switch to login form after 5 seconds
                setTimeout(() => {
                    registerCard.style.display = 'none';
                    loginCard.style.display = 'block';
                }, 5000);
            } catch (error) {
                errorDiv.textContent = error.message;
                errorDiv.style.display = 'block';
            }
        });
    });
}

// Export for use in other scripts
if (typeof window !== 'undefined') {
    window.apiClient = apiClient;
    window.TokenManager = TokenManager;
}
