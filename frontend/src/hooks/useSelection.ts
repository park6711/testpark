// 선택 관리 훅

import { useState, useCallback } from 'react';

export const useSelection = <T extends { id: number }>() => {
  const [selectedItems, setSelectedItems] = useState<number[]>([]);

  const selectItem = useCallback((id: number) => {
    setSelectedItems(prev => [...prev, id]);
  }, []);

  const deselectItem = useCallback((id: number) => {
    setSelectedItems(prev => prev.filter(itemId => itemId !== id));
  }, []);

  const toggleItem = useCallback((id: number) => {
    setSelectedItems(prev =>
      prev.includes(id)
        ? prev.filter(itemId => itemId !== id)
        : [...prev, id]
    );
  }, []);

  const selectAll = useCallback((items: T[]) => {
    setSelectedItems(items.map(item => item.id));
  }, []);

  const deselectAll = useCallback(() => {
    setSelectedItems([]);
  }, []);

  const isSelected = useCallback((id: number) => {
    return selectedItems.includes(id);
  }, [selectedItems]);

  const getSelectedItems = useCallback(<T extends { id: number }>(items: T[]): T[] => {
    return items.filter(item => selectedItems.includes(item.id));
  }, [selectedItems]);

  return {
    selectedItems,
    selectItem,
    deselectItem,
    toggleItem,
    selectAll,
    deselectAll,
    isSelected,
    getSelectedItems,
    selectedCount: selectedItems.length
  };
};