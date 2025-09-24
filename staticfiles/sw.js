// TestPark Service Worker
const CACHE_NAME = 'testpark-v3'; // v3로 업데이트
const urlsToCache = [
  '/',
  '/static/css/main.a874db27.css',
  '/static/js/main.f7a94119.js' // 새로운 JS 파일
];

// Install event
self.addEventListener('install', event => {
  console.log('Service Worker: Installing v3...');
  self.skipWaiting(); // 즉시 활성화
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: 캐시 생성');
        return cache.addAll(urlsToCache);
      })
      .catch(err => {
        console.error('Service Worker: 캐시 생성 실패', err);
      })
  );
});

// Fetch event
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});

// Activate event
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating v3...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          // v3 이외의 모든 캐시 삭제
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: 오래된 캐시 삭제:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      return clients.claim(); // 즉시 컨트롤 획득
    })
  );
});

console.log('TestPark Service Worker 로드됨');
