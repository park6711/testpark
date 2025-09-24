// 의뢰(Order) 관련 타입 정의

// 의뢰 상태 타입
export type OrderStatus =
  | '대기중'
  | '할당'
  | '반려'
  | '취소'
  | '제외'
  | '업체미비'
  | '중복접수'
  | '연락처오류'
  | '가능문의'
  | '불가능답변(X)'
  | '고객문의'
  | '계약';

// 지정 타입
export type DesignationType =
  | '지정없음'
  | '업체지정'
  | '지역지정'
  | '우선지정';

// 의뢰 인터페이스
export interface Order {
  no: number;
  id?: number;
  time: string;
  designation?: string;
  designation_type?: DesignationType;
  sNick?: string;
  sNaverID?: string;
  sName?: string;
  sPhone?: string;
  post_link?: string;
  sPost?: string;
  sArea?: string;
  dateSchedule?: string;
  sConstruction?: string;
  assigned_company?: string;
  recent_status: OrderStatus;
  re_request_count?: number;
  created_at?: string;
  updated_at?: string;
  memo_count?: number;
  quote_count?: number;
  messages?: OrderMessage[];
  quotes?: OrderQuote[];
  memos?: OrderMemo[];
}

// 메모 인터페이스
export interface OrderMemo {
  id: number;
  content: string;
  author: string;
  created_at: string;
}

// 견적서 인터페이스
export interface OrderQuote {
  id: number;
  draft_type: '초안' | '1차' | '2차' | '3차' | '최종';
  link: string;
  created_at: string;
}

// 메시지 인터페이스
export interface OrderMessage {
  id: number;
  content: string;
  recipient: '업체' | '고객' | '업체+고객';
  sent_at: string;
  status: 'sent' | 'delivered' | 'failed';
}

// 업체 인터페이스
export interface Company {
  id: number;
  name: string;
  contact?: string;
  area?: string[];
  is_active: boolean;
  capacity?: number;
  current_orders?: number;
}

// 필터 인터페이스
export interface OrderFilters {
  status?: OrderStatus;
  search?: string;
  dateRange?: [string, string];
  area?: string;
  designation_type?: DesignationType;
  assigned_company?: string;
}

// API 응답 인터페이스
export interface OrdersResponse {
  results: Order[];
  count: number;
  next?: string;
  previous?: string;
}

// 상태 변경 요청 인터페이스
export interface UpdateStatusRequest {
  status: OrderStatus;
  message_sent?: boolean;
  recipient?: '업체' | '고객' | '업체+고객';
  message_content?: string;
  author?: string;
}

// 필드 업데이트 요청 인터페이스
export interface UpdateFieldRequest {
  field_name: string;
  field_label: string;
  new_value: any;
  author?: string;
}

// 통계 인터페이스
export interface OrderStatistics {
  total: number;
  byStatus: Record<OrderStatus, number>;
  byArea: Record<string, number>;
  byDate: {
    today: number;
    thisWeek: number;
    thisMonth: number;
  };
  conversionRate: number;
  averageResponseTime: number;
}