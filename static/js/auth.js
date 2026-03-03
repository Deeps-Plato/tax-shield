// Auth state management
import { GET, POST, setTokens, clearTokens, getToken } from './api.js';

let currentUser = null;
const authListeners = [];

function onAuthChange(fn) {
    authListeners.push(fn);
}

function notifyAuth() {
    authListeners.forEach(fn => fn(currentUser));
}

async function checkAuth() {
    if (!getToken()) {
        currentUser = null;
        notifyAuth();
        return false;
    }
    try {
        currentUser = await GET('/auth/me');
        notifyAuth();
        return true;
    } catch {
        clearTokens();
        currentUser = null;
        notifyAuth();
        return false;
    }
}

async function login(email, password) {
    const data = await POST('/auth/login', { email, password });
    setTokens(data.access_token, data.refresh_token);
    await checkAuth();
    return currentUser;
}

async function register(email, password, name) {
    await POST('/auth/register', { email, password, name });
    return login(email, password);
}

function logout() {
    clearTokens();
    currentUser = null;
    notifyAuth();
}

function getUser() {
    return currentUser;
}

function isAdmin() {
    return currentUser?.role === 'admin';
}

export { checkAuth, login, register, logout, getUser, isAdmin, onAuthChange };
