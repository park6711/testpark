import React, { Suspense, lazy, useEffect, useState } from 'react';
import { ConfigProvider, Spin, notification } from 'antd';
import koKR from 'antd/locale/ko_KR';
import './App.css';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { AuthProvider } from './contexts/AuthContext';

// 의뢰관리 컴포넌트만 로드
const QuoteManagement = lazy(() => import('./components/QuoteManagement'));

// 전역 설정
const globalConfig = {
  theme: {
    token: {
      colorPrimary: '#667eea',
      borderRadius: 6,
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    },
  },
};

// Django 컨텍스트 타입
interface DjangoContext {
  user: {
    username: string;
    email: string;
    isAuthenticated: boolean;
    isStaff: boolean;
  };
  apiBaseUrl: string;
  csrfToken: string;
}

function App() {
  const [djangoContext, setDjangoContext] = useState<DjangoContext | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Django 컨텍스트 초기화
    const context = (window as any).__DJANGO_CONTEXT__;
    if (context) {
      setDjangoContext(context);
      console.log('Django 컨텍스트 로드:', context);
    } else {
      console.warn('Django 컨텍스트를 찾을 수 없습니다.');
    }
    setLoading(false);

    // 전역 에러 핸들러
    const handleError = (event: ErrorEvent) => {
      console.error('전역 에러:', event.error);
      notification.error({
        message: '오류 발생',
        description: '예기치 않은 오류가 발생했습니다. 페이지를 새로고침해주세요.',
        placement: 'topRight',
      });
    };

    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: '#f0f2f5'
      }}>
        <Spin size="large" tip="애플리케이션을 불러오는 중..." />
      </div>
    );
  }

  return (
    <ConfigProvider locale={koKR} theme={globalConfig.theme}>
      <ErrorBoundary>
        <AuthProvider context={djangoContext}>
          <div style={{
            minHeight: '100vh',
            background: '#f0f2f5'
          }}>
            <Suspense fallback={
              <div style={{
                padding: '50px',
                textAlign: 'center'
              }}>
                <Spin size="large" tip="의뢰관리 시스템을 불러오는 중..." />
              </div>
            }>
              {/* 의뢰관리 시스템만 표시 - 네비게이션 없음 */}
              <QuoteManagement />
            </Suspense>
          </div>
        </AuthProvider>
      </ErrorBoundary>
    </ConfigProvider>
  );
}

export default App;