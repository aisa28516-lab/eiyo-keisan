// 電波がないときも開けるようにする。通信できるときは常に最新を取りに行く。
const C = 'eiyo-44eb9ab300';
self.addEventListener('install', e => { self.skipWaiting(); e.waitUntil(caches.open(C).then(c => c.addAll(['./', 'config.js', 'manifest.webmanifest', 'icon-180.png', 'icon-192.png']))) });
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.origin !== location.origin) return;
  e.respondWith(fetch(e.request).then(r => { const cp = r.clone(); caches.open(C).then(c => c.put(e.request, cp)); return r }).catch(() => caches.match(e.request, { ignoreSearch: true })));
});
