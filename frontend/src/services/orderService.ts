// 의뢰 관련 API 서비스

import axios, { AxiosInstance } from 'axios';
import {
  Order,
  OrdersResponse,
  OrderFilters,
  UpdateStatusRequest,
  UpdateFieldRequest,
  Company,
  OrderMemo,
  OrderQuote,
  OrderStatistics
} from '../types/order.types';

// API 인스턴스 설정
class OrderService {
  private api: AxiosInstance;

  constructor() {
    // Django 컨텍스트에서 API 설정 가져오기
    const djangoContext = (window as any).__DJANGO_CONTEXT__ || {};

    // 환경 변수 또는 Django 컨텍스트에서 API URL 가져오기
    let baseURL = djangoContext.apiBaseUrl || process.env.REACT_APP_API_URL || '';

    // API 경로 추가
    baseURL = baseURL + '/order/api';

    this.api = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': djangoContext.csrfToken || ''
      },
      withCredentials: true
    });

    // 요청 인터셉터
    this.api.interceptors.request.use(
      (config) => {
        // 로딩 상태 처리 등
        console.log('API Request:', config.method?.toUpperCase(), config.url);
        return config;
      },
      (error) => {
        console.error('Request Error:', error);
        return Promise.reject(error);
      }
    );

    // 응답 인터셉터
    this.api.interceptors.response.use(
      (response) => {
        return response;
      },
      (error) => {
        this.handleError(error);
        return Promise.reject(error);
      }
    );
  }

  // 에러 핸들링
  private handleError(error: any): void {
    if (error.response) {
      const { status, data } = error.response;
      const message = data?.message || data?.detail || '오류가 발생했습니다.';

      switch (status) {
        case 400:
          console.error('잘못된 요청:', message);
          break;
        case 401:
          console.error('인증 필요');
          // 로그인 페이지로 리다이렉트
          window.location.href = '/accounts/login/';
          break;
        case 403:
          console.error('권한 없음:', message);
          break;
        case 404:
          console.error('리소스를 찾을 수 없음:', message);
          break;
        case 500:
          console.error('서버 오류:', message);
          break;
        default:
          console.error('오류:', message);
      }
    } else if (error.request) {
      console.error('네트워크 오류: 서버에 연결할 수 없습니다.');
    } else {
      console.error('오류:', error.message);
    }
  }

  // 의뢰 목록 조회
  async getOrders(filters?: OrderFilters): Promise<OrdersResponse> {
    try {
      const response = await this.api.get<OrdersResponse>('/orders/', {
        params: filters
      });
      return response.data;
    } catch (error) {
      console.error('의뢰 목록 조회 실패:', error);
      throw error;
    }
  }

  // 단일 의뢰 조회
  async getOrder(id: number): Promise<Order> {
    try {
      const response = await this.api.get<Order>(`/orders/${id}/`);
      return response.data;
    } catch (error) {
      console.error('의뢰 조회 실패:', error);
      throw error;
    }
  }

  // 의뢰 생성
  async createOrder(order: Partial<Order>): Promise<Order> {
    try {
      const response = await this.api.post<Order>('/orders/', order);
      return response.data;
    } catch (error) {
      console.error('의뢰 생성 실패:', error);
      throw error;
    }
  }

  // 의뢰 상태 업데이트
  async updateStatus(id: number, data: UpdateStatusRequest): Promise<Order> {
    try {
      const response = await this.api.post<Order>(
        `/orders/${id}/update_status/`,
        data
      );
      return response.data;
    } catch (error) {
      console.error('상태 업데이트 실패:', error);
      throw error;
    }
  }

  // 의뢰 필드 업데이트
  async updateField(id: number, data: UpdateFieldRequest): Promise<Order> {
    try {
      const response = await this.api.post<Order>(
        `/orders/${id}/update_field/`,
        data
      );
      return response.data;
    } catch (error) {
      console.error('필드 업데이트 실패:', error);
      throw error;
    }
  }

  // 메모 추가
  async addMemo(id: number, content: string, author?: string): Promise<OrderMemo> {
    try {
      const response = await this.api.post<OrderMemo>(
        `/orders/${id}/add_memo/`,
        { content, author: author || '관리자' }
      );
      return response.data;
    } catch (error) {
      console.error('메모 추가 실패:', error);
      throw error;
    }
  }

  // 견적서 링크 추가
  async addQuoteLink(
    id: number,
    link: string,
    draftType: string = '초안'
  ): Promise<OrderQuote> {
    try {
      const response = await this.api.post<OrderQuote>(
        `/orders/${id}/add_quote_link/`,
        { link, draft_type: draftType }
      );
      return response.data;
    } catch (error) {
      console.error('견적서 링크 추가 실패:', error);
      throw error;
    }
  }

  // 의뢰 복사
  async copyOrder(id: number): Promise<Order> {
    try {
      const response = await this.api.post<Order>(`/orders/${id}/copy/`);
      return response.data;
    } catch (error) {
      console.error('의뢰 복사 실패:', error);
      throw error;
    }
  }

  // 의뢰 삭제
  async deleteOrder(id: number): Promise<void> {
    try {
      await this.api.delete(`/orders/${id}/`);
    } catch (error) {
      console.error('의뢰 삭제 실패:', error);
      throw error;
    }
  }

  // 대량 삭제
  async bulkDelete(ids: number[]): Promise<void> {
    try {
      await this.api.post('/orders/bulk_delete/', { order_ids: ids });
    } catch (error) {
      console.error('대량 삭제 실패:', error);
      throw error;
    }
  }

  // 업체 목록 조회
  async getCompanies(): Promise<Company[]> {
    try {
      const response = await this.api.get<Company[]>('/companies/');
      return response.data;
    } catch (error) {
      console.error('업체 목록 조회 실패:', error);
      throw error;
    }
  }

  // 통계 조회
  async getStatistics(dateRange?: [string, string]): Promise<OrderStatistics> {
    try {
      const response = await this.api.get<OrderStatistics>('/statistics/', {
        params: { date_from: dateRange?.[0], date_to: dateRange?.[1] }
      });
      return response.data;
    } catch (error) {
      console.error('통계 조회 실패:', error);
      throw error;
    }
  }

  // Excel 내보내기
  async exportToExcel(filters?: OrderFilters): Promise<Blob> {
    try {
      const response = await this.api.get('/orders/export/', {
        params: filters,
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Excel 내보내기 실패:', error);
      throw error;
    }
  }

  // Google Sheets 동기화
  async syncWithGoogleSheets(): Promise<{ message: string }> {
    try {
      const response = await this.api.post<{ message: string }>(
        '/orders/sync_google_sheets/'
      );
      return response.data;
    } catch (error) {
      console.error('Google Sheets 동기화 실패:', error);
      throw error;
    }
  }
}

// 싱글톤 인스턴스 생성 및 내보내기
export const orderService = new OrderService();

// 기본 내보내기
export default orderService;