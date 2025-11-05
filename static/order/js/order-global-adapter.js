/**
 * Order 앱 전역 어댑터
 * Order 앱의 함수들을 TestPark 전역 네임스페이스에 등록
 */

(function() {
    'use strict';

    // TestPark이 로드되지 않은 경우 대기
    if (!window.TestPark) {
        console.error('TestPark 전역 객체가 로드되지 않았습니다. global-app.js를 먼저 로드하세요.');
        return;
    }

    // Order 앱의 유틸리티 함수들을 TestPark에 등록
    window.TestPark.registerApp('order', {
        utils: {
            getCookie: window.OrderUtils?.getCookie || window.TestPark.utils.getCookie,
            apiCall: window.OrderUtils?.apiCall || window.TestPark.api.call,
            formatDate: window.OrderUtils?.formatDate || window.TestPark.utils.formatDate,
            formatPhone: window.OrderUtils?.formatPhone || window.TestPark.utils.formatPhone,
            getStatusBadgeHtml: window.OrderUtils?.getStatusBadgeHtml || window.TestPark.ui.getStatusBadge
        },
        actions: {
            // 이 함수들은 각 모듈(order-list.js, order-assign.js 등)에서 등록됩니다
            // 여기서는 빈 객체로 초기화만 합니다
        }
    });

    // 하위 호환성: window.OrderUtils 유지
    if (!window.OrderUtils) {
        window.OrderUtils = window.TestPark.apps.order.utils;
    }

    console.log('✅ Order 앱이 TestPark 전역 네임스페이스에 등록되었습니다.');

})();
