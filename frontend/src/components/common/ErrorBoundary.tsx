// 에러 바운더리 컴포넌트

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Result, Button } from 'antd';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo
    });

    // 에러 로깅 서비스로 전송 (예: Sentry)
    // logErrorToService(error, errorInfo);
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
    // 페이지 새로고침
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return <>{this.props.fallback}</>;
      }

      return (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          background: '#f0f2f5'
        }}>
          <Result
            status="error"
            title="오류가 발생했습니다"
            subTitle="예기치 않은 오류가 발생했습니다. 페이지를 새로고침하거나 잠시 후 다시 시도해주세요."
            extra={[
              <Button type="primary" key="reload" onClick={this.handleReset}>
                페이지 새로고침
              </Button>,
              <Button key="home" onClick={() => window.location.href = '/'}>
                홈으로 이동
              </Button>
            ]}
          >
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div style={{
                marginTop: 24,
                padding: 16,
                background: '#fff',
                border: '1px solid #f0f0f0',
                borderRadius: 4,
                maxHeight: 400,
                overflow: 'auto'
              }}>
                <h4 style={{ marginBottom: 8 }}>에러 상세 정보 (개발 모드)</h4>
                <pre style={{
                  fontSize: 12,
                  color: '#ff4d4f',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word'
                }}>
                  <strong>{this.state.error.toString()}</strong>
                  {'\n\n'}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </div>
            )}
          </Result>
        </div>
      );
    }

    return this.props.children;
  }
}