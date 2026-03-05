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
    if (path.startsWith('/tax-records')) return [];
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

// Demo questionnaire flow
const DEMO_QUESTIONS = [
    {
        question_key: 'filing_status',
        question: 'What is your filing status?',
        options: ['Single', 'Married Filing Jointly', 'Married Filing Separately', 'Head of Household'],
    },
    {
        question_key: 'income_source',
        question: 'What is your primary income source?',
        options: ['W-2 Employee', 'Self-Employed / Freelancer', 'Business Owner (LLC/S-Corp)', 'Investor / Retired'],
    },
    {
        question_key: 'home_office',
        question: 'Do you work from home or have a dedicated home office?',
        options: ['Yes — dedicated room', 'Sometimes — shared space', 'No'],
        discovers: ['Home Office Deduction (Simplified Method)', 'Internet Service (Business Portion)'],
    },
    {
        question_key: 'vehicle',
        question: 'Do you use a personal vehicle for business purposes?',
        options: ['Yes — frequently', 'Occasionally', 'No'],
        discovers: ['Standard Mileage Deduction'],
    },
    {
        question_key: 'real_estate',
        question: 'Do you own rental or investment real estate?',
        options: ['Yes — residential rental', 'Yes — commercial property', 'Yes — land / agricultural', 'No'],
        discovers: ['Rental Property Depreciation (Residential 27.5-Year)', 'Mortgage Interest Deduction (Rental Property)', 'Property Tax Deduction (Rental)'],
    },
    {
        question_key: 'retirement',
        question: 'Which retirement accounts do you contribute to?',
        options: ['401(k) / 403(b)', 'IRA (Traditional or Roth)', 'SEP IRA / Solo 401(k)', 'None currently'],
        discovers: ['Traditional IRA Deduction'],
    },
    {
        question_key: 'health',
        question: 'Do you have a High Deductible Health Plan (HDHP) with an HSA?',
        options: ['Yes', 'No', 'Not sure'],
        discovers: ['Health Savings Account (HSA) Contributions'],
    },
    {
        question_key: 'dependents',
        question: 'Do you have children or dependents?',
        options: ['Yes — under 17', 'Yes — 17 or older', 'No'],
        discovers: ['Child Tax Credit', 'Child and Dependent Care Credit'],
    },
];

let demoQStep = 0;
let demoSessionId = 'demo-session-' + Date.now();

function buildDemoQuestion(step, discovered) {
    if (step >= DEMO_QUESTIONS.length) {
        return {
            session_id: demoSessionId,
            question_key: 'complete',
            question: `Questionnaire complete! We identified ${discovered.length} potential deductions based on your answers.`,
            options: null,
            discovered_items: [],
            is_final: true,
        };
    }
    const q = DEMO_QUESTIONS[step];
    return {
        session_id: demoSessionId,
        question_key: q.question_key,
        question: q.question,
        options: q.options,
        discovered_items: discovered,
        is_final: false,
    };
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
    if (path === '/analysis/questionnaire/start') {
        demoQStep = 0;
        demoSessionId = 'demo-session-' + Date.now();
        return buildDemoQuestion(0, []);
    }
    if (path === '/analysis/questionnaire/answer') {
        const data = await loadDemoData();
        const prev = DEMO_QUESTIONS[demoQStep];
        demoQStep++;
        // Resolve discovered items from seed data
        const discovered = (prev?.discovers || []).map(name => {
            const item = data.items.find(i => i.name === name);
            return item ? { id: item.id, name: item.name, description: item.description } : null;
        }).filter(Boolean);
        return buildDemoQuestion(demoQStep, discovered);
    }
    if (path === '/analysis/synergy') {
        return {
            analysis: 'Demo mode: Synergy analysis requires the backend API with Claude AI integration. In production, this analyzes your selected deductions for overlapping benefits and optimization opportunities.',
            item_ids: _body?.item_ids || [],
            cached: false,
        };
    }
    return {};
}
