// 모달 관리 훅

import { useState, useCallback } from 'react';

export const useModal = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [data, setData] = useState<any>(null);

  const open = useCallback((modalData?: any) => {
    setData(modalData);
    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
    // 애니메이션을 위해 데이터는 나중에 지움
    setTimeout(() => {
      setData(null);
    }, 300);
  }, []);

  const toggle = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);

  return {
    isOpen,
    data,
    open,
    close,
    toggle,
    setData
  };
};

// 여러 모달을 관리하는 훅
export const useModals = () => {
  const [modals, setModals] = useState<Record<string, boolean>>({});
  const [modalData, setModalData] = useState<Record<string, any>>({});

  const openModal = useCallback((modalName: string, data?: any) => {
    setModals(prev => ({ ...prev, [modalName]: true }));
    if (data) {
      setModalData(prev => ({ ...prev, [modalName]: data }));
    }
  }, []);

  const closeModal = useCallback((modalName: string) => {
    setModals(prev => ({ ...prev, [modalName]: false }));
    // 애니메이션을 위해 데이터는 나중에 지움
    setTimeout(() => {
      setModalData(prev => {
        const newData = { ...prev };
        delete newData[modalName];
        return newData;
      });
    }, 300);
  }, []);

  const toggleModal = useCallback((modalName: string) => {
    setModals(prev => ({ ...prev, [modalName]: !prev[modalName] }));
  }, []);

  const isModalOpen = useCallback((modalName: string) => {
    return modals[modalName] || false;
  }, [modals]);

  const getModalData = useCallback((modalName: string) => {
    return modalData[modalName];
  }, [modalData]);

  return {
    modals,
    modalData,
    openModal,
    closeModal,
    toggleModal,
    isModalOpen,
    getModalData,
    setModalData
  };
};