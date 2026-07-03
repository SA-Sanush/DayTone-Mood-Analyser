/**
 * DayTone Service Worker
 * ======================
 * Strategy:
 *   - Static assets (CSS, JS, fonts, icons): Cache-First
 *   - HTML pages: Network-First with offline fallback
 *   - API / form POSTs: Network-only (never cache)
 *
 * Update flow: bump CACHE_VERSION to force refresh on next visit.
 */

const CACHE_VERSION = 'daytone-v10';
const OFFLINE_URL   = '/offline';

// Static assets to pre-cache on install
const PRECACHE_URLS = [
  '/offline',
  '/static/css/bootstrap.min.css',
  '/static/css/custom-v7.min.css',
  '/static/css/dark-v7.min.css',
  '/static/js/bootstrap.bundle.min.js',
  '/static/js/lucide.min.js',
  '/static/js/darkmode.js',
  '/static/js/ambient.js',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
];

// ── Install: pre-cache static shell ──────────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then(cache => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())   // activate immediately
  );
});

// ── Activate: delete old caches ───────────────────────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key !== CACHE_VERSION)
          .map(key => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

// ── Fetch: routing strategies ─────────────────────────────────────────────────
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // 1. Never intercept non-GET, cross-origin, or API requests
  if (request.method !== 'GET') return;
  if (url.origin !== self.location.origin) return;
  if (url.pathname.startsWith('/api/')) return;

  // 2. Static assets → Cache-First
  if (isStaticAsset(url.pathname)) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // 3. HTML pages → Network-First with offline fallback
  if (request.headers.get('Accept')?.includes('text/html')) {
    event.respondWith(networkFirstWithOfflineFallback(request));
    return;
  }

  // 4. Everything else → Network-First
  event.respondWith(networkFirst(request));
});

// ── Helpers ───────────────────────────────────────────────────────────────────

function isStaticAsset(pathname) {
  return (
    pathname.startsWith('/static/css/') ||
    pathname.startsWith('/static/js/') ||
    pathname.startsWith('/static/icons/') ||
    pathname.startsWith('/static/img/')
  );
}

async function cacheFirst(request) {
  const cached = await caches.match(request, { ignoreSearch: true });
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_VERSION);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return new Response('Offline — static asset unavailable', { status: 503 });
  }
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_VERSION);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request, { ignoreSearch: true });
    return cached || new Response('Offline', { status: 503 });
  }
}

async function networkFirstWithOfflineFallback(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_VERSION);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request, { ignoreSearch: true });
    if (cached) return cached;

    // Return the offline page
    const offlinePage = await caches.match(OFFLINE_URL);
    return offlinePage || new Response(
      '<h1>You are offline</h1><p>Please check your connection.</p>',
      { headers: { 'Content-Type': 'text/html' } }
    );
  }
}

// ── Push notifications (future extension point) ───────────────────────────────
self.addEventListener('push', event => {
  if (!event.data) return;
  const data = event.data.json();
  event.waitUntil(
    self.registration.showNotification(data.title || 'DayTone', {
      body: data.body || "Don't forget to log today's mood!",
      icon: '/static/icons/icon-192.png',
      badge: '/static/icons/icon-96.png',
      tag: 'daytone-reminder',
      renotify: true,
      data: { url: data.url || '/' },
    })
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data?.url || '/')
  );
});
