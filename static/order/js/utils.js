/**
 * Order 앱 전용 JavaScript 유틸리티 함수
 */

(function() {
    'use strict';

    window.OrderUtils = {
        /**
         * 쿠키 가져오기
         */
        getCookie: function(name) {
            // TestPark.utils가 있으면 사용
            if (window.TestPark && window.TestPark.utils.getCookie) {
                return window.TestPark.utils.getCookie(name);
            }

            // 폴백
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },

        /**
         * API 호출
         */
        apiCall: async function(url, method = 'GET', data = null) {
            // TestPark.api가 있으면 사용
            if (window.TestPark && window.TestPark.api.call) {
                return window.TestPark.api.call(url, method, data);
            }

            // 폴백
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            };

            if (method !== 'GET' && data) {
                options.body = JSON.stringify(data);
            }

            try {
                const response = await fetch(url, options);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('API 호출 오류:', error);
                throw error;
            }
        },

        /**
         * 날짜 포맷팅
         */
        formatDate: function(dateString, format = 'YYYY-MM-DD') {
            // TestPark.utils가 있으면 사용
            if (window.TestPark && window.TestPark.utils.formatDate) {
                return window.TestPark.utils.formatDate(dateString, format);
            }

            // 폴백
            if (!dateString) return '-';
            const date = new Date(dateString);
            return date.toLocaleDateString('ko-KR');
        },

        /**
         * 전화번호 포맷팅
         */
        formatPhone: function(phone) {
            if (!phone) return '-';
            return phone.replace(/(\d{3})(\d{4})(\d{4})/, '$1-$2-$3');
        },

        /**
         * 상태 배지 HTML 생성
         */
        getStatusBadgeHtml: function(status) {
            const badgeMap = window.TestParkConstants
                ? window.TestParkConstants.StatusBadgeMap
                : {
                    '대기중': 'warning',
                    '할당': 'success',
                    '반려': 'danger',
                    '취소': 'secondary',
                    '계약': 'success'
                };

            const badgeType = badgeMap[status] || 'info';
            return `<span class="info-badge ${badgeType}">${status || '대기중'}</span>`;
        },

        /**
         * 의뢰 표시 이름 생성
         */
        getOrderDisplayName: function(order) {
            const name = order.sName || '이름없음';
            const area = order.sArea || '지역없음';
            return `${name} - ${area}`;
        }
    };

    console.log('✅ Order 유틸리티가 로드되었습니다.');

})();
