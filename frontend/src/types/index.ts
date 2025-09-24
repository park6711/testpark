// 의뢰 관련 타입 정의

// 회사 정보
export interface CompanyData {
  id: number;
  name: string;
  area?: string;
  contact?: string;
  email?: string;
  isActive?: boolean;
}

// 서비스 정보
export interface ServiceData {
  id: number;
  name: string;
  description?: string;
  price?: number;
  category?: string;
}

// 의뢰 데이터 (백엔드와 일치)
export interface OrderData {
  no: number;
  time: string;
  designation: string;
  designation_type: string;
  sNick: string;
  sNaverID: string;
  sName: string;
  sPhone: string;
  sPost?: string;  // 의뢰게시글
  post_link: string;
  sArea: string;
  dateSchedule?: string;
  sConstruction: string;
  assigned_company: string;
  recent_status: string;
  re_request_count: number;
  bPrivacy1: boolean;
  bPrivacy2: boolean;
  created_at: string;
  updated_at: string;
  google_sheet_uuid?: string;
  quote_links?: string[];  // 열린견적서 링크들
}

// 프론트엔드용 의뢰 데이터 (표시용)
export interface QuoteRequestData {
  id: number;
  receiptDate: string;
  designation: string;
  designationType: string;
  nickname: string;
  naverId: string;
  name: string;
  phone: string;
  postLink: string;
  area: string;
  scheduledDate?: string;
  workContent: string;
  assignedCompany: string;
  recentStatus: string;
  reRequestCount: number;
  quoteCount: number;
  memoCount: number;
}

// 모달 관련 타입
export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
}

// 메모 타입
export interface MemoData {
  id: number;
  content: string;
  author: string;
  created_at: string;
  order: number;
}

// 메시지 템플릿 타입
export type MessageTemplate = '템플릿1' | '템플릿2' | '템플릿3' | '커스텀';
export type MessageRecipient = '업체' | '고객' | '업체+고객';

// 상태 옵션 타입
export interface StatusOption {
  value: string;
  label: string;
  color: string;
}

// API 응답 타입
export interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// 필터 타입
export interface FilterOptions {
  status?: string;
  area?: string;
  company?: string;
  dateFrom?: string;
  dateTo?: string;
  searchText?: string;
}

// 정렬 타입
export type SortField = 'no' | 'time' | 'sArea' | 'recent_status' | 'assigned_company';
export type SortOrder = 'asc' | 'desc';

export interface SortOptions {
  field: SortField;
  order: SortOrder;
}