/**
 * TestPark 메인 애플리케이션
 * 전역 네임스페이스 및 앱 관리
 *
 * 의존성: constants.js, utils.js
 */

(function() {
    'use strict';

    // 의존성 체크
    if (!window.TestParkConstants) {
        console.error('TestParkConstants가 로드되지 않았습니다. constants.js를 먼저 로드하세요.');
        return;
    }

    /**
     * TestPark 전역 네임스페이스
     * 모든 앱의 함수가 여기에 등록됩니다
     */
    window.TestPark = {
        // 버전 정보
        version: '1.1.0',

        // 상수 참조 (편의성)
        constants: window.TestParkConstants,

        // 공통 유틸리티 (기존 함수들과 호환)
        utils: {
            getCookie: function(name) {
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

            formatDate: function(dateString, format = 'YYYY-MM-DD') {
                if (!dateString) return '-';
                const date = new Date(dateString);

                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const hours = String(date.getHours()).padStart(2, '0');
                const minutes = String(date.getMinutes()).padStart(2, '0');

                switch (format) {
                    case 'YYYY-MM-DD':
                        return `${year}-${month}-${day}`;
                    case 'YYYY-MM-DD HH:mm':
                        return `${year}-${month}-${day} ${hours}:${minutes}`;
                    case 'localeString':
                        return date.toLocaleString('ko-KR');
                    default:
                        return date.toLocaleDateString('ko-KR');
                }
            },

            formatPhone: function(phone) {
                if (!phone) return '-';
                return phone.replace(/(\d{3})(\d{4})(\d{4})/, '$1-$2-$3');
            },

            isUrgent: function(scheduledDate, daysThreshold = 3) {
                if (!scheduledDate) return false;
                const today = new Date();
                const schedule = new Date(scheduledDate);
                const diffTime = schedule.getTime() - today.getTime();
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                return diffDays <= daysThreshold && diffDays >= 0;
            }
        },

        // API 관련 함수
        api: {
            call: async function(url, method = 'GET', data = null) {
                // api-helpers.js의 함수 사용 (있으면)
                if (window.apiRequest) {
                    const options = { method };
                    if (data && method !== 'GET') {
                        options.body = JSON.stringify(data);
                    }
                    return window.apiRequest(url, options);
                }

                // 폴백: 직접 구현
                const options = {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': TestPark.utils.getCookie('csrftoken')
                    }
                };

                if (method !== 'GET' && data) {
                    options.body = JSON.stringify(data);
                }

                try {
                    const response = await fetch(url, options);
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    return await response.json();
                } catch (error) {
                    console.error('API 호출 오류:', error);
                    throw error;
                }
            }
        },

        // UI 관련 함수
        ui: {
            toast: function(message, type = 'info') {
                // window.Toast가 있으면 사용 (order 앱의 Toast)
                if (window.Toast) {
                    switch (type) {
                        case 'success': window.Toast.success(message); break;
                        case 'error': window.Toast.error(message); break;
                        case 'warning': window.Toast.warning(message); break;
                        default: window.Toast.info(message);
                    }
                    return;
                }

                // window.showNotification이 있으면 사용 (api-helpers.js)
                if (window.showNotification) {
                    window.showNotification(message, type);
                    return;
                }

                // 폴백: alert
                alert(message);
            },

            confirm: function(message) {
                return window.confirmAction ? window.confirmAction(message) : confirm(message);
            },

            loading: {
                show: function(text = '로딩 중...') {
                    if (window.loadingManager) {
                        window.loadingManager.show(text);
                    }
                },
                hide: function() {
                    if (window.loadingManager) {
                        window.loadingManager.hide();
                    }
                }
            },

            getStatusBadge: function(status) {
                const statusMap = {
                    '대기중': 'warning',
                    '할당': 'success',
                    '반려': 'danger',
                    '취소': 'secondary',
                    '제외': 'dark',
                    '계약': 'success',
                    '업체미비': 'info',
                    '중복접수': 'warning',
                    '연락처오류': 'danger',
                    '가능문의': 'info',
                    '불가능답변(X)': 'secondary',
                    '고객문의': 'info'
                };

                const badgeType = statusMap[status] || 'info';
                return `<span class="info-badge ${badgeType}">${status || '대기중'}</span>`;
            }
        },

        // 앱별 네임스페이스
        // 각 앱은 여기에 자신의 함수들을 등록합니다
        apps: {
            // Order 앱
            order: {
                actions: {},
                utils: {}
            },

            // Company 앱
            company: {
                actions: {},
                utils: {}
            },

            // 다른 앱들도 여기에 추가...
        },

        /**
         * 앱 등록 헬퍼 함수
         * @param {string} appName - 앱 이름
         * @param {object} functions - 등록할 함수들
         */
        registerApp: function(appName, functions) {
            if (!this.apps[appName]) {
                this.apps[appName] = { actions: {}, utils: {} };
            }

            Object.assign(this.apps[appName], functions);
            console.log(`✅ ${appName} 앱이 등록되었습니다.`);
        },

        /**
         * 전역 함수로 노출 (하위 호환성)
         * @param {string} appName - 앱 이름
         * @param {string} namespace - 'actions' 또는 'utils'
         */
        exposeGlobal: function(appName, namespace = 'actions') {
            const app = this.apps[appName];
            if (!app || !app[namespace]) {
                console.warn(`${appName}.${namespace}를 찾을 수 없습니다.`);
                return;
            }

            Object.keys(app[namespace]).forEach(key => {
                if (typeof app[namespace][key] === 'function') {
                    window[key] = app[namespace][key];
                }
            });

            console.log(`✅ ${appName}.${namespace}가 전역으로 노출되었습니다.`);
        }
    };

    // 하위 호환성: 기존 코드가 사용하는 별칭들
    window.App = window.TestPark;

    console.log('🚀 TestPark 전역 애플리케이션 관리자가 초기화되었습니다.');

})();
