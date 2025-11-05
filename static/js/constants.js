/**
 * TestPark 전역 JavaScript 상수
 * 모든 앱에서 공통으로 사용하는 상수 정의
 */

(function() {
    'use strict';

    /**
     * 전역 상수 네임스페이스
     */
    window.TestParkConstants = {
        // 상태 관련
        OrderStatus: {
            WAITING: '대기중',
            ASSIGNED: '할당',
            REJECTED: '반려',
            CANCELLED: '취소',
            EXCLUDED: '제외',
            CONTRACTED: '계약',
            COMPANY_INSUFFICIENT: '업체미비',
            DUPLICATE: '중복접수',
            CONTACT_ERROR: '연락처오류',
            INQUIRY_AVAILABLE: '가능문의',
            INQUIRY_UNAVAILABLE: '불가능답변(X)',
            CUSTOMER_INQUIRY: '고객문의'
        },

        CompanyStatus: {
            ACTIVE: '활성',
            INACTIVE: '비활성',
            SUSPENDED: '정지'
        },

        DesignationType: {
            NONE: '지정없음',
            DIRECT: '지정',
            GROUP_PURCHASE: '공동구매'
        },

        // UI 배지 타입
        BadgeType: {
            PRIMARY: 'primary',
            SECONDARY: 'secondary',
            SUCCESS: 'success',
            DANGER: 'danger',
            WARNING: 'warning',
            INFO: 'info',
            LIGHT: 'light',
            DARK: 'dark'
        },

        // 상태별 배지 매핑
        StatusBadgeMap: {
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
        },

        // 페이지네이션 설정
        Pagination: {
            DEFAULT_PAGE_SIZE: 20,
            MAX_PAGE_SIZE: 100,
            PAGE_SIZE_OPTIONS: [10, 20, 50, 100]
        },

        // 날짜/시간 형식
        DateFormats: {
            DATE: 'YYYY-MM-DD',
            DATETIME: 'YYYY-MM-DD HH:mm',
            DATETIME_FULL: 'YYYY-MM-DD HH:mm:ss',
            TIME: 'HH:mm'
        },

        // API 설정
        ApiSettings: {
            VERSION: 'v1',
            TIMEOUT: 30000,  // milliseconds
            MAX_RETRIES: 3
        },

        // 파일 업로드 설정
        UploadSettings: {
            MAX_FILE_SIZE: 10 * 1024 * 1024,  // 10MB
            ALLOWED_EXTENSIONS: ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx'],
            UPLOAD_PATH: 'uploads/'
        },

        // 긴급성 임계값 (일)
        URGENCY_THRESHOLD_DAYS: 3,

        // HTTP 메서드
        HttpMethods: {
            GET: 'GET',
            POST: 'POST',
            PUT: 'PUT',
            PATCH: 'PATCH',
            DELETE: 'DELETE'
        },

        // 로컬 스토리지 키
        StorageKeys: {
            USER_PREFERENCES: 'testpark_user_preferences',
            LAST_SEARCH: 'testpark_last_search',
            THEME: 'testpark_theme'
        }
    };

    // 짧은 별칭
    window.TPC = window.TestParkConstants;

    console.log('✅ TestPark 상수가 로드되었습니다.');

})();
