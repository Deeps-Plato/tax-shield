// Demo mode: serves embedded data when no backend is available (e.g. GitHub Pages)
let demoData = null;

async function loadDemoData() {
    if (demoData) return demoData;
    const base = import.meta.url.replace(/\/js\/demo\.js.*/, '');
    const resp = await fetch(`${base}/js/demo-data.json`);
    demoData = await resp.json();
    return demoData;
}

export async function isDemo() {
    try {
        const resp = await fetch('/api/categories', { method: 'HEAD' });
        return !resp.ok;
    } catch {
        return true;
    }
}

const DEMO_USER = {
    id: '00000000-0000-0000-0000-000000000001',
    email: 'demo@taxshield.local',
    name: 'Demo User',
    role: 'admin',
    filing_type: 'self_employed',
    is_active: true,
    created_at: new Date().toISOString(),
};

export function getDemoUser() {
    return DEMO_USER;
}

export async function demoGET(path) {
    const data = await loadDemoData();

    if (path === '/auth/me') return DEMO_USER;
    if (path === '/categories') return data.categories;
    if (path.startsWith('/items')) return data.items;
    if (path.startsWith('/strategies')) return data.strategies;
    if (path.startsWith('/transactions')) return [];
    if (path.startsWith('/user-items')) return [];
    if (path === '/admin/stats') {
        return {
            users: 1,
            items: data.items.length,
            categories: data.categories.length,
            strategies: data.strategies.length,
            saved_items: 0,
        };
    }
    return [];
}

export async function demoPOST(path, _body) {
    if (path === '/auth/login' || path === '/auth/register') {
        return { access_token: 'demo-token', refresh_token: 'demo-refresh', token_type: 'bearer' };
    }
    if (path === '/search') {
        const data = await loadDemoData();
        const query = (_body?.query || '').toLowerCase();
        const results = data.items.filter(i =>
            i.name.toLowerCase().includes(query) ||
            i.description.toLowerCase().includes(query)
        ).slice(0, 20);
        return { items: results, total: results.length, query: _body?.query || '' };
    }
    return {};
}
