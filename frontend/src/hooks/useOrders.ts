// 의뢰 관리 훅

import { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';
import { OrderData, FilterOptions, SortOptions } from '../types';

export const useOrders = () => {
  const [orders, setOrders] = useState<OrderData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterOptions>({});
  const [sortOptions, setSortOptions] = useState<SortOptions>({
    field: 'no',
    order: 'desc'
  });

  // 의뢰 목록 가져오기
  const fetchOrders = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.fetchOrders();
      setOrders(data);
    } catch (err) {
      setError('의뢰 목록을 불러오는데 실패했습니다.');
      console.error('Error fetching orders:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // 의뢰 삭제
  const deleteOrders = useCallback(async (orderIds: number[]) => {
    try {
      await apiService.deleteOrders(orderIds);
      await fetchOrders(); // 목록 새로고침
      return { success: true };
    } catch (err) {
      console.error('Error deleting orders:', err);
      return { success: false, error: '삭제 중 오류가 발생했습니다.' };
    }
  }, [fetchOrders]);

  // 의뢰 상태 업데이트
  const updateOrderStatus = useCallback(async (
    orderId: number,
    status: string,
    messageData?: any
  ) => {
    try {
      await apiService.updateOrderStatus(orderId, status, messageData);
      await fetchOrders(); // 목록 새로고침
      return { success: true };
    } catch (err) {
      console.error('Error updating order status:', err);
      return { success: false, error: '상태 업데이트 중 오류가 발생했습니다.' };
    }
  }, [fetchOrders]);

  // 의뢰 필드 업데이트
  const updateOrderField = useCallback(async (
    orderId: number,
    fieldName: string,
    fieldLabel: string,
    newValue: any
  ) => {
    try {
      await apiService.updateOrderField(orderId, fieldName, fieldLabel, newValue);
      await fetchOrders(); // 목록 새로고침
      return { success: true };
    } catch (err) {
      console.error('Error updating order field:', err);
      return { success: false, error: '필드 업데이트 중 오류가 발생했습니다.' };
    }
  }, [fetchOrders]);

  // 메모 추가
  const addMemo = useCallback(async (orderId: number, content: string) => {
    try {
      await apiService.addMemo(orderId, content);
      await fetchOrders(); // 목록 새로고침
      return { success: true };
    } catch (err) {
      console.error('Error adding memo:', err);
      return { success: false, error: '메모 추가 중 오류가 발생했습니다.' };
    }
  }, [fetchOrders]);

  // 견적 링크 추가
  const addQuoteLink = useCallback(async (
    orderId: number,
    draftType: string,
    link: string
  ) => {
    try {
      await apiService.addQuoteLink(orderId, draftType, link);
      await fetchOrders(); // 목록 새로고침
      return { success: true };
    } catch (err) {
      console.error('Error adding quote link:', err);
      return { success: false, error: '견적 링크 추가 중 오류가 발생했습니다.' };
    }
  }, [fetchOrders]);

  // 필터링된 의뢰 목록 계산
  const getFilteredOrders = useCallback(() => {
    let filtered = [...orders];

    // 필터 적용
    if (filters.status) {
      filtered = filtered.filter(order => order.recent_status === filters.status);
    }
    if (filters.area) {
      filtered = filtered.filter(order => order.sArea === filters.area);
    }
    if (filters.company) {
      filtered = filtered.filter(order => order.assigned_company === filters.company);
    }
    if (filters.searchText) {
      const searchLower = filters.searchText.toLowerCase();
      const searchText = filters.searchText;
      filtered = filtered.filter(order =>
        order.sName.toLowerCase().includes(searchLower) ||
        order.sNick.toLowerCase().includes(searchLower) ||
        order.sPhone.includes(searchText) ||
        order.sNaverID.toLowerCase().includes(searchLower)
      );
    }

    // 정렬 적용
    filtered.sort((a, b) => {
      const aValue = a[sortOptions.field as keyof OrderData];
      const bValue = b[sortOptions.field as keyof OrderData];

      if (aValue === undefined || bValue === undefined) return 0;

      const comparison = aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      return sortOptions.order === 'asc' ? comparison : -comparison;
    });

    return filtered;
  }, [orders, filters, sortOptions]);

  // 초기 데이터 로드
  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  return {
    orders: getFilteredOrders(),
    loading,
    error,
    filters,
    setFilters,
    sortOptions,
    setSortOptions,
    actions: {
      fetchOrders,
      deleteOrders,
      updateOrderStatus,
      updateOrderField,
      addMemo,
      addQuoteLink
    }
  };
};