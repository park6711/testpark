# TestPark 공통 React 컴포넌트 라이브러리

TestPark 프로젝트의 모든 앱에서 일관된 UI/UX를 제공하기 위한 공통 React 컴포넌트 라이브러리입니다.

## 파일 구조

```
/static/js/
├── api-helpers.js          # API 요청 유틸리티 함수들
├── common-react-components.js  # React 컴포넌트들
└── common-styles.css       # 공통 CSS 스타일
```

## 설치 및 사용법

### 1. HTML 템플릿에 라이브러리 포함

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- 공통 스타일 -->
    <link href="{% static 'js/common-styles.css' %}" rel="stylesheet">

    <!-- React -->
    <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>

    <!-- Babel -->
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
</head>
<body>
    <div id="react-root"></div>

    <!-- CSRF Token -->
    <script>
        window.csrfToken = '{{ csrf_token }}';
    </script>

    <!-- 공통 라이브러리 -->
    <script src="{% static 'js/api-helpers.js' %}"></script>
    <script src="{% static 'js/common-react-components.js' %}"></script>

    <!-- 앱별 컴포넌트 -->
    <script type="text/babel">
        // 여기에 앱별 React 컴포넌트 작성
    </script>
</body>
</html>
```

### 2. API 헬퍼 사용법

```javascript
// 기본 API 요청
const response = await window.apiRequest('/api/data/', {
    method: 'GET'
});

// CRUD 작업
const newItem = await window.apiCRUD.create('/api/items/', {
    name: '새 아이템',
    description: '설명'
});

const item = await window.apiCRUD.read('/api/items/1/');
const updatedItem = await window.apiCRUD.update('/api/items/1/', { name: '수정된 이름' });
await window.apiCRUD.delete('/api/items/1/');

// 목록 API (페이지네이션)
const listData = await window.apiListRequest('/api/items', {
    search: '검색어',
    status: '활성'
}, 1, 20);

// 알림 표시
window.showNotification('성공적으로 저장되었습니다.', 'success');
window.showNotification('오류가 발생했습니다.', 'error');

// 로딩 표시
window.loadingManager.show('데이터를 불러오는 중...');
window.loadingManager.hide();
```

## 컴포넌트 사용법

### DataTable 컴포넌트

리스트 페이지에서 사용하는 데이터 테이블 컴포넌트입니다.

```javascript
const MyListPage = () => {
    const [data, setData] = useState([]);
    const [pagination, setPagination] = useState(null);
    const [loading, setLoading] = useState(false);

    const columns = [
        {
            key: 'name',
            title: '이름',
            render: (value, row) => (
                <span className="cursor-pointer text-decoration-underline">
                    {value}
                </span>
            )
        },
        {
            key: 'status',
            title: '상태',
            render: (value) => React.createElement(window.StatusBadge, { status: value })
        },
        {
            key: 'created_at',
            title: '생성일',
            render: (value) => window.formatDate(value, 'YYYY-MM-DD')
        }
    ];

    const actions = [
        {
            label: '새 항목 추가',
            className: 'btn btn-success',
            onClick: () => console.log('새 항목 추가')
        },
        {
            label: '선택 삭제',
            className: 'btn btn-danger',
            requireSelection: true,
            onClick: (selectedIds) => console.log('삭제할 ID들:', selectedIds)
        }
    ];

    return React.createElement(window.DataTable, {
        data: data,
        columns: columns,
        pagination: pagination,
        loading: loading,
        actions: actions,
        onPageChange: (page) => loadData(page),
        onSearch: (searchTerm) => loadData(1, { search: searchTerm }),
        onSelectionChange: (selectedIds) => console.log('선택된 항목들:', selectedIds)
    });
};
```

### Modal 컴포넌트

```javascript
const MyModal = () => {
    const [showModal, setShowModal] = useState(false);

    const footer = [
        React.createElement('button', {
            key: 'cancel',
            className: 'btn btn-secondary',
            onClick: () => setShowModal(false)
        }, '취소'),
        React.createElement('button', {
            key: 'save',
            className: 'btn btn-primary',
            onClick: () => console.log('저장')
        }, '저장')
    ];

    return React.createElement(window.Modal, {
        show: showModal,
        onClose: () => setShowModal(false),
        title: '항목 편집',
        size: 'lg',
        footer: footer
    }, React.createElement('div', null, '모달 내용'));
};
```

### FormField 컴포넌트

```javascript
const MyForm = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        status: '',
        description: '',
        active: false
    });

    const handleFieldChange = (name, value) => {
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    return React.createElement('form', null, [
        React.createElement(window.FormField, {
            key: 'name',
            type: 'text',
            label: '이름',
            name: 'name',
            value: formData.name,
            onChange: handleFieldChange,
            required: true,
            placeholder: '이름을 입력하세요'
        }),
        React.createElement(window.FormField, {
            key: 'email',
            type: 'email',
            label: '이메일',
            name: 'email',
            value: formData.email,
            onChange: handleFieldChange,
            required: true
        }),
        React.createElement(window.FormField, {
            key: 'status',
            type: 'select',
            label: '상태',
            name: 'status',
            value: formData.status,
            onChange: handleFieldChange,
            options: [
                { value: '', label: '선택하세요' },
                { value: 'active', label: '활성' },
                { value: 'inactive', label: '비활성' }
            ]
        }),
        React.createElement(window.FormField, {
            key: 'description',
            type: 'textarea',
            label: '설명',
            name: 'description',
            value: formData.description,
            onChange: handleFieldChange,
            rows: 4
        }),
        React.createElement(window.FormField, {
            key: 'active',
            type: 'checkbox',
            label: '활성화',
            name: 'active',
            value: formData.active,
            onChange: handleFieldChange
        })
    ]);
};
```

### FilterPanel 컴포넌트

```javascript
const MyFilterPanel = () => {
    const [filters, setFilters] = useState({
        search: '',
        status: '',
        category: '',
        urgent_only: false
    });

    const filterOptions = [
        {
            name: 'status',
            type: 'select',
            width: 2,
            allLabel: '전체 상태',
            options: [
                { value: 'active', label: '활성' },
                { value: 'inactive', label: '비활성' }
            ]
        },
        {
            name: 'category',
            type: 'select',
            width: 2,
            allLabel: '전체 카테고리',
            options: [
                { value: 'cat1', label: '카테고리1' },
                { value: 'cat2', label: '카테고리2' }
            ]
        },
        {
            name: 'urgent_only',
            type: 'checkbox',
            width: 2,
            label: '긴급만 보기'
        }
    ];

    return React.createElement(window.FilterPanel, {
        filters: filters,
        onFilterChange: (name, value) => setFilters(prev => ({ ...prev, [name]: value })),
        onSearch: () => console.log('검색:', filters),
        filterOptions: filterOptions,
        searchPlaceholder: '이름, 설명으로 검색...'
    });
};
```

### StatusBadge 컴포넌트

```javascript
const MyStatusBadge = ({ status }) => {
    return React.createElement(window.StatusBadge, {
        status: status,
        onClick: (status) => console.log('상태 클릭:', status)
    });
};
```

### LoadingSpinner 컴포넌트

```javascript
const MyLoadingComponent = () => {
    const [loading, setLoading] = useState(true);

    if (loading) {
        return React.createElement(window.LoadingSpinner, {
            size: 'large',
            text: '데이터를 불러오는 중입니다...'
        });
    }

    return React.createElement('div', null, '데이터 로드 완료');
};
```

## 유틸리티 함수들

### 날짜 포맷팅

```javascript
const formattedDate = window.formatDate(new Date(), 'YYYY-MM-DD');
const formattedDateTime = window.formatDate(new Date(), 'YYYY-MM-DD HH:mm');
const localeString = window.formatDate(new Date(), 'localeString');
```

### 긴급성 체크

```javascript
const urgent = window.isUrgent('2024-01-15'); // 3일 이내인지 체크
```

### 상태 배지 클래스

```javascript
const badgeClass = window.getStatusBadgeClass('활성'); // 'bg-success text-white'
```

## CSS 클래스

공통 스타일시트에서 제공하는 유틸리티 클래스들을 사용할 수 있습니다:

```html
<!-- TestPark 전용 클래스 -->
<div class="testpark-card">카드 컨테이너</div>
<table class="testpark-table">테이블</table>
<button class="testpark-btn testpark-btn-primary">버튼</button>
<span class="testpark-status-badge">상태 배지</span>

<!-- Tailwind 스타일 유틸리티 클래스 -->
<div class="bg-gray-100 p-4 rounded-lg shadow-md">
    <div class="text-gray-800 font-semibold">제목</div>
    <div class="text-gray-600 text-sm">설명</div>
</div>
```

## 완전한 예제

다른 앱에서 이 라이브러리를 사용하는 완전한 예제:

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>샘플 앱</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{% static 'js/common-styles.css' %}" rel="stylesheet">
    <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
</head>
<body>
    <div id="react-root"></div>
    <script>window.csrfToken = '{{ csrf_token }}';</script>
    <script src="{% static 'js/api-helpers.js' %}"></script>
    <script src="{% static 'js/common-react-components.js' %}"></script>

    <script type="text/babel">
        const SampleApp = () => {
            const [data, setData] = useState([]);
            const [pagination, setPagination] = useState(null);
            const [loading, setLoading] = useState(false);

            const loadData = async (page = 1, filters = {}) => {
                setLoading(true);
                try {
                    const response = await window.apiListRequest('/api/sample/', filters, page);
                    setData(response.data);
                    setPagination(response.pagination);
                } catch (error) {
                    window.showNotification('데이터 로드 실패', 'error');
                } finally {
                    setLoading(false);
                }
            };

            useEffect(() => {
                loadData();
            }, []);

            const columns = [
                { key: 'name', title: '이름' },
                { key: 'status', title: '상태', render: (value) =>
                    React.createElement(window.StatusBadge, { status: value }) }
            ];

            return React.createElement('div', { className: 'container-fluid py-4' }, [
                React.createElement('h1', { key: 'title' }, '샘플 앱'),
                React.createElement(window.DataTable, {
                    key: 'table',
                    data: data,
                    columns: columns,
                    pagination: pagination,
                    loading: loading,
                    onPageChange: loadData,
                    onSearch: (search) => loadData(1, { search })
                })
            ]);
        };

        ReactDOM.render(React.createElement(SampleApp), document.getElementById('react-root'));
    </script>
</body>
</html>
```

이제 모든 앱에서 일관된 UI/UX를 제공할 수 있습니다!