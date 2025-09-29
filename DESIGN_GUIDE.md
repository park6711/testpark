# 🎨 (주)박목수의 열린견적서 - 디자인 가이드

## 📌 디자인 철학

### 핵심 가치
- **신뢰성**: 인테리어 업체와 고객 간의 신뢰를 시각적으로 표현
- **전문성**: 깔끔하고 현대적인 디자인으로 전문성 강조
- **접근성**: 모든 사용자가 쉽게 사용할 수 있는 직관적인 인터페이스
- **일관성**: 전체 애플리케이션에서 통일된 디자인 언어 사용

---

## 🎨 브랜드 아이덴티티

### 로고
- **메인 로고**: 녹색 그라디언트 큐브 형태
  - 건축과 인테리어를 상징하는 3D 큐브 디자인
  - 친환경과 신뢰를 나타내는 녹색 컬러
  - 크기: 기본 100px, 반응형 80px (모바일)

### 브랜드 컬러 팔레트

#### 주요 색상 (Primary Colors)
```css
/* 브랜드 그린 - 메인 액션 색상 */
--primary-green: #10b981;      /* 메인 그린 */
--primary-green-hover: #059669; /* 호버 상태 */
--primary-green-light: #34d399; /* 라이트 버전 */
--primary-green-bg: #d1fae5;    /* 배경용 연한 그린 */

/* 네이버 그린 - 로그인 연동 */
--naver-green: #03C75A;
--naver-green-hover: #02b151;
```

#### 보조 색상 (Secondary Colors)
```css
/* 그레이 스케일 - 텍스트와 배경 */
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-300: #d1d5db;
--gray-400: #9ca3af;
--gray-500: #6b7280;
--gray-600: #4b5563;
--gray-700: #374151;
--gray-800: #1f2937;
--gray-900: #111827;

/* 의미 색상 - 상태 표시 */
--success: #22c55e;
--warning: #f59e0b;
--error: #ef4444;
--info: #3b82f6;
```

#### 배경 그라디언트
```css
/* 로그인 페이지 배경 */
background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);

/* 대시보드 헤더 */
background: linear-gradient(90deg, #34d399 0%, #10b981 100%);
```

---

## 📝 타이포그래피

### 폰트 패밀리
```css
font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### 폰트 웨이트
- **Light (300)**: 보조 텍스트
- **Regular (400)**: 본문 텍스트
- **Medium (500)**: 버튼, 중요 레이블
- **SemiBold (600)**: 섹션 제목
- **Bold (700)**: 페이지 제목, 강조

### 텍스트 크기
```css
/* 제목 */
--text-h1: 1.875rem;  /* 30px - 페이지 제목 */
--text-h2: 1.5rem;    /* 24px - 섹션 제목 */
--text-h3: 1.25rem;   /* 20px - 서브 섹션 */
--text-h4: 1.125rem;  /* 18px - 카드 제목 */

/* 본문 */
--text-base: 1rem;    /* 16px - 기본 텍스트 */
--text-sm: 0.875rem;  /* 14px - 작은 텍스트 */
--text-xs: 0.75rem;   /* 12px - 캡션, 힌트 */
```

---

## 🔲 레이아웃 및 스페이싱

### 그리드 시스템
- **컨테이너 최대 너비**: 1280px
- **그리드 컬럼**: 12 컬럼 시스템
- **거터**: 1rem (16px)

### 스페이싱 규칙
```css
/* 패딩/마진 단위 */
--spacing-xs: 0.25rem;  /* 4px */
--spacing-sm: 0.5rem;   /* 8px */
--spacing-md: 1rem;     /* 16px */
--spacing-lg: 1.5rem;   /* 24px */
--spacing-xl: 2rem;     /* 32px */
--spacing-2xl: 3rem;    /* 48px */
```

### 모서리 둥글기
```css
--radius-sm: 0.375rem;   /* 6px - 작은 요소 */
--radius-md: 0.5rem;     /* 8px - 기본 카드 */
--radius-lg: 0.75rem;    /* 12px - 큰 카드 */
--radius-xl: 1rem;       /* 16px - 모달 */
--radius-2xl: 1.5rem;    /* 24px - 로그인 박스 */
--radius-full: 9999px;   /* 완전 둥근 */
```

---

## 🎯 컴포넌트 스타일 가이드

### 버튼 (Buttons)
```css
/* 기본 버튼 스타일 */
.btn {
    padding: 0.75rem 1.5rem;
    border-radius: var(--radius-md);
    font-weight: 500;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

/* 주요 버튼 */
.btn-primary {
    background: var(--primary-green);
    color: white;
    box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);
}

.btn-primary:hover {
    background: var(--primary-green-hover);
    transform: translateY(-2px);
    box-shadow: 0 8px 12px rgba(16, 185, 129, 0.3);
}

/* 네이버 로그인 버튼 */
.btn-naver {
    background: var(--naver-green);
    color: white;
}
```

### 카드 (Cards)
```css
.card {
    background: white;
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--gray-200);
}

.card:hover {
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

### 입력 필드 (Input Fields)
```css
.input-field {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 1px solid var(--gray-300);
    border-radius: var(--radius-md);
    font-size: var(--text-base);
    transition: all 0.2s;
}

.input-field:focus {
    border-color: var(--primary-green);
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
    outline: none;
}
```

### 테이블 (Tables)
```css
.table {
    background: white;
    border-radius: var(--radius-md);
    overflow: hidden;
}

.table th {
    background: var(--gray-50);
    color: var(--gray-700);
    font-weight: 600;
    padding: 0.75rem;
    border-bottom: 2px solid var(--gray-200);
}

.table td {
    padding: 0.75rem;
    border-bottom: 1px solid var(--gray-100);
}

.table tr:hover {
    background: var(--gray-50);
}
```

### 상태 배지 (Status Badges)
```css
.badge {
    display: inline-flex;
    padding: 0.25rem 0.75rem;
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: 500;
}

.badge-success {
    background: #d1fae5;
    color: #065f46;
}

.badge-warning {
    background: #fef3c7;
    color: #92400e;
}

.badge-error {
    background: #fee2e2;
    color: #991b1b;
}
```

---

## 📱 반응형 디자인

### 브레이크포인트
```css
/* 모바일 우선 접근 */
--screen-sm: 576px;   /* 모바일 */
--screen-md: 768px;   /* 태블릿 */
--screen-lg: 992px;   /* 데스크톱 */
--screen-xl: 1200px;  /* 와이드 스크린 */
```

### 반응형 규칙
1. **모바일 우선**: 기본 스타일은 모바일 기준
2. **유연한 그리드**: 백분율 기반 너비 사용
3. **터치 친화적**: 최소 44px 터치 타겟
4. **가독성 우선**: 모바일에서도 읽기 쉬운 폰트 크기

---

## 🎭 애니메이션 및 전환

### 트랜지션
```css
/* 기본 트랜지션 */
--transition-fast: 0.15s ease;
--transition-base: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow: 0.5s ease-out;
```

### 애니메이션 예시
```css
/* 페이드 인 */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* 슬라이드 업 */
@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 로딩 스피너 */
@keyframes spin {
    to { transform: rotate(360deg); }
}
```

---

## ♿ 접근성 가이드라인

### 색상 대비
- **일반 텍스트**: 최소 4.5:1 대비율
- **큰 텍스트**: 최소 3:1 대비율
- **중요 정보**: 색상에만 의존하지 않고 아이콘/텍스트 병행

### 키보드 접근성
```css
/* 포커스 표시 */
:focus {
    outline: 2px solid var(--primary-green);
    outline-offset: 2px;
}

/* 포커스 비저블 */
.focus-visible:focus-visible {
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.5);
}
```

### 스크린 리더 지원
```css
/* 숨김 텍스트 (스크린 리더용) */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    border: 0;
}
```

---

## 🌙 다크 모드 (향후 구현)

### 다크 모드 색상
```css
@media (prefers-color-scheme: dark) {
    :root {
        --bg-primary: #1a202c;
        --bg-secondary: #2d3748;
        --text-primary: #f7fafc;
        --text-secondary: #cbd5e0;
    }
}
```

---

## 📋 체크리스트

### 새 컴포넌트 개발 시
- [ ] 브랜드 컬러 팔레트 사용
- [ ] Noto Sans KR 폰트 적용
- [ ] 정의된 스페이싱 단위 사용
- [ ] 반응형 디자인 적용
- [ ] 키보드 접근성 확인
- [ ] 호버/포커스 상태 정의
- [ ] 로딩/에러 상태 처리
- [ ] 다크 모드 고려 (향후)

### 페이지 레이아웃 시
- [ ] 일관된 헤더/푸터 사용
- [ ] 최대 너비 1280px 제한
- [ ] 모바일 우선 디자인
- [ ] 적절한 여백과 간격
- [ ] 시각적 계층 구조 확립

---

## 🔧 구현 예시

### Django 템플릿 적용
```html
<!-- base.html -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{% static 'css/design-system.css' %}">
```

### React 컴포넌트 적용
```jsx
// theme.js
export const theme = {
  colors: {
    primary: '#10b981',
    primaryHover: '#059669',
    gray: {
      50: '#f9fafb',
      // ...
    }
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    // ...
  }
};
```

---

## 📚 참고 자료

- Material Design Guidelines
- Apple Human Interface Guidelines
- Web Content Accessibility Guidelines (WCAG) 2.1
- 네이버 디자인 시스템

---

## 🔄 버전 히스토리

- **v1.0.0** (2025-09-30): 초기 디자인 가이드 작성 - 루크
  - 브랜드 아이덴티티 정의
  - 컬러 팔레트 확립
  - 기본 컴포넌트 스타일 정의
  - 반응형 디자인 가이드라인

---

> 이 가이드는 지속적으로 업데이트되며, 모든 개발자와 디자이너가 참고해야 합니다.