const CACHE_NAME = 'supernova-cache-v1';
const OFFLINE_URLS = [
  '/web_ui/index.html',
  '/web_ui/script.js',
  '/web_ui/manifest.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(OFFLINE_URLS))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(resp => resp || fetch(event.request))
  );
});
