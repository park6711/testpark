// 로딩 폴백 컴포넌트

import React from 'react';
import { Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

interface LoadingFallbackProps {
  tip?: string;
  size?: 'small' | 'default' | 'large';
  height?: string | number;
}

export const LoadingFallback: React.FC<LoadingFallbackProps> = ({
  tip = '페이지를 불러오는 중...',
  size = 'large',
  height = '60vh'
}) => {
  const antIcon = <LoadingOutlined style={{ fontSize: size === 'large' ? 48 : 24 }} spin />;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: height,
        background: 'transparent'
      }}
    >
      <Spin indicator={antIcon} size={size} tip={tip} />
    </div>
  );
};

// 인라인 로딩 컴포넌트
export const InlineLoading: React.FC<{ tip?: string }> = ({ tip = '로딩 중...' }) => (
  <div style={{ textAlign: 'center', padding: '20px' }}>
    <Spin tip={tip} />
  </div>
);

// 전체 화면 로딩 컴포넌트
export const FullPageLoading: React.FC<{ tip?: string }> = ({ tip = '잠시만 기다려주세요...' }) => (
  <div
    style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      background: 'rgba(255, 255, 255, 0.95)',
      zIndex: 9999
    }}
  >
    <div style={{ textAlign: 'center' }}>
      <Spin size="large" />
      <div style={{ marginTop: 16, color: '#666' }}>{tip}</div>
    </div>
  </div>
);