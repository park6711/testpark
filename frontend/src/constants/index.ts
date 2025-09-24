// 애플리케이션 상수

// 상태 옵션
export const STATUS_OPTIONS = [
  { value: '접수완료', label: '접수완료', color: '#4CAF50' },
  { value: '업체전달', label: '업체전달', color: '#2196F3' },
  { value: '현장미팅', label: '현장미팅', color: '#FF9800' },
  { value: '견적전달', label: '견적전달', color: '#9C27B0' },
  { value: '계약완료', label: '계약완료', color: '#00BCD4' },
  { value: '시공중', label: '시공중', color: '#FFC107' },
  { value: '완료', label: '완료', color: '#8BC34A' },
  { value: '취소', label: '취소', color: '#F44336' },
  { value: '보류', label: '보류', color: '#9E9E9E' }
];

// 메시지 템플릿
export const MESSAGE_TEMPLATES = {
  '템플릿1': '안녕하세요, {name}님. 문의주신 건에 대해 안내드립니다.',
  '템플릿2': '견적 확인 부탁드립니다. 추가 문의사항이 있으시면 연락주세요.',
  '템플릿3': '시공 일정 조율을 위해 연락드립니다. 가능하신 시간을 알려주세요.',
  '커스텀': ''
};

// 페이지 크기 옵션
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

// 기본 페이지 크기
export const DEFAULT_PAGE_SIZE = 20;

// 날짜 형식
export const DATE_FORMAT = 'YYYY-MM-DD';
export const DATETIME_FORMAT = 'YYYY-MM-DD HH:mm:ss';

// 지역 옵션
export const AREA_OPTIONS = [
  '서울',
  '경기',
  '인천',
  '대전',
  '대구',
  '부산',
  '광주',
  '울산',
  '세종',
  '강원',
  '충북',
  '충남',
  '전북',
  '전남',
  '경북',
  '경남',
  '제주'
];

// 시공 유형
export const CONSTRUCTION_TYPES = [
  '전체시공',
  '부분시공',
  '도배',
  '장판',
  '타일',
  '욕실',
  '주방',
  '인테리어',
  '기타'
];

// API 엔드포인트
export const API_ENDPOINTS = {
  ORDERS: '/order/api/orders/',
  COMPANIES: '/order/api/companies/',
  AREAS: '/order/api/areas/',
  MEMOS: '/order/api/memos/',
  STATUS_UPDATE: '/order/api/orders/{id}/update_status/',
  FIELD_UPDATE: '/order/api/orders/{id}/update_field/',
  ADD_MEMO: '/order/api/orders/{id}/add_memo/',
  ADD_QUOTE: '/order/api/orders/{id}/add_quote_link/',
  BULK_DELETE: '/order/api/orders/bulk_delete/'
};