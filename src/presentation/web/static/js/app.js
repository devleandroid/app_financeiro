/* ============================================
   SitesPro - Frontend JavaScript
   ============================================ */

const API_BASE = '/api';

// ========== AUTH STATE ==========
function getToken() {
    return localStorage.getItem('sitespro_token');
}

function setToken(token) {
    localStorage.setItem('sitespro_token', token);
}

function clearToken() {
    localStorage.removeItem('sitespro_token');
    localStorage.removeItem('sitespro_user');
}

function getUser() {
    const data = localStorage.getItem('sitespro_user');
    return data ? JSON.parse(data) : null;
}

function setUser(user) {
    localStorage.setItem('sitespro_user', JSON.stringify(user));
}

function isLoggedIn() {
    return !!getToken();
}

// ========== API HELPER ==========
async function apiCall(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers
    };

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Erro na requisicao');
        }

        return data;
    } catch (error) {
        if (error.message === 'Failed to fetch') {
            throw new Error('Erro de conexao com o servidor');
        }
        throw error;
    }
}

// ========== AUTH FUNCTIONS ==========
async function register(email, password, nome, telefone) {
    const data = await apiCall('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ email, password, nome, telefone })
    });
    setToken(data.token);
    setUser(data.user);
    return data;
}

async function login(email, password) {
    const data = await apiCall('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
    });
    setToken(data.token);
    setUser(data.user);
    return data;
}

function logout() {
    clearToken();
    window.location.href = '/';
}

async function fetchCurrentUser() {
    const data = await apiCall('/auth/me');
    setUser(data.user);
    return data.user;
}

// ========== SITES FUNCTIONS ==========
async function listSites() {
    return await apiCall('/sites');
}

async function createSite(siteData) {
    return await apiCall('/sites', {
        method: 'POST',
        body: JSON.stringify(siteData)
    });
}

async function getSite(siteId) {
    return await apiCall(`/sites/${siteId}`);
}

async function updateSite(siteId, siteData) {
    return await apiCall(`/sites/${siteId}`, {
        method: 'PUT',
        body: JSON.stringify(siteData)
    });
}

async function deleteSite(siteId) {
    return await apiCall(`/sites/${siteId}`, {
        method: 'DELETE'
    });
}

async function publishSite(siteId) {
    return await apiCall(`/sites/${siteId}/publish`, {
        method: 'POST'
    });
}

async function checkSiteLimit() {
    return await apiCall('/sites/check-limit');
}

// ========== SUBSCRIPTION FUNCTIONS ==========
async function getPlans() {
    return await apiCall('/subscriptions/plans');
}

async function getSubscriptionStatus() {
    return await apiCall('/subscriptions/status');
}

async function checkout(plano) {
    return await apiCall('/subscriptions/checkout', {
        method: 'POST',
        body: JSON.stringify({ plano })
    });
}

async function cancelSubscription() {
    return await apiCall('/subscriptions/cancel', {
        method: 'POST'
    });
}

// ========== TEMPLATE FUNCTIONS ==========
async function listTemplates() {
    return await apiCall('/templates');
}

// ========== UI HELPERS ==========
function showAlert(message, type = 'info') {
    const existing = document.querySelector('.alert-toast');
    if (existing) existing.remove();

    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-toast`;
    alert.style.cssText = 'position:fixed;top:90px;right:20px;z-index:3000;min-width:300px;animation:slideIn 0.3s ease;';
    alert.innerHTML = `<span>${message}</span>`;
    document.body.appendChild(alert);

    setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
    }, 4000);
}

function showModal(title, content, actions) {
    const overlay = document.getElementById('modal-overlay');
    if (!overlay) return;

    overlay.querySelector('.modal h2').textContent = title;
    overlay.querySelector('.modal-body').innerHTML = content;

    const actionsDiv = overlay.querySelector('.modal-actions');
    actionsDiv.innerHTML = '';
    if (actions) {
        actions.forEach(action => {
            const btn = document.createElement('button');
            btn.className = `btn ${action.class || 'btn-primary'}`;
            btn.textContent = action.text;
            btn.onclick = () => {
                action.onClick();
                closeModal();
            };
            actionsDiv.appendChild(btn);
        });
    }

    overlay.classList.add('active');
}

function closeModal() {
    const overlay = document.getElementById('modal-overlay');
    if (overlay) overlay.classList.remove('active');
}

// ========== NAVIGATION ==========
function updateNavForAuth() {
    const navAuth = document.getElementById('nav-auth');
    if (!navAuth) return;

    if (isLoggedIn()) {
        const user = getUser();
        navAuth.innerHTML = `
            <a href="/dashboard">Dashboard</a>
            <span style="color:var(--text-muted);font-size:0.85rem;">${user ? user.nome : ''}</span>
            <button class="btn btn-outline" onclick="logout()" style="padding:6px 16px;font-size:0.85rem;">Sair</button>
        `;
    } else {
        navAuth.innerHTML = `
            <a href="/login">Entrar</a>
            <a href="/register" class="btn btn-primary" style="padding:8px 20px;">Criar Conta</a>
        `;
    }
}

// ========== INIT ==========
document.addEventListener('DOMContentLoaded', () => {
    updateNavForAuth();

    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', (e) => {
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

// CSS animation
const style = document.createElement('style');
style.textContent = '@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }';
document.head.appendChild(style);
