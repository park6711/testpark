/**
 * 공통 API 헬퍼 함수들
 * TestPark 프로젝트의 모든 앱에서 사용할 수 있는 API 유틸리티
 */

// CSRF 토큰 설정
window.getCSRFToken = function() {
    return window.csrfToken || document.querySelector('[name=csrfmiddlewaretoken]')?.value;
};

// 기본 API 요청 함수
window.apiRequest = async function(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.getCSRFToken(),
        },
        credentials: 'same-origin'
    };

    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };

    try {
        const response = await fetch(url, mergedOptions);

        if (!response.ok) {
            const errorText = await response.text();
            let errorData;
            try {
                errorData = JSON.parse(errorText);
            } catch {
                errorData = { error: errorText || `HTTP ${response.status}` };
            }
            throw new Error(errorData.error || `API 요청 실패: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API 요청 오류:', error);
        throw error;
    }
};

// 페이지네이션이 있는 목록 API 요청
window.apiListRequest = async function(baseUrl, filters = {}, page = 1, pageSize = 20) {
    const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        ...filters
    });

    return await window.apiRequest(`${baseUrl}?${params}`);
};

// CRUD 작업을 위한 API 헬퍼들
window.apiCRUD = {
    // 생성
    create: async function(url, data) {
        return await window.apiRequest(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    // 조회
    read: async function(url) {
        return await window.apiRequest(url);
    },

    // 수정
    update: async function(url, data) {
        return await window.apiRequest(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    // 부분 수정
    patch: async function(url, data) {
        return await window.apiRequest(url, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    },

    // 삭제
    delete: async function(url) {
        return await window.apiRequest(url, {
            method: 'DELETE'
        });
    },

    // 일괄 삭제
    bulkDelete: async function(url, ids) {
        return await window.apiRequest(url, {
            method: 'POST',
            body: JSON.stringify({ ids: ids })
        });
    }
};

// 알림 및 확인 헬퍼
window.showNotification = function(message, type = 'info') {
    // Bootstrap 기반 알림 (Toast 또는 Alert)
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    // 5초 후 자동 제거
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
};

window.confirmAction = function(message) {
    return window.confirm(message);
};

// 로딩 상태 관리
window.loadingManager = {
    show: function(text = '로딩 중...') {
        let loader = document.getElementById('global-loader');
        if (!loader) {
            loader = document.createElement('div');
            loader.id = 'global-loader';
            loader.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center';
            loader.style.cssText = 'background: rgba(0,0,0,0.5); z-index: 9999;';
            loader.innerHTML = `
                <div class="bg-white p-4 rounded shadow text-center">
                    <div class="spinner-border text-primary mb-2" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <div>${text}</div>
                </div>
            `;
            document.body.appendChild(loader);
        }
        loader.style.display = 'flex';
    },

    hide: function() {
        const loader = document.getElementById('global-loader');
        if (loader) {
            loader.style.display = 'none';
        }
    }
};

// 날짜 포맷팅 헬퍼
window.formatDate = function(date, format = 'YYYY-MM-DD') {
    if (!date) return '';
    const d = new Date(date);

    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');

    switch (format) {
        case 'YYYY-MM-DD':
            return `${year}-${month}-${day}`;
        case 'YYYY-MM-DD HH:mm':
            return `${year}-${month}-${day} ${hours}:${minutes}`;
        case 'MM/DD':
            return `${month}/${day}`;
        case 'localeString':
            return d.toLocaleString('ko-KR');
        default:
            return d.toLocaleDateString('ko-KR');
    }
};

// 긴급성 체크 헬퍼 (3일 이내)
window.isUrgent = function(scheduledDate) {
    if (!scheduledDate) return false;
    const today = new Date();
    const schedule = new Date(scheduledDate);
    const diffTime = schedule.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays <= 3 && diffDays >= 0;
};

// 상태별 배지 클래스 반환
window.getStatusBadgeClass = function(status) {
    const statusClasses = {
        '대기중': 'bg-warning text-dark',
        '할당': 'bg-primary text-white',
        '반려': 'bg-danger text-white',
        '취소': 'bg-secondary text-white',
        '제외': 'bg-dark text-white',
        '업체미비': 'bg-info text-white',
        '중복접수': 'bg-warning text-dark',
        '연락처오류': 'bg-warning text-dark',
        '가능문의': 'bg-success text-white',
        '불가능답변(X)': 'bg-secondary text-white',
        '고객문의': 'bg-info text-white',
        '계약': 'bg-success text-white',
        '활성': 'bg-success text-white',
        '비활성': 'bg-secondary text-white',
        '승인': 'bg-primary text-white',
        '거부': 'bg-danger text-white',
        '대기': 'bg-warning text-dark'
    };
    return statusClasses[status] || 'bg-secondary text-white';
};

console.log('TestPark API 헬퍼 라이브러리가 로드되었습니다.');