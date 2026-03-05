// API wrapper with auth token management
// Falls back to demo mode when no backend is available (GitHub Pages)

import { isDemo, demoGET, demoPOST } from './demo.js';

const API_BASE = '/api';
let _demoMode = null;

async function checkDemoMode() {
    if (_demoMode === null) _demoMode = await isDemo();
    return _demoMode;
}

function getToken() {
    return localStorage.getItem('access_token');
}

function getRefreshToken() {
    return localStorage.getItem('refresh_token');
}

function setTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
}

function clearTokens() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
}

async function api(path, options = {}) {
    // Demo mode bypass
    if (await checkDemoMode()) {
        const method = (options.method || 'GET').toUpperCase();
        if (method === 'GET') return demoGET(path);
        if (method === 'POST') {
            const body = typeof options.body === 'string' ? JSON.parse(options.body) : options.body;
            return demoPOST(path, body);
        }
        return {};
    }

    const url = `${API_BASE}${path}`;
    const headers = { ...options.headers };

    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    if (options.body && !(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(options.body);
    }

    let response = await fetch(url, { ...options, headers });

    // Try refresh on 401
    if (response.status === 401 && getRefreshToken()) {
        const refreshed = await tryRefresh();
        if (refreshed) {
            headers['Authorization'] = `Bearer ${getToken()}`;
            response = await fetch(url, { ...options, headers });
        }
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    if (response.status === 204) return null;
    return response.json();
}

async function tryRefresh() {
    try {
        const resp = await fetch(`${API_BASE}/auth/refresh?refresh_token=${getRefreshToken()}`, {
            method: 'POST',
        });
        if (!resp.ok) return false;
        const data = await resp.json();
        setTokens(data.access_token, data.refresh_token);
        return true;
    } catch {
        clearTokens();
        return false;
    }
}

// Convenience methods
const GET = (path) => api(path);
const POST = (path, body) => api(path, { method: 'POST', body });
const PATCH = (path, body) => api(path, { method: 'PATCH', body });
const DELETE = (path) => api(path, { method: 'DELETE' });

async function uploadFile(path, file, params = {}) {
    const formData = new FormData();
    formData.append('file', file);
    const query = new URLSearchParams(params).toString();
    const url = query ? `${path}?${query}` : path;
    return api(url, { method: 'POST', body: formData });
}

export { GET, POST, PATCH, DELETE, uploadFile, setTokens, clearTokens, getToken, checkDemoMode };
