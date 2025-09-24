// API 서비스
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface OrderData {
  no: number;
  time: string;
  designation: string;
  designation_type: string;
  sNick: string;
  sNaverID: string;
  sName: string;
  sPhone: string;
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
}

export interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

class ApiService {
  private baseURL = API_BASE_URL;

  async fetchOrders(): Promise<OrderData[]> {
    try {
      const response = await fetch(`${this.baseURL}/order/api/orders/`, {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ApiResponse<OrderData> = await response.json();
      return data.results || [];
    } catch (error) {
      console.error('Error fetching orders:', error);
      throw error;
    }
  }

  async createOrder(orderData: Partial<OrderData>): Promise<OrderData> {
    try {
      const response = await fetch(`${this.baseURL}/order/api/orders/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating order:', error);
      throw error;
    }
  }

  async updateOrderStatus(orderId: number, status: string, messageData?: any): Promise<void> {
    try {
      const response = await fetch(`${this.baseURL}/order/api/orders/${orderId}/update_status/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status,
          ...messageData,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('Error updating order status:', error);
      throw error;
    }
  }

  async updateOrderField(orderId: number, fieldName: string, fieldLabel: string, newValue: any): Promise<void> {
    try {
      const response = await fetch(`${this.baseURL}/order/api/orders/${orderId}/update_field/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          field_name: fieldName,
          field_label: fieldLabel,
          new_value: newValue,
          author: '관리자', // TODO: 실제 로그인 사용자로 변경
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('Error updating order field:', error);
      throw error;
    }
  }

  async addMemo(orderId: number, content: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseURL}/order/api/orders/${orderId}/add_memo/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          author: '관리자', // TODO: 실제 로그인 사용자로 변경
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('Error adding memo:', error);
      throw error;
    }
  }

  async addQuoteLink(orderId: number, draftType: string, link: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseURL}/order/api/orders/${orderId}/add_quote_link/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          draft_type: draftType,
          link,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('Error adding quote link:', error);
      throw error;
    }
  }

  async deleteOrders(orderIds: number[]): Promise<void> {
    try {
      const response = await fetch(`${this.baseURL}/order/api/orders/bulk_delete/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          order_ids: orderIds,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('Error deleting orders:', error);
      throw error;
    }
  }

  async fetchCompanies(): Promise<any[]> {
    try {
      const response = await fetch(`${this.baseURL}/order/api/companies/`, {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching companies:', error);
      throw error;
    }
  }

  async fetchAreas(): Promise<string[]> {
    try {
      const response = await fetch(`${this.baseURL}/order/api/areas/`, {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching areas:', error);
      throw error;
    }
  }
}

export const apiService = new ApiService();