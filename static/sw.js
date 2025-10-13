// Service Worker for TestPark
// 개선된 Service Worker - 불필요한 페이지 리로드 방지

const CACHE_NAME = 'testpark-v1';
const urlsToCache = [
  '/',
  '/static/css/',
  '/static/js/',
];

// 설치 이벤트: 새 Service Worker가 설치될 때
self.addEventListener('install', function(event) {
  console.log('Service Worker: 설치 중...');

  // 즉시 활성화하지 않고 대기 (기존 페이지들이 닫힐 때까지)
  // skipWaiting()을 제거하여 자동 새로고침 방지
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Service Worker: 캐시 생성 완료');
        // 실제 필요한 리소스만 캐시 (선택적)
        // return cache.addAll(urlsToCache);
        return Promise.resolve();
      })
  );
});

// 활성화 이벤트: 새 Service Worker가 활성화될 때
self.addEventListener('activate', function(event) {
  console.log('Service Worker: 활성화됨');

  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          // 오래된 캐시 삭제
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: 오래된 캐시 삭제', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(function() {
      // 모든 클라이언트를 즉시 제어하지 않음 (자동 새로고침 방지)
      // return self.clients.claim(); // 주석 처리
      console.log('Service Worker: 준비 완료');
    })
  );
});

// 페치 이벤트: 네트워크 우선 전략으로 변경
self.addEventListener('fetch', function(event) {
  // API 요청은 항상 네트워크로
  if (event.request.url.includes('/api/') || event.request.url.includes('/order/')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // 네트워크 우선, 실패 시 캐시 사용
  event.respondWith(
    fetch(event.request)
      .then(function(response) {
        // 성공적인 응답을 캐시에 저장
        if (response && response.status === 200) {
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(event.request, responseToCache);
          });
        }
        return response;
      })
      .catch(function() {
        // 네트워크 실패 시 캐시에서 가져오기
        return caches.match(event.request);
      })
  );
});

console.log('TestPark Service Worker 로드됨 (v1.1 - 자동 새로고침 방지)');
