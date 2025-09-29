/**
 * 공통 React 컴포넌트 라이브러리
 * TestPark 프로젝트의 모든 앱에서 재사용 가능한 React 컴포넌트들
 */

// React Hooks 공통 import
const { useState, useEffect, useCallback, useMemo } = React;

// Lucide Icons (외부에서 로드된다고 가정)
// const { Search, Plus, Edit, Trash2, X, ChevronDown, Save, RotateCcw } = lucide;

/**
 * 공통 데이터 테이블 컴포넌트
 * 페이지네이션, 검색, 정렬, 선택 기능을 포함
 */
window.DataTable = function({
    data = [],
    columns = [],
    pagination = null,
    onPageChange = () => {},
    onSearch = () => {},
    onSort = () => {},
    onSelectionChange = () => {},
    loading = false,
    searchable = true,
    selectable = true,
    actions = [],
    className = "",
    emptyMessage = "데이터가 없습니다."
}) {
    const [selectedRows, setSelectedRows] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');

    const handleSelectAll = (e) => {
        const newSelection = e.target.checked ? data.map(row => row.id) : [];
        setSelectedRows(newSelection);
        onSelectionChange(newSelection);
    };

    const handleSelectRow = (id) => {
        const newSelection = selectedRows.includes(id)
            ? selectedRows.filter(rowId => rowId !== id)
            : [...selectedRows, id];
        setSelectedRows(newSelection);
        onSelectionChange(newSelection);
    };

    const handleSearch = () => {
        onSearch(searchTerm);
    };

    return React.createElement('div', { className: `card ${className}` }, [
        // 검색 및 액션 바
        searchable || actions.length > 0 ? React.createElement('div', {
            key: 'header',
            className: 'card-header'
        }, [
            React.createElement('div', {
                key: 'header-content',
                className: 'd-flex justify-content-between align-items-center'
            }, [
                // 검색
                searchable ? React.createElement('div', {
                    key: 'search',
                    className: 'input-group',
                    style: { maxWidth: '300px' }
                }, [
                    React.createElement('input', {
                        key: 'search-input',
                        type: 'text',
                        className: 'form-control',
                        placeholder: '검색...',
                        value: searchTerm,
                        onChange: (e) => setSearchTerm(e.target.value),
                        onKeyPress: (e) => e.key === 'Enter' && handleSearch()
                    }),
                    React.createElement('button', {
                        key: 'search-btn',
                        className: 'btn btn-outline-secondary',
                        onClick: handleSearch
                    }, '검색')
                ]) : null,
                // 액션 버튼들
                actions.length > 0 ? React.createElement('div', {
                    key: 'actions',
                    className: 'd-flex gap-2'
                }, actions.map((action, index) =>
                    React.createElement('button', {
                        key: index,
                        className: action.className || 'btn btn-primary',
                        onClick: () => action.onClick(selectedRows),
                        disabled: action.requireSelection && selectedRows.length === 0
                    }, action.label)
                )) : null
            ])
        ]) : null,

        // 테이블 본체
        React.createElement('div', {
            key: 'body',
            className: 'card-body'
        }, [
            loading ? React.createElement('div', {
                key: 'loading',
                className: 'text-center py-4'
            }, [
                React.createElement('div', {
                    key: 'spinner',
                    className: 'spinner-border',
                    role: 'status'
                }),
                React.createElement('div', {
                    key: 'loading-text',
                    className: 'mt-2'
                }, '데이터를 불러오는 중...')
            ]) : React.createElement('div', {
                key: 'table-wrapper',
                className: 'table-responsive'
            }, [
                data.length === 0 ? React.createElement('div', {
                    key: 'empty',
                    className: 'text-center py-4 text-muted'
                }, emptyMessage) : React.createElement('table', {
                    key: 'table',
                    className: 'table table-hover'
                }, [
                    // 테이블 헤더
                    React.createElement('thead', {
                        key: 'thead',
                        className: 'table-light'
                    }, React.createElement('tr', { key: 'header-row' }, [
                        selectable ? React.createElement('th', {
                            key: 'select-all',
                            width: '40'
                        }, React.createElement('input', {
                            type: 'checkbox',
                            className: 'form-check-input',
                            checked: selectedRows.length === data.length && data.length > 0,
                            onChange: handleSelectAll
                        })) : null,
                        ...columns.map((col, index) =>
                            React.createElement('th', {
                                key: col.key || index,
                                width: col.width,
                                className: col.sortable ? 'cursor-pointer' : '',
                                onClick: col.sortable ? () => onSort(col.key) : undefined
                            }, col.title)
                        )
                    ])),
                    // 테이블 바디
                    React.createElement('tbody', { key: 'tbody' },
                        data.map((row, rowIndex) =>
                            React.createElement('tr', {
                                key: row.id || rowIndex,
                                className: row.urgent ? 'table-warning' : ''
                            }, [
                                selectable ? React.createElement('td', {
                                    key: 'select'
                                }, React.createElement('input', {
                                    type: 'checkbox',
                                    className: 'form-check-input',
                                    checked: selectedRows.includes(row.id),
                                    onChange: () => handleSelectRow(row.id)
                                })) : null,
                                ...columns.map((col, colIndex) =>
                                    React.createElement('td', {
                                        key: col.key || colIndex
                                    }, col.render ? col.render(row[col.key], row) : row[col.key])
                                )
                            ])
                        )
                    )
                ])
            ])
        ]),

        // 페이지네이션
        pagination && pagination.total_pages > 1 ? React.createElement('div', {
            key: 'pagination',
            className: 'card-footer'
        }, React.createElement('nav', {
            'aria-label': 'Page navigation'
        }, React.createElement('ul', {
            className: 'pagination justify-content-center mb-0'
        }, [
            React.createElement('li', {
                key: 'prev',
                className: `page-item ${!pagination.has_previous ? 'disabled' : ''}`
            }, React.createElement('button', {
                className: 'page-link',
                onClick: () => onPageChange(pagination.current_page - 1),
                disabled: !pagination.has_previous
            }, '이전')),
            ...Array.from({ length: pagination.total_pages }, (_, i) =>
                React.createElement('li', {
                    key: i,
                    className: `page-item ${pagination.current_page === i + 1 ? 'active' : ''}`
                }, React.createElement('button', {
                    className: 'page-link',
                    onClick: () => onPageChange(i + 1)
                }, i + 1))
            ),
            React.createElement('li', {
                key: 'next',
                className: `page-item ${!pagination.has_next ? 'disabled' : ''}`
            }, React.createElement('button', {
                className: 'page-link',
                onClick: () => onPageChange(pagination.current_page + 1),
                disabled: !pagination.has_next
            }, '다음'))
        ]))) : null
    ]);
};

/**
 * 공통 모달 컴포넌트
 */
window.Modal = function({
    show = false,
    onClose = () => {},
    title = '',
    size = '',
    children,
    footer = null
}) {
    if (!show) return null;

    const modalClass = size ? `modal-${size}` : '';

    return React.createElement('div', {
        className: 'modal show',
        style: { display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' },
        onClick: (e) => e.target === e.currentTarget && onClose()
    }, React.createElement('div', {
        className: `modal-dialog ${modalClass}`
    }, React.createElement('div', {
        className: 'modal-content'
    }, [
        React.createElement('div', {
            key: 'header',
            className: 'modal-header'
        }, [
            React.createElement('h5', {
                key: 'title',
                className: 'modal-title'
            }, title),
            React.createElement('button', {
                key: 'close',
                type: 'button',
                className: 'btn-close',
                onClick: onClose
            })
        ]),
        React.createElement('div', {
            key: 'body',
            className: 'modal-body'
        }, children),
        footer ? React.createElement('div', {
            key: 'footer',
            className: 'modal-footer'
        }, footer) : null
    ])));
};

/**
 * 공통 폼 컴포넌트
 */
window.FormField = function({
    type = 'text',
    label,
    name,
    value,
    onChange,
    required = false,
    placeholder = '',
    options = [],
    rows = 3,
    className = '',
    ...props
}) {
    const inputId = `field-${name}`;

    return React.createElement('div', {
        className: `mb-3 ${className}`
    }, [
        label ? React.createElement('label', {
            key: 'label',
            className: 'form-label',
            htmlFor: inputId
        }, [label, required ? React.createElement('span', {
            key: 'required',
            className: 'text-danger'
        }, ' *') : null]) : null,

        type === 'select' ? React.createElement('select', {
            key: 'select',
            id: inputId,
            className: 'form-select',
            value: value,
            onChange: (e) => onChange(name, e.target.value),
            required,
            ...props
        }, options.map(option =>
            React.createElement('option', {
                key: option.value,
                value: option.value
            }, option.label)
        )) :

        type === 'textarea' ? React.createElement('textarea', {
            key: 'textarea',
            id: inputId,
            className: 'form-control',
            value: value,
            onChange: (e) => onChange(name, e.target.value),
            placeholder,
            required,
            rows,
            ...props
        }) :

        type === 'checkbox' ? React.createElement('div', {
            key: 'checkbox',
            className: 'form-check'
        }, [
            React.createElement('input', {
                key: 'checkbox-input',
                type: 'checkbox',
                id: inputId,
                className: 'form-check-input',
                checked: value,
                onChange: (e) => onChange(name, e.target.checked),
                ...props
            }),
            React.createElement('label', {
                key: 'checkbox-label',
                className: 'form-check-label',
                htmlFor: inputId
            }, label)
        ]) :

        React.createElement('input', {
            key: 'input',
            type,
            id: inputId,
            className: 'form-control',
            value: value,
            onChange: (e) => onChange(name, e.target.value),
            placeholder,
            required,
            ...props
        })
    ]);
};

/**
 * 상태 배지 컴포넌트
 */
window.StatusBadge = function({
    status,
    onClick = null,
    className = ''
}) {
    const badgeClass = window.getStatusBadgeClass(status);
    const isClickable = onClick !== null;

    return React.createElement('span', {
        className: `badge ${badgeClass} ${isClickable ? 'cursor-pointer' : ''} ${className}`,
        onClick: isClickable ? () => onClick(status) : undefined
    }, status);
};

/**
 * 필터 컴포넌트
 */
window.FilterPanel = function({
    filters = {},
    onFilterChange = () => {},
    onSearch = () => {},
    filterOptions = [],
    searchPlaceholder = '검색...'
}) {
    return React.createElement('div', {
        className: 'card mb-4'
    }, React.createElement('div', {
        className: 'card-body'
    }, React.createElement('div', {
        className: 'row g-3'
    }, [
        // 검색 필드
        React.createElement('div', {
            key: 'search',
            className: 'col-md-4'
        }, React.createElement('div', {
            className: 'input-group'
        }, [
            React.createElement('input', {
                key: 'search-input',
                type: 'text',
                className: 'form-control',
                placeholder: searchPlaceholder,
                value: filters.search || '',
                onChange: (e) => onFilterChange('search', e.target.value),
                onKeyPress: (e) => e.key === 'Enter' && onSearch()
            }),
            React.createElement('button', {
                key: 'search-btn',
                className: 'btn btn-primary',
                onClick: onSearch
            }, '검색')
        ])),

        // 필터 옵션들
        ...filterOptions.map((filter, index) =>
            React.createElement('div', {
                key: filter.name,
                className: `col-md-${filter.width || 2}`
            }, filter.type === 'select' ? React.createElement('select', {
                className: 'form-select',
                value: filters[filter.name] || '',
                onChange: (e) => onFilterChange(filter.name, e.target.value)
            }, [
                React.createElement('option', {
                    key: 'all',
                    value: ''
                }, filter.allLabel || '전체'),
                ...filter.options.map(option =>
                    React.createElement('option', {
                        key: option.value,
                        value: option.value
                    }, option.label)
                )
            ]) : filter.type === 'checkbox' ? React.createElement('div', {
                className: 'form-check'
            }, [
                React.createElement('input', {
                    key: 'checkbox',
                    className: 'form-check-input',
                    type: 'checkbox',
                    checked: filters[filter.name] || false,
                    onChange: (e) => onFilterChange(filter.name, e.target.checked)
                }),
                React.createElement('label', {
                    key: 'label',
                    className: 'form-check-label'
                }, filter.label)
            ]) : null)
        )
    ])));
};

/**
 * 로딩 스피너 컴포넌트
 */
window.LoadingSpinner = function({
    size = 'medium',
    text = '로딩 중...',
    className = ''
}) {
    const sizeClass = {
        small: 'spinner-border-sm',
        medium: '',
        large: 'spinner-border-lg'
    }[size];

    return React.createElement('div', {
        className: `text-center py-4 ${className}`
    }, [
        React.createElement('div', {
            key: 'spinner',
            className: `spinner-border ${sizeClass}`,
            role: 'status'
        }, React.createElement('span', {
            className: 'visually-hidden'
        }, 'Loading...')),
        text ? React.createElement('div', {
            key: 'text',
            className: 'mt-2'
        }, text) : null
    ]);
};

console.log('TestPark 공통 React 컴포넌트 라이브러리가 로드되었습니다.');