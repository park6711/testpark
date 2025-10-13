/**
 * API 엔드포인트 중앙 관리
 * 모든 API URL을 여기서 관리하여 유지보수성 향상
 */

(function() {
    'use strict';

    // 기본 API 베이스 URL (환경별 설정 가능)
    const API_BASE_URL = '/order/api';

    /**
     * API 엔드포인트 목록
     */
    const API_ENDPOINTS = {
        // 의뢰(Order) 관련 API
        orders: {
            list: `${API_BASE_URL}/orders/`,
            detail: (orderNo) => `${API_BASE_URL}/orders/${orderNo}/`,
            copy: (orderNo) => `${API_BASE_URL}/orders/${orderNo}/copy/`,
            addMemo: (orderNo) => `${API_BASE_URL}/orders/${orderNo}/add_memo/`,
            assignCompanies: `${API_BASE_URL}/orders/assign_companies/`,
            postWithToken: `${API_BASE_URL}/orders/post-with-token/`
        },

        // 업체(Company) 관련 API
        companies: {
            list: `${API_BASE_URL}/companies/`,
            detail: (companyNo) => `${API_BASE_URL}/companies/${companyNo}/`,
        },

        // 공동구매(Group Purchase) 관련 API
        groupPurchases: {
            list: `${API_BASE_URL}/group-purchases/`,
            detail: (gpNo) => `${API_BASE_URL}/group-purchases/${gpNo}/`,
        },

        // 견적(Estimate) 관련 API
        estimates: {
            list: `${API_BASE_URL}/estimates/`,
            detail: (estimateNo) => `${API_BASE_URL}/estimates/${estimateNo}/`,
        },

        // 메모(Memo) 관련 API
        memos: {
            list: `${API_BASE_URL}/memos/`,
            detail: (memoNo) => `${API_BASE_URL}/memos/${memoNo}/`,
        }
    };

    /**
     * API 호출 헬퍼 함수
     * @param {string} url - API 엔드포인트 URL
     * @param {string} method - HTTP 메서드 (GET, POST, PUT, DELETE 등)
     * @param {Object|null} data - 요청 데이터 (body)
     * @param {Object} options - 추가 옵션
     * @returns {Promise} API 응답 Promise
     */
    async function apiRequest(url, method = 'GET', data = null, options = {}) {
        const requestOptions = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        // GET이 아니고 데이터가 있으면 CSRF 토큰과 body 추가
        if (method !== 'GET' && data) {
            requestOptions.headers['X-CSRFToken'] = getCookie('csrftoken');
            requestOptions.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, requestOptions);

            // 응답이 JSON인 경우
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const jsonData = await response.json();

                // HTTP 에러 상태 체크
                if (!response.ok) {
                    throw new Error(jsonData.message || `HTTP ${response.status}: ${response.statusText}`);
                }

                return jsonData;
            }

            // JSON이 아닌 경우 텍스트로 반환
            return await response.text();

        } catch (error) {
            console.error('API 호출 오류:', error);
            throw error;
        }
    }

    /**
     * CSRF 토큰 가져오기
     */
    function getCookie(name) {
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
    }

    // 전역 객체로 노출
    window.ApiConfig = {
        endpoints: API_ENDPOINTS,
        request: apiRequest,
        baseUrl: API_BASE_URL
    };

})();
