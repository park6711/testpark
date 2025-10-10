// Service Worker for TestPark
// 간단한 Service Worker 구현

const CACHE_NAME = 'testpark-v1';
const urlsToCache = [
  '/',
  '/static/css/',
  '/static/js/',
];

self.addEventListener('install', function(event) {
  // 설치 중에는 캐시 생성
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Service Worker: 캐시 생성');
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // 캐시에서 발견되면 반환, 없으면 네트워크에서 가져오기
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});

console.log('TestPark Service Worker 로드됨');
