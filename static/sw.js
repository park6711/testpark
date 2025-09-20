// Service Worker for PMIS 2.0
const CACHE_NAME = 'pmis-2.0-cache-v1';
const urlsToCache = [
    '/',
    '/static/manifest.json',
    '/accounts/login/',
    '/possiblearea/',
    '/member/',
    '/company/'
];

// Service Worker 설치
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('캐시 열림');
                return cache.addAll(urlsToCache);
            })
    );
    self.skipWaiting();
});

// Service Worker 활성화
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        console.log('오래된 캐시 삭제:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// 네트워크 요청 가로채기
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // 캐시에 있으면 캐시에서 반환
                if (response) {
                    return response;
                }

                // 캐시에 없으면 네트워크에서 가져오기
                return fetch(event.request).then(function(response) {
                    // 유효한 응답인지 확인
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }

                    // 응답 복사 (스트림은 한 번만 사용 가능)
                    const responseToCache = response.clone();

                    caches.open(CACHE_NAME)
                        .then(function(cache) {
                            cache.put(event.request, responseToCache);
                        });

                    return response;
                }).catch(function() {
                    // 네트워크 오류 시 기본 페이지 반환
                    return caches.match('/');
                });
            })
    );
});

// 브라우저 알림 비활성화
self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow('/')
    );
});

// 푸시 메시지 무시
self.addEventListener('push', function(event) {
    // 푸시 알림 무시
    event.waitUntil(Promise.resolve());
});

// 백그라운드 동기화 무시
self.addEventListener('sync', function(event) {
    // 백그라운드 동기화 무시
    event.waitUntil(Promise.resolve());
});