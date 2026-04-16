const API = {
    baseUrl: '/api',

    async request(method, path, body = null) {
        const opts = {
            method,
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        };
        if (body) opts.body = JSON.stringify(body);
        const res = await fetch(this.baseUrl + path, opts);
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: 'Request failed' }));
            throw new Error(err.detail || 'Request failed');
        }
        if (res.status === 204) return null;
        return res.json();
    },

    get: (path) => API.request('GET', path),
    post: (path, body) => API.request('POST', path, body),
    put: (path, body) => API.request('PUT', path, body),
    patch: (path, body) => API.request('PATCH', path, body),
    delete: (path) => API.request('DELETE', path),
};

const Auth = {
    user: null,

    async init() {
        try {
            this.user = await API.get('/auth/me');
        } catch {
            this.user = null;
        }
        this.updateNav();
    },

    updateNav() {
        const loginLink = document.getElementById('nav-login');
        const userMenu = document.getElementById('nav-user-menu');
        const userEmailEl = document.getElementById('nav-user-email');
        const adminLinks = document.querySelectorAll('.admin-only');

        if (this.user) {
            if (loginLink) loginLink.style.display = 'none';
            if (userMenu) userMenu.style.display = 'block';
            if (userEmailEl) userEmailEl.textContent = this.user.email.split('@')[0];
            if (this.user.role === 'admin') {
                adminLinks.forEach(el => el.style.display = 'flex');
            }
        } else {
            if (loginLink) loginLink.style.display = 'flex';
            if (userMenu) userMenu.style.display = 'none';
        }
    },

    async logout() {
        try {
            await API.delete('/auth/logout');
        } catch {}
        this.user = null;
        window.location.href = '/';
    },

    isLoggedIn() {
        return !!this.user;
    },

    isAdmin() {
        return this.user?.role === 'admin';
    }
};

function showAlert(container, message, type = 'error') {
    const existing = container.querySelector('.alert');
    if (existing) existing.remove();

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    container.prepend(alert);

    setTimeout(() => alert.remove(), 5000);
}

function toggleUserMenu() {
    const dropdown = document.getElementById('user-dropdown');
    if (dropdown) dropdown.classList.toggle('open');
}

document.addEventListener('click', (e) => {
    const dropdown = document.getElementById('user-dropdown');
    const btn = document.getElementById('user-menu-btn');
    if (dropdown && !dropdown.contains(e.target) && btn && !btn.contains(e.target)) {
        dropdown.classList.remove('open');
    }
});

function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('open');
        document.body.style.overflow = '';
    }
}

document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.classList.remove('open');
        document.body.style.overflow = '';
    }
});

function renderStars(count) {
    if (!count) return '';
    return '★'.repeat(count) + '☆'.repeat(5 - count);
}

function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('uk-UA', {
        day: '2-digit', month: '2-digit', year: 'numeric'
    });
}

function formatCurrency(amount) {
    return '₴' + amount.toLocaleString('uk-UA');
}

document.addEventListener('DOMContentLoaded', () => {
    Auth.init();
});