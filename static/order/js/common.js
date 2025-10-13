/**
 * 공통 유틸리티 함수
 * Order 관리 시스템에서 사용하는 공통 기능
 */

// CSRF 토큰 가져오기
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

// API 호출 헬퍼 함수 (하위 호환성 유지)
async function apiCall(url, method = 'GET', data = null) {
    // ApiConfig가 있으면 사용, 없으면 기존 방식
    if (window.ApiConfig && window.ApiConfig.request) {
        return window.ApiConfig.request(url, method, data);
    }

    // 폴백: 기존 방식
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (method !== 'GET' && data) {
        options.headers['X-CSRFToken'] = getCookie('csrftoken');
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error('API 호출 오류:', error);
        throw error;
    }
}

// 날짜 포맷 함수
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR');
}

// 전화번호 포맷 함수
function formatPhone(phone) {
    if (!phone) return '-';
    return phone.replace(/(\d{3})(\d{4})(\d{4})/, '$1-$2-$3');
}

// 상태 배지 HTML 생성
function getStatusBadgeHtml(status) {
    const statusMap = {
        '대기중': 'info',
        '할당': 'success',
        '반려': 'danger',
        '취소': 'warning',
        '계약': 'success',
        '연락처오류': 'danger',
        '제외': 'warning'
    };

    const badgeType = statusMap[status] || 'info';
    return `<span class="info-badge ${badgeType}">${status || '대기중'}</span>`;
}

// 전역 객체로 노출 (다른 모듈에서 사용 가능)
window.OrderUtils = {
    getCookie,
    apiCall,
    formatDate,
    formatPhone,
    getStatusBadgeHtml
};
