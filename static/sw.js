const CACHE_NAME = 'tax-shield-v2';
const STATIC_ASSETS = [
    './',
    './index.html',
    './css/app.css',
    './js/app.js',
    './js/api.js',
    './js/auth.js',
    './js/demo.js',
    './js/demo-data.json',
    './manifest.json',
];

// Install — cache static shell
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
    );
    self.skipWaiting();
});

// Activate — clean old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
        )
    );
    self.clients.claim();
});

// Fetch — network-first for API, cache-first for static assets
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // API calls: always go to network
    if (url.pathname.includes('/api/')) {
        event.respondWith(fetch(event.request));
        return;
    }

    // Static assets: cache-first, fallback to network
    event.respondWith(
        caches.match(event.request).then((cached) => {
            if (cached) return cached;
            return fetch(event.request).then((response) => {
                if (response.ok) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                }
                return response;
            });
        })
    );
});
