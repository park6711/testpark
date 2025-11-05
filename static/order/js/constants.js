/**
 * Order 앱 전용 JavaScript 상수
 */

(function() {
    'use strict';

    window.OrderConstants = {
        // 할당 상태
        AssignStatus: {
            PENDING: '대기',
            SENT: '발송',
            VIEWED: '확인',
            RESPONDED: '응답',
            ACCEPTED: '수락',
            REJECTED: '거절'
        },

        // Order 설정
        Settings: {
            AUTO_ASSIGN_ENABLED: true,
            MAX_ASSIGN_COMPANIES: 10,
            ASSIGN_TIMEOUT_HOURS: 24,
            REMINDER_INTERVAL_HOURS: 6
        },

        // 견적서 설정
        EstimateSettings: {
            MAX_ESTIMATES_PER_ORDER: 20,
            ESTIMATE_VALID_DAYS: 30
        },

        // API 엔드포인트 (api-config.js와 중복 제거 예정)
        ApiEndpoints: {
            BASE: '/order/api',
            ORDERS: '/order/api/orders/',
            COMPANIES: '/order/api/companies/',
            ESTIMATES: '/order/api/estimates/',
            MEMOS: '/order/api/memos/',
            GROUP_PURCHASES: '/order/api/group-purchases/'
        }
    };

    console.log('✅ Order 상수가 로드되었습니다.');

})();
