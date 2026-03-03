import { GET, POST, PATCH, DELETE, uploadFile } from './api.js';
import { checkAuth, login, register, logout, getUser, isAdmin, onAuthChange } from './auth.js';

// ── State ──
let categories = [];
let currentPage = 'dashboard';

// ── Router ──
const routes = {
    '': 'dashboard',
    'dashboard': 'dashboard',
    'search': 'search',
    'items': 'items',
    'my-items': 'my-items',
    'strategies': 'strategies',
    'transactions': 'transactions',
    'questionnaire': 'questionnaire',
    'analysis': 'analysis',
    'tax-forms': 'tax-forms',
    'admin': 'admin',
    'login': 'login',
    'register': 'register',
};

function navigate(page) {
    window.location.hash = `#${page}`;
}

function getRoute() {
    return window.location.hash.replace('#', '') || 'dashboard';
}

// ── Toast ──
function toast(message, type = 'info') {
    const colors = { info: 'bg-blue-600', success: 'bg-green-600', error: 'bg-red-600' };
    const div = document.createElement('div');
    div.className = `toast ${colors[type]} text-white px-4 py-2 rounded-lg shadow-lg`;
    div.textContent = message;
    document.body.appendChild(div);
    setTimeout(() => div.remove(), 3000);
}

// ── Render Engine ──
const $main = () => document.getElementById('main-content');

function html(strings, ...values) {
    return strings.reduce((result, str, i) => result + str + (values[i] ?? ''), '');
}

async function render() {
    const route = getRoute();
    const user = getUser();

    if (!user && !['login', 'register'].includes(route)) {
        navigate('login');
        return;
    }
    if (user && ['login', 'register'].includes(route)) {
        navigate('dashboard');
        return;
    }

    updateNav(user);
    currentPage = route;

    const main = $main();
    if (!main) return;

    main.innerHTML = '<div class="flex justify-center py-12"><div class="spinner"></div></div>';

    try {
        switch (route) {
            case 'login': main.innerHTML = renderLogin(); break;
            case 'register': main.innerHTML = renderRegister(); break;
            case 'dashboard': await renderDashboard(main); break;
            case 'search': main.innerHTML = renderSearch(); break;
            case 'items': await renderItems(main); break;
            case 'my-items': await renderMyItems(main); break;
            case 'strategies': await renderStrategies(main); break;
            case 'transactions': await renderTransactions(main); break;
            case 'questionnaire': main.innerHTML = renderQuestionnaire(); break;
            case 'analysis': main.innerHTML = renderAnalysis(); break;
            case 'tax-forms': await renderTaxForms(main); break;
            case 'admin': await renderAdmin(main); break;
            default: main.innerHTML = '<p class="p-8 text-gray-500">Page not found</p>';
        }
    } catch (e) {
        main.innerHTML = `<p class="p-8 text-red-600">Error: ${e.message}</p>`;
    }
}

function updateNav(user) {
    const nav = document.getElementById('nav-links');
    if (!nav) return;
    if (!user) { nav.innerHTML = ''; return; }

    const links = [
        ['dashboard', 'Dashboard'],
        ['search', 'Search'],
        ['items', 'Browse Items'],
        ['my-items', 'My Items'],
        ['strategies', 'Strategies'],
        ['transactions', 'Transactions'],
        ['questionnaire', 'Questionnaire'],
        ['analysis', 'AI Analysis'],
        ['tax-forms', 'Tax Forms'],
    ];
    if (user.role === 'admin') links.push(['admin', 'Admin']);

    nav.innerHTML = links.map(([href, label]) =>
        `<a href="#${href}" class="px-3 py-2 rounded text-sm ${
            getRoute() === href ? 'bg-blue-700 text-white' : 'text-blue-100 hover:bg-blue-700'
        }">${label}</a>`
    ).join('');

    // Mobile slide-out nav
    const mobileNav = document.getElementById('mobile-nav-links');
    if (mobileNav) {
        mobileNav.innerHTML = links.map(([href, label]) =>
            `<a href="#${href}" class="px-3 py-2 rounded text-sm ${
                getRoute() === href ? 'bg-blue-700 text-white' : 'text-blue-100 hover:bg-blue-700'
            }">${label}</a>`
        ).join('');
        // Close mobile nav on link click
        mobileNav.querySelectorAll('a').forEach(a =>
            a.addEventListener('click', () => document.getElementById('mobile-nav')?.classList.add('hidden'))
        );
    }

    // Bottom tab bar — show when logged in
    const mobileTabs = document.getElementById('mobile-tabs');
    if (mobileTabs) {
        mobileTabs.classList.toggle('hidden', !user);
        mobileTabs.querySelectorAll('.tab-link').forEach(tab => {
            const isActive = tab.dataset.tab === getRoute();
            tab.classList.toggle('active', isActive);
            tab.classList.toggle('text-blue-800', isActive);
            tab.classList.toggle('text-gray-500', !isActive);
        });
    }

    document.getElementById('user-info').innerHTML = `
        <span class="text-blue-100 text-sm mr-3 hidden sm:inline">${user.name}</span>
        <button id="logout-btn" class="text-blue-200 hover:text-white text-sm">Logout</button>
    `;
    document.getElementById('logout-btn')?.addEventListener('click', () => {
        logout();
        navigate('login');
    });
}

// ── Pages ──

function renderLogin() {
    return html`
    <div class="max-w-md mx-auto mt-16 bg-white rounded-lg shadow p-8">
        <h1 class="text-2xl font-bold text-gray-800 mb-6 text-center">Tax Shield</h1>
        <form id="login-form" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input type="email" id="login-email" required
                    class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <input type="password" id="login-password" required
                    class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none">
            </div>
            <button type="submit" class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
                Sign In
            </button>
            <p class="text-center text-sm text-gray-500">
                No account? <a href="#register" class="text-blue-600 hover:underline">Register</a>
            </p>
        </form>
    </div>`;
}

function renderRegister() {
    return html`
    <div class="max-w-md mx-auto mt-16 bg-white rounded-lg shadow p-8">
        <h1 class="text-2xl font-bold text-gray-800 mb-6 text-center">Create Account</h1>
        <form id="register-form" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input type="text" id="reg-name" required
                    class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input type="email" id="reg-email" required
                    class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <input type="password" id="reg-password" required minlength="8"
                    class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:outline-none">
            </div>
            <button type="submit" class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
                Register
            </button>
            <p class="text-center text-sm text-gray-500">
                Already have an account? <a href="#login" class="text-blue-600 hover:underline">Sign in</a>
            </p>
        </form>
    </div>`;
}

async function renderDashboard(main) {
    const user = getUser();
    let stats = { items: 0, categories: 0, strategies: 0, saved_items: 0 };
    try {
        if (isAdmin()) stats = await GET('/admin/stats');
    } catch { /* non-admin */ }

    let myItems = [];
    try { myItems = await GET('/user-items?limit=5'); } catch {}

    main.innerHTML = html`
    <div class="max-w-6xl mx-auto p-6">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">Welcome, ${user.name}</h1>
        <p class="text-gray-500 mb-8">Your tax deduction dashboard</p>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div class="bg-white rounded-lg shadow p-5">
                <div class="text-2xl font-bold text-blue-600">${stats.items || '—'}</div>
                <div class="text-sm text-gray-500">Deduction Items</div>
            </div>
            <div class="bg-white rounded-lg shadow p-5">
                <div class="text-2xl font-bold text-green-600">${stats.saved_items || '—'}</div>
                <div class="text-sm text-gray-500">Saved Items</div>
            </div>
            <div class="bg-white rounded-lg shadow p-5">
                <div class="text-2xl font-bold text-purple-600">${stats.strategies || '—'}</div>
                <div class="text-sm text-gray-500">Strategies</div>
            </div>
            <div class="bg-white rounded-lg shadow p-5">
                <div class="text-2xl font-bold text-amber-600">${stats.categories || '—'}</div>
                <div class="text-sm text-gray-500">Categories</div>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-lg font-semibold mb-4">Quick Actions</h2>
                <div class="space-y-2">
                    <a href="#search" class="block px-4 py-3 bg-blue-50 rounded-lg hover:bg-blue-100 text-blue-700">
                        Search for deductions
                    </a>
                    <a href="#questionnaire" class="block px-4 py-3 bg-green-50 rounded-lg hover:bg-green-100 text-green-700">
                        Start smart questionnaire
                    </a>
                    <a href="#transactions" class="block px-4 py-3 bg-purple-50 rounded-lg hover:bg-purple-100 text-purple-700">
                        Upload bank statements
                    </a>
                    <a href="#tax-forms" class="block px-4 py-3 bg-amber-50 rounded-lg hover:bg-amber-100 text-amber-700">
                        Generate tax forms
                    </a>
                </div>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-lg font-semibold mb-4">My Saved Items</h2>
                ${myItems.length ? myItems.map(ui => `
                    <div class="flex justify-between items-center py-2 border-b last:border-0">
                        <span class="text-gray-700">${ui.item?.name || 'Item #' + ui.item_id}</span>
                        <span class="text-green-600 font-medium">
                            ${ui.estimated_savings ? '$' + ui.estimated_savings.toLocaleString() : '—'}
                        </span>
                    </div>
                `).join('') : '<p class="text-gray-400">No saved items yet. <a href="#search" class="text-blue-600">Start searching</a></p>'}
            </div>
        </div>
    </div>`;
}

function renderSearch() {
    return html`
    <div class="max-w-4xl mx-auto p-6">
        <h1 class="text-2xl font-bold text-gray-800 mb-6">Search Tax Deductions & Credits</h1>
        <form id="search-form" class="flex gap-3 mb-6">
            <input type="text" id="search-input" placeholder="e.g., laptop, home office, vehicle..."
                class="flex-1 border rounded-lg px-4 py-3 text-lg focus:ring-2 focus:ring-blue-500 focus:outline-none">
            <select id="search-category" class="border rounded-lg px-3 py-2">
                <option value="">All Categories</option>
            </select>
            <button type="submit" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
                Search
            </button>
        </form>
        <div id="search-results"></div>
    </div>`;
}

async function renderItems(main) {
    if (!categories.length) {
        try { categories = await GET('/categories'); } catch {}
    }
    const items = await GET('/items?limit=100');
    main.innerHTML = html`
    <div class="max-w-6xl mx-auto p-6">
        <h1 class="text-2xl font-bold text-gray-800 mb-6">Browse Deduction Items</h1>
        <div class="flex gap-3 mb-6 flex-wrap">
            <button class="cat-filter px-3 py-1 rounded-full text-sm bg-blue-600 text-white" data-id="">All</button>
            ${categories.map(c => `
                <button class="cat-filter px-3 py-1 rounded-full text-sm bg-gray-200 hover:bg-gray-300" data-id="${c.id}">
                    ${c.name}
                </button>
            `).join('')}
        </div>
        <div id="items-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            ${items.map(renderItemCard).join('')}
        </div>
    </div>`;
}

function renderItemCard(item) {
    const typeColors = {
        deduction: 'bg-green-100 text-green-800',
        credit: 'bg-blue-100 text-blue-800',
        both: 'bg-purple-100 text-purple-800',
    };
    return html`
    <div class="bg-white rounded-lg shadow p-4 card-hover" data-category="${item.category_id}">
        <div class="flex justify-between items-start mb-2">
            <h3 class="font-semibold text-gray-800">${item.name}</h3>
            <span class="text-xs px-2 py-1 rounded-full ${typeColors[item.deduction_type] || 'bg-gray-100'}">
                ${item.deduction_type}
            </span>
        </div>
        <p class="text-sm text-gray-600 mb-3">${item.description.substring(0, 120)}${item.description.length > 120 ? '...' : ''}</p>
        <div class="flex justify-between items-center text-xs text-gray-400">
            <span>${item.irs_reference || ''}</span>
            ${item.max_amount ? `<span class="font-medium">Max: $${item.max_amount.toLocaleString()}</span>` : ''}
        </div>
        <button class="save-item-btn mt-3 w-full text-sm bg-blue-50 text-blue-600 py-1.5 rounded hover:bg-blue-100"
            data-item-id="${item.id}">
            Save to My Items
        </button>
    </div>`;
}

async function renderMyItems(main) {
    const myItems = await GET('/user-items');
    const totalSavings = myItems.reduce((s, ui) => s + (ui.estimated_savings || 0), 0);

    main.innerHTML = html`
    <div class="max-w-4xl mx-auto p-6">
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-bold text-gray-800">My Saved Items</h1>
            <div class="text-right">
                <div class="text-2xl font-bold text-green-600">$${totalSavings.toLocaleString()}</div>
                <div class="text-sm text-gray-500">Est. Total Savings</div>
            </div>
        </div>
        ${myItems.length ? html`
        <div class="space-y-3">
            ${myItems.map(ui => html`
            <div class="bg-white rounded-lg shadow p-4 flex justify-between items-center">
                <div>
                    <h3 class="font-semibold text-gray-800">${ui.item?.name || 'Item #' + ui.item_id}</h3>
                    <p class="text-sm text-gray-500">${ui.notes || 'No notes'}</p>
                    <div class="flex gap-2 mt-1">
                        <span class="text-xs px-2 py-0.5 rounded ${ui.claimed ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}">
                            ${ui.claimed ? 'Claimed' : 'Not claimed'}
                        </span>
                        <span class="text-xs text-gray-400">TY ${ui.tax_year}</span>
                    </div>
                </div>
                <div class="flex items-center gap-3">
                    <span class="text-lg font-bold text-green-600">
                        ${ui.estimated_savings ? '$' + ui.estimated_savings.toLocaleString() : '—'}
                    </span>
                    <button class="remove-item-btn text-red-400 hover:text-red-600 text-sm" data-id="${ui.id}">Remove</button>
                </div>
            </div>
            `).join('')}
        </div>
        ` : '<p class="text-gray-400 text-center py-12">No saved items. <a href="#search" class="text-blue-600">Search for deductions</a></p>'}
    </div>`;
}

async function renderStrategies(main) {
    const strategies = await GET('/strategies');
    main.innerHTML = html`
    <div class="max-w-4xl mx-auto p-6">
        <h1 class="text-2xl font-bold text-gray-800 mb-6">Tax Strategies</h1>
        <div class="space-y-4">
            ${strategies.map(s => html`
            <details class="bg-white rounded-lg shadow group">
                <summary class="p-4 cursor-pointer flex justify-between items-center">
                    <div>
                        <h3 class="font-semibold text-gray-800">${s.name}</h3>
                        <div class="flex gap-2 mt-1">
                            <span class="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-700">${s.complexity}</span>
                            ${s.estimated_savings ? `<span class="text-xs px-2 py-0.5 rounded bg-green-100 text-green-700">${s.estimated_savings}</span>` : ''}
                        </div>
                    </div>
                    <span class="text-gray-400 group-open:rotate-180 transition-transform">▼</span>
                </summary>
                <div class="px-4 pb-4 border-t">
                    <p class="text-gray-600 mt-3 mb-3">${s.description}</p>
                    ${s.requirements ? `<p class="text-sm"><strong>Requirements:</strong> ${s.requirements}</p>` : ''}
                    ${s.example ? `<p class="text-sm mt-2"><strong>Example:</strong> ${s.example}</p>` : ''}
                    ${s.caveats ? `<p class="text-sm mt-2 text-amber-700"><strong>Caveats:</strong> ${s.caveats}</p>` : ''}
                </div>
            </details>
            `).join('')}
        </div>
    </div>`;
}

async function renderTransactions(main) {
    let transactions = [];
    try { transactions = await GET('/transactions?limit=100'); } catch {}

    main.innerHTML = html`
    <div class="max-w-6xl mx-auto p-6">
        <h1 class="text-2xl font-bold text-gray-800 mb-6">Transactions</h1>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="font-semibold mb-3">Upload CSV Statement</h2>
                <div id="csv-dropzone" class="dropzone">
                    <p class="text-gray-500 mb-2">Drag & drop your bank CSV here</p>
                    <input type="file" id="csv-file" accept=".csv" class="hidden">
                    <button id="csv-browse" class="text-blue-600 hover:underline text-sm">or browse files</button>
                </div>
                <div id="csv-result" class="mt-3 hidden"></div>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="font-semibold mb-3">Bank Connections (Plaid)</h2>
                <div id="plaid-connections"></div>
                <button id="plaid-link-btn" class="mt-3 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm">
                    Connect Bank Account
                </button>
            </div>
        </div>

        <div class="bg-white rounded-lg shadow">
            <div class="p-4 border-b flex justify-between items-center">
                <h2 class="font-semibold">${transactions.length} Transactions</h2>
                <div class="flex gap-2">
                    <select id="txn-filter-deductible" class="border rounded px-2 py-1 text-sm">
                        <option value="">All</option>
                        <option value="true">Deductible</option>
                        <option value="false">Not Deductible</option>
                    </select>
                </div>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="text-left px-4 py-2">Date</th>
                            <th class="text-left px-4 py-2">Description</th>
                            <th class="text-left px-4 py-2">Merchant</th>
                            <th class="text-right px-4 py-2">Amount</th>
                            <th class="text-center px-4 py-2">Deductible</th>
                            <th class="text-left px-4 py-2">Source</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${transactions.map(t => html`
                        <tr class="border-t hover:bg-gray-50">
                            <td class="px-4 py-2">${new Date(t.date).toLocaleDateString()}</td>
                            <td class="px-4 py-2">${t.description}</td>
                            <td class="px-4 py-2">${t.merchant || '—'}</td>
                            <td class="px-4 py-2 text-right font-medium">$${t.amount.toFixed(2)}</td>
                            <td class="px-4 py-2 text-center">
                                ${t.is_deductible === true ? '<span class="text-green-600">Yes</span>' :
                                  t.is_deductible === false ? '<span class="text-red-500">No</span>' :
                                  '<span class="text-gray-400">?</span>'}
                            </td>
                            <td class="px-4 py-2"><span class="text-xs px-2 py-0.5 rounded bg-gray-100">${t.source}</span></td>
                        </tr>
                        `).join('')}
                    </tbody>
                </table>
                ${!transactions.length ? '<p class="text-center py-8 text-gray-400">No transactions yet. Upload a CSV or connect your bank.</p>' : ''}
            </div>
        </div>
    </div>`;
}

function renderQuestionnaire() {
    return html`
    <div class="max-w-2xl mx-auto p-6">
        <h1 class="text-2xl font-bold text-gray-800 mb-2">Smart Tax Questionnaire</h1>
        <p class="text-gray-500 mb-6">Answer a few questions to discover deductions you might be missing.</p>
        <div id="q-container" class="bg-white rounded-lg shadow p-6">
            <button id="q-start" class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
                Start Questionnaire
            </button>
        </div>
        <div id="q-discoveries" class="mt-6 hidden">
            <h2 class="font-semibold text-gray-800 mb-3">Discovered Deductions</h2>
            <div id="q-items" class="space-y-2"></div>
        </div>
    </div>`;
}

function renderAnalysis() {
    return html`
    <div class="max-w-4xl mx-auto p-6">
        <h1 class="text-2xl font-bold text-gray-800 mb-2">AI Synergy Analysis</h1>
        <p class="text-gray-500 mb-6">Select saved items to find overlapping deductions and optimization strategies.</p>
        <div id="analysis-items" class="space-y-2 mb-4"></div>
        <button id="run-analysis" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700" disabled>
            Run Analysis (select 2+ items)
        </button>
        <div id="analysis-result" class="mt-6 hidden bg-white rounded-lg shadow p-6 prose"></div>
    </div>`;
}

async function renderTaxForms(main) {
    let records = [];
    try { records = await GET('/tax-records'); } catch {}

    main.innerHTML = html`
    <div class="max-w-4xl mx-auto p-6">
        <h1 class="text-2xl font-bold text-gray-800 mb-6">Tax Forms</h1>

        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h2 class="font-semibold mb-4">Generate New Form</h2>
            <form id="generate-form" class="flex gap-3 flex-wrap">
                <select id="form-type" class="border rounded-lg px-3 py-2" required>
                    <option value="">Select form...</option>
                    <option value="1040">Form 1040</option>
                    <option value="schedule_a">Schedule A</option>
                    <option value="schedule_c">Schedule C</option>
                    <option value="schedule_d">Schedule D</option>
                    <option value="1120s">Form 1120-S</option>
                    <option value="1065">Form 1065</option>
                    <option value="w2">W-2</option>
                    <option value="1099">1099</option>
                </select>
                <select id="form-filing-type" class="border rounded-lg px-3 py-2">
                    <option value="individual">Individual</option>
                    <option value="self_employed">Self-Employed</option>
                    <option value="s_corp">S-Corporation</option>
                    <option value="partnership">Partnership</option>
                </select>
                <input type="number" id="form-year" value="2025" class="border rounded-lg px-3 py-2 w-24">
                <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                    Generate Draft
                </button>
            </form>
        </div>

        <div class="space-y-3">
            ${records.map(r => html`
            <div class="bg-white rounded-lg shadow p-4 flex justify-between items-center">
                <div>
                    <h3 class="font-semibold">${r.form_type} — ${r.tax_year}</h3>
                    <span class="text-xs px-2 py-0.5 rounded ${
                        r.status === 'final' ? 'bg-green-100 text-green-700' :
                        r.status === 'review' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-gray-100 text-gray-600'
                    }">${r.status}</span>
                    <span class="text-xs text-gray-400 ml-2">${new Date(r.generated_at).toLocaleDateString()}</span>
                </div>
                <a href="/api/tax-forms/${r.id}/pdf" target="_blank"
                    class="bg-blue-50 text-blue-600 px-4 py-2 rounded hover:bg-blue-100 text-sm">
                    Download PDF
                </a>
            </div>
            `).join('')}
            ${!records.length ? '<p class="text-gray-400 text-center py-8">No forms generated yet.</p>' : ''}
        </div>
    </div>`;
}

async function renderAdmin(main) {
    if (!isAdmin()) { navigate('dashboard'); return; }

    const stats = await GET('/admin/stats');
    let users = [];
    try { users = await GET('/admin/users'); } catch {}

    main.innerHTML = html`
    <div class="max-w-4xl mx-auto p-6">
        <h1 class="text-2xl font-bold text-gray-800 mb-6">Admin Panel</h1>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            ${Object.entries(stats).map(([k, v]) => `
                <div class="bg-white rounded-lg shadow p-4 text-center">
                    <div class="text-2xl font-bold text-blue-600">${v}</div>
                    <div class="text-sm text-gray-500">${k.replace('_', ' ')}</div>
                </div>
            `).join('')}
        </div>

        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <div class="flex justify-between items-center mb-4">
                <h2 class="font-semibold">Seed Data</h2>
                <button id="seed-btn" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 text-sm">
                    Run Seed
                </button>
            </div>
            <div id="seed-result"></div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
            <h2 class="font-semibold mb-4">Users</h2>
            <div class="space-y-2">
                ${users.map(u => `
                    <div class="flex justify-between items-center py-2 border-b">
                        <div>
                            <span class="font-medium">${u.name}</span>
                            <span class="text-sm text-gray-500 ml-2">${u.email}</span>
                            <span class="text-xs ml-2 px-1.5 py-0.5 rounded ${u.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-gray-100'}">${u.role}</span>
                        </div>
                        <button class="toggle-user-btn text-sm ${u.is_active ? 'text-red-500' : 'text-green-500'}"
                            data-user-id="${u.id}">
                            ${u.is_active ? 'Disable' : 'Enable'}
                        </button>
                    </div>
                `).join('')}
            </div>
        </div>
    </div>`;
}

// ── Event Delegation ──
document.addEventListener('click', async (e) => {
    const target = e.target;

    // Save item button
    if (target.classList.contains('save-item-btn')) {
        const itemId = parseInt(target.dataset.itemId);
        try {
            await POST('/user-items', { item_id: itemId });
            toast('Item saved!', 'success');
            target.textContent = 'Saved!';
            target.disabled = true;
        } catch (err) {
            toast(err.message, 'error');
        }
    }

    // Remove saved item
    if (target.classList.contains('remove-item-btn')) {
        try {
            await DELETE(`/user-items/${target.dataset.id}`);
            toast('Item removed', 'info');
            render();
        } catch (err) {
            toast(err.message, 'error');
        }
    }

    // Category filter
    if (target.classList.contains('cat-filter')) {
        document.querySelectorAll('.cat-filter').forEach(b => b.className = b.className.replace('bg-blue-600 text-white', 'bg-gray-200'));
        target.classList.remove('bg-gray-200');
        target.classList.add('bg-blue-600', 'text-white');
        const catId = target.dataset.id;
        document.querySelectorAll('#items-grid > div').forEach(card => {
            card.style.display = (!catId || card.dataset.category === catId) ? '' : 'none';
        });
    }

    // Seed button
    if (target.id === 'seed-btn') {
        target.disabled = true;
        target.textContent = 'Seeding...';
        try {
            const result = await POST('/admin/seed');
            document.getElementById('seed-result').innerHTML =
                `<p class="text-green-600">Done! ${JSON.stringify(result.counts)}</p>`;
        } catch (err) {
            document.getElementById('seed-result').innerHTML =
                `<p class="text-red-600">${err.message}</p>`;
        }
        target.disabled = false;
        target.textContent = 'Run Seed';
    }

    // Toggle user active
    if (target.classList.contains('toggle-user-btn')) {
        try {
            await PATCH(`/admin/users/${target.dataset.userId}/toggle-active`);
            render();
        } catch (err) {
            toast(err.message, 'error');
        }
    }

    // CSV browse
    if (target.id === 'csv-browse') {
        document.getElementById('csv-file')?.click();
    }

    // Questionnaire start
    if (target.id === 'q-start') {
        target.disabled = true;
        target.textContent = 'Loading...';
        try {
            const q = await POST('/analysis/questionnaire/start', { tax_year: 2025 });
            showQuestion(q);
        } catch (err) {
            toast(err.message, 'error');
        }
    }
});

function showQuestion(q) {
    const container = document.getElementById('q-container');
    if (q.is_final) {
        container.innerHTML = `
            <div class="text-center">
                <div class="text-green-600 text-lg font-semibold mb-2">Questionnaire Complete!</div>
                <p class="text-gray-600">${q.question}</p>
            </div>`;
        return;
    }

    container.innerHTML = `
        <h3 class="text-lg font-medium mb-4">${q.question}</h3>
        <div class="space-y-2">
            ${(q.options || []).map(opt => `
                <button class="q-option block w-full text-left px-4 py-3 border rounded-lg hover:bg-blue-50"
                    data-session="${q.session_id}" data-key="${q.question_key}" data-response="${opt}">
                    ${opt}
                </button>
            `).join('')}
        </div>`;

    // Show discoveries
    if (q.discovered_items?.length) {
        const disc = document.getElementById('q-discoveries');
        const items = document.getElementById('q-items');
        disc?.classList.remove('hidden');
        q.discovered_items.forEach(item => {
            items.innerHTML += `<div class="bg-green-50 p-3 rounded">${item.name}: ${item.description || ''}</div>`;
        });
    }

    container.querySelectorAll('.q-option').forEach(btn => {
        btn.addEventListener('click', async () => {
            btn.disabled = true;
            try {
                const next = await POST('/analysis/questionnaire/answer', {
                    session_id: btn.dataset.session,
                    question_key: btn.dataset.key,
                    response: btn.dataset.response,
                });
                showQuestion(next);
            } catch (err) {
                toast(err.message, 'error');
            }
        });
    });
}

// Form submissions
document.addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;

    if (form.id === 'login-form') {
        try {
            await login(
                document.getElementById('login-email').value,
                document.getElementById('login-password').value,
            );
            navigate('dashboard');
        } catch (err) {
            toast(err.message, 'error');
        }
    }

    if (form.id === 'register-form') {
        try {
            await register(
                document.getElementById('reg-email').value,
                document.getElementById('reg-password').value,
                document.getElementById('reg-name').value,
            );
            navigate('dashboard');
        } catch (err) {
            toast(err.message, 'error');
        }
    }

    if (form.id === 'search-form') {
        const query = document.getElementById('search-input').value.trim();
        if (!query) return;
        const categoryId = document.getElementById('search-category').value;
        const resultsDiv = document.getElementById('search-results');
        resultsDiv.innerHTML = '<div class="flex justify-center py-8"><div class="spinner"></div></div>';

        try {
            const body = { query, limit: 30 };
            if (categoryId) body.category_id = parseInt(categoryId);
            const data = await POST('/search', body);
            resultsDiv.innerHTML = `
                <p class="text-sm text-gray-500 mb-4">${data.total} results for "${data.query}"</p>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    ${data.items.map(renderItemCard).join('')}
                </div>`;
        } catch (err) {
            resultsDiv.innerHTML = `<p class="text-red-600">${err.message}</p>`;
        }
    }

    if (form.id === 'generate-form') {
        const formType = document.getElementById('form-type').value;
        const filingType = document.getElementById('form-filing-type').value;
        const year = parseInt(document.getElementById('form-year').value);
        if (!formType) return;

        try {
            await POST('/tax-records', { tax_year: year, filing_type: filingType, form_type: formType });
            toast('Form generated!', 'success');
            render();
        } catch (err) {
            toast(err.message, 'error');
        }
    }
});

// CSV upload
document.addEventListener('change', async (e) => {
    if (e.target.id === 'csv-file') {
        const file = e.target.files[0];
        if (!file) return;
        const resultDiv = document.getElementById('csv-result');
        resultDiv.classList.remove('hidden');
        resultDiv.innerHTML = '<div class="spinner mx-auto"></div>';

        try {
            const data = await uploadFile('/transactions/upload-csv', file, { tax_year: 2025 });
            resultDiv.innerHTML = `
                <p class="text-green-600">Imported: ${data.imported} | Skipped: ${data.skipped}</p>
                ${data.errors.length ? `<p class="text-red-500 text-sm mt-1">${data.errors.join('<br>')}</p>` : ''}`;
            setTimeout(render, 1500);
        } catch (err) {
            resultDiv.innerHTML = `<p class="text-red-600">${err.message}</p>`;
        }
    }
});

// Analysis page: load items on navigate
window.addEventListener('hashchange', async () => {
    render();

    if (getRoute() === 'analysis') {
        setTimeout(loadAnalysisItems, 100);
    }
    if (getRoute() === 'search') {
        setTimeout(loadCategoryFilter, 100);
    }
});

async function loadCategoryFilter() {
    if (!categories.length) {
        try { categories = await GET('/categories'); } catch {}
    }
    const select = document.getElementById('search-category');
    if (select && categories.length) {
        categories.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.id;
            opt.textContent = c.name;
            select.appendChild(opt);
        });
    }
}

async function loadAnalysisItems() {
    const container = document.getElementById('analysis-items');
    const btn = document.getElementById('run-analysis');
    if (!container || !btn) return;

    try {
        const myItems = await GET('/user-items');
        const selected = new Set();

        container.innerHTML = myItems.map(ui => `
            <label class="flex items-center gap-3 bg-white rounded-lg shadow p-3 cursor-pointer hover:bg-blue-50">
                <input type="checkbox" class="analysis-cb" data-item-id="${ui.item_id}" value="${ui.item_id}">
                <span>${ui.item?.name || 'Item #' + ui.item_id}</span>
            </label>
        `).join('') || '<p class="text-gray-400">Save some items first!</p>';

        container.addEventListener('change', () => {
            selected.clear();
            container.querySelectorAll('.analysis-cb:checked').forEach(cb => selected.add(parseInt(cb.value)));
            btn.disabled = selected.size < 2;
            btn.textContent = selected.size < 2
                ? `Run Analysis (select ${2 - selected.size} more)`
                : `Run Analysis (${selected.size} items)`;
        });

        btn.addEventListener('click', async () => {
            btn.disabled = true;
            btn.textContent = 'Analyzing...';
            const resultDiv = document.getElementById('analysis-result');
            resultDiv.classList.remove('hidden');
            resultDiv.innerHTML = '<div class="flex justify-center py-8"><div class="spinner"></div></div>';

            try {
                const data = await POST('/analysis/synergy', { item_ids: [...selected] });
                resultDiv.innerHTML = `
                    ${data.cached ? '<p class="text-xs text-gray-400 mb-2">Cached result</p>' : ''}
                    <div class="prose">${data.analysis.replace(/\n/g, '<br>')}</div>`;
            } catch (err) {
                resultDiv.innerHTML = `<p class="text-red-600">${err.message}</p>`;
            }
            btn.disabled = false;
            btn.textContent = `Run Analysis (${selected.size} items)`;
        });
    } catch {}
}

// CSV drag and drop
document.addEventListener('dragover', (e) => {
    const dz = document.getElementById('csv-dropzone');
    if (dz && dz.contains(e.target)) {
        e.preventDefault();
        dz.classList.add('active');
    }
});
document.addEventListener('dragleave', (e) => {
    const dz = document.getElementById('csv-dropzone');
    if (dz) dz.classList.remove('active');
});
document.addEventListener('drop', async (e) => {
    const dz = document.getElementById('csv-dropzone');
    if (dz && dz.contains(e.target)) {
        e.preventDefault();
        dz.classList.remove('active');
        const file = e.dataTransfer?.files[0];
        if (file) {
            // Trigger via the file input
            const input = document.getElementById('csv-file');
            const dt = new DataTransfer();
            dt.items.add(file);
            input.files = dt.files;
            input.dispatchEvent(new Event('change'));
        }
    }
});

// ── Init ──
async function init() {
    await checkAuth();
    render();
}

onAuthChange(() => render());
init();
