// 인증 컨텍스트

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { notification } from 'antd';

interface User {
  username: string;
  email: string;
  isAuthenticated: boolean;
  isStaff: boolean;
}

interface DjangoContext {
  user: User;
  apiBaseUrl: string;
  csrfToken: string;
}

interface AuthContextValue {
  user: User | null;
  djangoContext: DjangoContext | null;
  isAuthenticated: boolean;
  isStaff: boolean;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
  context?: DjangoContext | null;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children, context }) => {
  const [user, setUser] = useState<User | null>(null);
  const [djangoContext, setDjangoContext] = useState<DjangoContext | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Django 컨텍스트에서 사용자 정보 초기화
    if (context) {
      setDjangoContext(context);
      if (context.user && context.user.isAuthenticated) {
        setUser(context.user);
      }
    }
    setLoading(false);
  }, [context]);

  const login = async (username: string, password: string): Promise<void> => {
    try {
      // Django 로그인 API 호출
      const response = await fetch('/accounts/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': djangoContext?.csrfToken || ''
        },
        body: JSON.stringify({ username, password }),
        credentials: 'include'
      });

      if (response.ok) {
        const userData = await response.json();
        setUser({
          username: userData.username,
          email: userData.email,
          isAuthenticated: true,
          isStaff: userData.is_staff || false
        });
        notification.success({
          message: '로그인 성공',
          description: `환영합니다, ${userData.username}님!`
        });
      } else {
        throw new Error('로그인 실패');
      }
    } catch (error) {
      notification.error({
        message: '로그인 실패',
        description: '아이디 또는 비밀번호를 확인해주세요.'
      });
      throw error;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      // Django 로그아웃 API 호출
      const response = await fetch('/accounts/logout/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': djangoContext?.csrfToken || ''
        },
        credentials: 'include'
      });

      if (response.ok) {
        setUser(null);
        notification.success({
          message: '로그아웃 완료',
          description: '안전하게 로그아웃되었습니다.'
        });
        // 로그인 페이지로 리다이렉트
        window.location.href = '/accounts/login/';
      }
    } catch (error) {
      notification.error({
        message: '로그아웃 실패',
        description: '다시 시도해주세요.'
      });
      throw error;
    }
  };

  const refreshUser = async (): Promise<void> => {
    try {
      setLoading(true);
      // 사용자 정보 새로고침 API 호출
      const response = await fetch('/api/auth/user/', {
        credentials: 'include'
      });

      if (response.ok) {
        const userData = await response.json();
        setUser({
          username: userData.username,
          email: userData.email,
          isAuthenticated: true,
          isStaff: userData.is_staff || false
        });
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('사용자 정보 새로고침 실패:', error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const value: AuthContextValue = {
    user,
    djangoContext,
    isAuthenticated: user?.isAuthenticated || false,
    isStaff: user?.isStaff || false,
    loading,
    login,
    logout,
    refreshUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// 커스텀 훅
export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// 권한 체크 HOC
export const withAuth = <P extends object>(
  Component: React.ComponentType<P>,
  requireStaff: boolean = false
): React.FC<P> => {
  return (props: P) => {
    const { isAuthenticated, isStaff, loading } = useAuth();

    if (loading) {
      return <div>로딩 중...</div>;
    }

    if (!isAuthenticated) {
      window.location.href = '/accounts/login/';
      return null;
    }

    if (requireStaff && !isStaff) {
      return (
        <div style={{ padding: '50px', textAlign: 'center' }}>
          <h2>접근 권한이 없습니다</h2>
          <p>이 페이지에 접근하려면 관리자 권한이 필요합니다.</p>
        </div>
      );
    }

    return <Component {...props} />;
  };
};