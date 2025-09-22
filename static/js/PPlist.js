// API 통합 PPlist React Component
const { useState, useEffect, useCallback } = React;
const { Search, Plus, Copy, FileText, Send, X, Edit2, MessageSquare, FileText: QuoteIcon } = lucide;

// API 서비스
const api = {
    // 의뢰 목록 조회
    getOrders: async (params = {}) => {
        const response = await axios.get('/orders/', { params });
        return response.data;
    },

    // 의뢰 상세 조회
    getOrder: async (id) => {
        const response = await axios.get(`/orders/${id}/`);
        return response.data;
    },

    // 필드 수정
    updateField: async (id, data) => {
        const response = await axios.post(`/orders/${id}/update_field/`, data);
        return response.data;
    },

    // 상태 변경
    updateStatus: async (id, data) => {
        const response = await axios.post(`/orders/${id}/update_status/`, data);
        return response.data;
    },

    // 메모 추가
    addMemo: async (id, data) => {
        const response = await axios.post(`/orders/${id}/add_memo/`, data);
        return response.data;
    },

    // 견적 링크 추가
    addQuoteLink: async (id, data) => {
        const response = await axios.post(`/orders/${id}/add_quote_link/`, data);
        return response.data;
    },

    // 의뢰 복사
    copyOrder: async (id) => {
        const response = await axios.post(`/orders/${id}/copy/`);
        return response.data;
    },

    // 선택 삭제
    bulkDelete: async (orderIds) => {
        const response = await axios.post('/orders/bulk_delete/', { order_ids: orderIds });
        return response.data;
    },

    // 업체 할당
    assignCompanies: async (data) => {
        const response = await axios.post('/orders/assign_companies/', data);
        return response.data;
    },

    // 업체 목록 조회
    getCompanies: async () => {
        const response = await axios.get('/companies/');
        return response.data;
    },

    // 공동구매 목록 조회
    getGroupPurchases: async () => {
        const response = await axios.get('/group-purchases/');
        return response.data;
    },

    // 메시지 템플릿 조회
    getMessageTemplates: async () => {
        const response = await axios.get('/message-templates/');
        return response.data;
    },

    // TODO(human): API 응답 에러 처리 함수를 구현해주세요.
    // 이 함수는 API 호출이 실패했을 때 사용자에게 적절한 에러 메시지를 표시해야 합니다.
    // 에러 상태 코드(400, 401, 403, 404, 500 등)에 따라 다른 메시지를 표시하면 좋습니다.
};

const QuoteManagementSystem = () => {
    const [currentPage, setCurrentPage] = useState('list');
    const [expandedRow, setExpandedRow] = useState(null);
    const [showPostModal, setShowPostModal] = useState(false);
    const [showMessageModal, setShowMessageModal] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [showQuoteModal, setShowQuoteModal] = useState(false);
    const [showMemoModal, setShowMemoModal] = useState(false);
    const [showStatusModal, setShowStatusModal] = useState(false);
    const [selectedQuoteId, setSelectedQuoteId] = useState(null);
    const [selectedQuoteForModal, setSelectedQuoteForModal] = useState(null);
    const [messageTemplate, setMessageTemplate] = useState('템플릿1');
    const [messageRecipient, setMessageRecipient] = useState('업체+고객');
    const [selectedCompanies, setSelectedCompanies] = useState([]);
    const [selectedServices, setSelectedServices] = useState([]);
    const [selectedRows, setSelectedRows] = useState([]);

    // API에서 가져온 데이터
    const [quoteRequestsData, setQuoteRequestsData] = useState([]);
    const [companies, setCompanies] = useState([]);
    const [groupPurchases, setGroupPurchases] = useState([]);
    const [messageTemplates, setMessageTemplates] = useState({});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // 상태 전환 규칙
    const statusTransitions = {
        '대기중': ['할당', '업체미비', '중복접수', '연락처오류', '가능문의', '고객문의'],
        '할당': ['반려', '취소', '제외', '연락처오류', '계약'],
        '연락처오류': ['대기중', '할당'],
        '가능문의': ['할당', '불가능답변(X)'],
        '반려': ['대기중', '할당', '계약'],
        '고객문의': ['대기중', '할당'],
        '취소': ['계약'],
        '제외': [],
        '업체미비': ['대기중'],
        '중복접수': [],
        '불가능답변(X)': ['대기중'],
        '계약': []
    };

    const customerInquiryTemplates = {
        '내용문의': '평수만 있거나 공사내용을 알 수 없는 경우에 고객에게 문의',
        '주소문의': '공사 지역이 비어있거나, 건물형태만 있는 경우 또는 시구동만 있는 경우인지 고객에게 문의',
        '주소내용문의': '평수만 있거나 공사내용을 알 수 없는 경우 + 공사 지역이 비어있거나, 건물형태만 있는 경우 또는 시구동만 있는 경우',
        '공사일정문의': '고객이 공사 일정을 적지 않은 경우, 고객께 문의 또는 안내',
        '공사일정먼경우': '고객께 문의 또는 안내',
        '공사일정촉박': '고객께 문의 또는 안내'
    };

    // 데이터 로드
    useEffect(() => {
        loadInitialData();
    }, []);

    const loadInitialData = async () => {
        setLoading(true);
        try {
            const [ordersData, companiesData, purchasesData, templatesData] = await Promise.all([
                api.getOrders(),
                api.getCompanies(),
                api.getGroupPurchases(),
                api.getMessageTemplates()
            ]);

            // Orders 데이터 변환
            const transformedOrders = ordersData.results ? ordersData.results : ordersData;
            const ordersWithCorrectFormat = transformedOrders.map(order => ({
                id: order.no,
                receiptDate: new Date(order.receipt_date || order.time).toISOString().slice(0, 16).replace('T', ' '),
                designation: order.designation || order.sAppoint || '',
                designationType: order.designation_type || '지정없음',
                nickname: order.sNick || '',
                naverId: order.sNaverID || '',
                name: order.sName || '',
                phone: order.sPhone || '',
                postLink: order.post_link || order.sPost || '',
                area: order.sArea || '',
                scheduledDate: order.dateSchedule || '',
                workContent: order.sConstruction || '',
                assignedCompany: order.assigned_company || '',
                recentStatus: order.recent_status || '대기중',
                reRequestCount: order.re_request_count || 0,
                quoteCount: 0,
                memoCount: 0
            }));

            setQuoteRequestsData(ordersWithCorrectFormat);
            setCompanies(companiesData);
            setGroupPurchases(purchasesData);
            setMessageTemplates(templatesData);
        } catch (err) {
            console.error('데이터 로드 실패:', err);
            setError('데이터를 불러오는데 실패했습니다.');
        } finally {
            setLoading(false);
        }
    };

    // 선택 관련 함수
    const handleSelectAll = (e) => {
        if (e.target.checked) {
            setSelectedRows(quoteRequestsData.map(item => item.id));
        } else {
            setSelectedRows([]);
        }
    };

    const handleSelectRow = (id) => {
        if (selectedRows.includes(id)) {
            setSelectedRows(selectedRows.filter(rowId => rowId !== id));
        } else {
            setSelectedRows([...selectedRows, id]);
        }
    };

    const handleDeleteSelected = async () => {
        if (selectedRows.length === 0) {
            alert('삭제할 항목을 선택해주세요.');
            return;
        }

        const confirmMessage = selectedRows.length === 1
            ? '선택한 1개 항목을 삭제하시겠습니까?'
            : `선택한 ${selectedRows.length}개 항목을 삭제하시겠습니까?`;

        if (window.confirm(confirmMessage)) {
            try {
                await api.bulkDelete(selectedRows);
                setQuoteRequestsData(prev =>
                    prev.filter(item => !selectedRows.includes(item.id))
                );
                setSelectedRows([]);
                alert('삭제되었습니다.');
            } catch (err) {
                console.error('삭제 실패:', err);
                alert('삭제에 실패했습니다.');
            }
        }
    };

    // 필드 편집 관련
    const [editField, setEditField] = useState({
        fieldName: '',
        fieldLabel: '',
        currentValue: '',
        newValue: '',
        quoteId: null
    });

    const [statusFormData, setStatusFormData] = useState({
        status: '대기중',
        template: '',
        recipient: '업체+고객',
        messageContent: ''
    });

    const fieldLabels = {
        designation: '지정',
        nickname: '별명',
        naverId: '네이버ID',
        name: '이름',
        phone: '전화번호',
        area: '공사지역',
        scheduledDate: '공사예정일',
        workContent: '공사내용'
    };

    const openEditModal = (quoteId, fieldName, currentValue) => {
        setEditField({
            fieldName,
            fieldLabel: fieldLabels[fieldName],
            currentValue,
            newValue: currentValue,
            quoteId
        });
        setShowEditModal(true);
    };

    const saveFieldEdit = async () => {
        if (editField.currentValue !== editField.newValue) {
            try {
                await api.updateField(editField.quoteId, {
                    field_name: editField.fieldName,
                    field_label: editField.fieldLabel,
                    new_value: editField.newValue,
                    author: '관리자'
                });

                setQuoteRequestsData(prev =>
                    prev.map(item =>
                        item.id === editField.quoteId
                            ? { ...item, [editField.fieldName]: editField.newValue }
                            : item
                    )
                );

                setShowEditModal(false);
                alert('수정되었습니다.');
            } catch (err) {
                console.error('필드 수정 실패:', err);
                alert('수정에 실패했습니다.');
            }
        } else {
            setShowEditModal(false);
        }
    };

    // 상태 변경 관련
    const openStatusModal = (quoteId) => {
        const quote = quoteRequestsData.find(q => q.id === quoteId);
        setSelectedQuoteForModal(quoteId);
        setStatusFormData({
            status: quote.recentStatus,
            template: '',
            recipient: '업체+고객',
            messageContent: ''
        });
        setShowStatusModal(true);
    };

    const handleStatusChange = (newStatus) => {
        const quote = quoteRequestsData.find(q => q.id === selectedQuoteForModal);
        const template = messageTemplates[newStatus];
        let messageContent = '';

        if (template && quote) {
            messageContent = template
                .replace('{name}', quote.name)
                .replace('{workContent}', quote.workContent);
        }

        setStatusFormData({
            ...statusFormData,
            status: newStatus,
            template: newStatus,
            messageContent
        });
    };

    const updateStatus = async (sendMessage) => {
        const currentQuote = quoteRequestsData.find(q => q.id === selectedQuoteForModal);

        try {
            await api.updateStatus(selectedQuoteForModal, {
                status: statusFormData.status,
                message_sent: sendMessage,
                message_content: statusFormData.messageContent,
                recipient: statusFormData.recipient,
                author: '관리자'
            });

            setQuoteRequestsData(prev =>
                prev.map(item =>
                    item.id === selectedQuoteForModal
                        ? { ...item, recentStatus: statusFormData.status }
                        : item
                )
            );

            setShowStatusModal(false);
            alert('상태가 변경되었습니다.');
        } catch (err) {
            console.error('상태 변경 실패:', err);
            alert(err.response?.data?.message || '상태 변경에 실패했습니다.');
        }
    };

    // 메모 관련
    const openMemoModal = (quoteId) => {
        setSelectedQuoteForModal(quoteId);
        setShowMemoModal(true);
    };

    const addMemo = async (content) => {
        try {
            const result = await api.addMemo(selectedQuoteForModal, {
                content,
                author: '관리자'
            });

            // 메모 카운트 업데이트
            setQuoteRequestsData(prev =>
                prev.map(item =>
                    item.id === selectedQuoteForModal
                        ? { ...item, memoCount: item.memoCount + 1 }
                        : item
                )
            );

            alert('메모가 추가되었습니다.');
            return result.memo;
        } catch (err) {
            console.error('메모 추가 실패:', err);
            alert('메모 추가에 실패했습니다.');
        }
    };

    // 견적서 관련
    const openQuoteModal = (quoteId) => {
        setSelectedQuoteForModal(quoteId);
        setShowQuoteModal(true);
    };

    const addQuoteLink = async (draftType, link) => {
        try {
            const result = await api.addQuoteLink(selectedQuoteForModal, {
                draft_type: draftType,
                link
            });

            // 견적서 카운트 업데이트
            setQuoteRequestsData(prev =>
                prev.map(item =>
                    item.id === selectedQuoteForModal
                        ? { ...item, quoteCount: item.quoteCount + 1 }
                        : item
                )
            );

            alert('견적서 링크가 추가되었습니다.');
            return result.draft;
        } catch (err) {
            console.error('견적서 추가 실패:', err);
            alert('견적서 추가에 실패했습니다.');
        }
    };

    // 의뢰 복사
    const copyQuoteRequest = async (item) => {
        try {
            const newOrder = await api.copyOrder(item.id);

            const newItem = {
                id: newOrder.no,
                receiptDate: new Date(newOrder.receipt_date || newOrder.time).toISOString().slice(0, 16).replace('T', ' '),
                designation: newOrder.designation || '',
                designationType: newOrder.designation_type || '지정없음',
                nickname: newOrder.sNick || '',
                naverId: newOrder.sNaverID || '',
                name: newOrder.sName || '',
                phone: newOrder.sPhone || '',
                postLink: '',
                area: newOrder.sArea || '',
                scheduledDate: newOrder.dateSchedule || '',
                workContent: newOrder.sConstruction || '',
                assignedCompany: '',
                recentStatus: '대기중',
                reRequestCount: 0,
                quoteCount: 0,
                memoCount: 0
            };

            setQuoteRequestsData([...quoteRequestsData, newItem]);
            alert('의뢰가 복사되었습니다.');
        } catch (err) {
            console.error('복사 실패:', err);
            alert('복사에 실패했습니다.');
        }
    };

    // 행 확장
    const toggleRowExpansion = (id) => {
        setExpandedRow(expandedRow === id ? null : id);
    };

    const extractPostNumber = (url) => {
        const match = url.match(/\/(\d{6})$/);
        return match ? match[1] : '';
    };

    // 업체 할당
    const handleCompanyAllocation = async (quoteId, companyIds, serviceIds) => {
        try {
            await api.assignCompanies({
                order_id: quoteId,
                company_ids: companyIds,
                service_ids: serviceIds
            });

            await loadInitialData();
            alert('업체가 할당되었습니다.');
            setExpandedRow(null);
        } catch (err) {
            console.error('업체 할당 실패:', err);
            alert('업체 할당에 실패했습니다.');
        }
    };

    // 모달 컴포넌트들
    const EditModal = () => (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg w-[500px]">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold">{editField.fieldLabel} 수정</h3>
                    <button
                        onClick={() => setShowEditModal(false)}
                        className="text-gray-500 hover:text-gray-700"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="mb-4">
                    <label className="block text-sm font-medium mb-2">현재 값</label>
                    <div className="p-2 bg-gray-100 rounded">{editField.currentValue}</div>
                </div>

                <div className="mb-4">
                    <label className="block text-sm font-medium mb-2">새로운 값</label>
                    {editField.fieldName === 'workContent' || editField.fieldName === 'area' ? (
                        <textarea
                            value={editField.newValue}
                            onChange={(e) => setEditField({...editField, newValue: e.target.value})}
                            className="w-full p-2 border rounded h-24"
                        />
                    ) : editField.fieldName === 'scheduledDate' ? (
                        <input
                            type="date"
                            value={editField.newValue}
                            onChange={(e) => setEditField({...editField, newValue: e.target.value})}
                            className="w-full p-2 border rounded"
                        />
                    ) : (
                        <input
                            type="text"
                            value={editField.newValue}
                            onChange={(e) => setEditField({...editField, newValue: e.target.value})}
                            className="w-full p-2 border rounded"
                        />
                    )}
                </div>

                <div className="flex justify-end space-x-2">
                    <button
                        onClick={() => setShowEditModal(false)}
                        className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
                    >
                        취소
                    </button>
                    <button
                        onClick={saveFieldEdit}
                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                        저장
                    </button>
                </div>
            </div>
        </div>
    );

    const StatusModal = () => {
        const quote = quoteRequestsData.find(q => q.id === selectedQuoteForModal);
        const currentStatus = quote?.recentStatus || '대기중';
        const hasAssignedCompany = quote?.assignedCompany && quote.assignedCompany !== '';

        let availableStatuses = statusTransitions[currentStatus] || [];

        if (currentStatus === '연락처오류' && !hasAssignedCompany) {
            availableStatuses = availableStatuses.filter(s => s !== '할당');
        }

        return (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white p-6 rounded-lg w-[600px] max-h-[90vh] overflow-y-auto">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-bold">할당상태 변경</h3>
                        <button
                            onClick={() => setShowStatusModal(false)}
                            className="text-gray-500 hover:text-gray-700"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    <div className="mb-4 p-3 bg-blue-50 rounded">
                        <div className="text-sm">
                            <span className="font-medium">현재 상태:</span>
                            <span className="ml-2 px-2 py-1 rounded text-xs bg-gray-100 text-gray-700">
                                {currentStatus}
                            </span>
                            {quote?.assignedCompany && (
                                <>
                                    <span className="ml-4 font-medium">할당업체:</span>
                                    <span className="ml-2 text-blue-600">{quote.assignedCompany}</span>
                                </>
                            )}
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">1. 상태 선택</label>
                            <select
                                value={statusFormData.status}
                                onChange={(e) => handleStatusChange(e.target.value)}
                                className="w-full p-2 border rounded"
                            >
                                <option value={currentStatus}>{currentStatus}</option>
                                {availableStatuses.map(status => (
                                    <option key={status} value={status}>{status}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">2. 수신자 선택</label>
                            <select
                                value={statusFormData.recipient}
                                onChange={(e) => setStatusFormData({...statusFormData, recipient: e.target.value})}
                                className="w-full p-2 border rounded"
                            >
                                <option value="업체+고객">업체+고객</option>
                                <option value="업체">업체</option>
                                <option value="고객">고객</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">3. 할당 문자 내용</label>
                            <textarea
                                value={statusFormData.messageContent}
                                onChange={(e) => setStatusFormData({...statusFormData, messageContent: e.target.value})}
                                className="w-full p-2 border rounded h-32"
                                placeholder="문자 내용을 입력하세요..."
                            />
                        </div>

                        <div className="flex justify-end space-x-2">
                            <button
                                onClick={() => setShowStatusModal(false)}
                                className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
                            >
                                취소
                            </button>
                            <button
                                onClick={() => updateStatus(false)}
                                disabled={availableStatuses.length === 0}
                                className="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600"
                            >
                                문자 안보내고 상태변경
                            </button>
                            <button
                                onClick={() => updateStatus(true)}
                                disabled={availableStatuses.length === 0}
                                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                            >
                                문자 보내고 상태변경
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    const MemoModal = () => {
        const [newMemo, setNewMemo] = useState('');

        const handleAddMemo = async () => {
            if (newMemo.trim()) {
                await addMemo(newMemo);
                setNewMemo('');
            }
        };

        return (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white p-6 rounded-lg w-[600px] max-h-[80vh] overflow-y-auto">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-bold">메모 관리</h3>
                        <button
                            onClick={() => setShowMemoModal(false)}
                            className="text-gray-500 hover:text-gray-700"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    <div className="mb-6">
                        <h4 className="font-medium mb-2">메모 입력</h4>
                        <textarea
                            value={newMemo}
                            onChange={(e) => setNewMemo(e.target.value)}
                            className="w-full p-2 border rounded h-24 mb-2"
                            placeholder="메모를 입력하세요..."
                        />
                        <button
                            onClick={handleAddMemo}
                            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                            메모 추가
                        </button>
                    </div>

                    <div className="flex justify-end">
                        <button
                            onClick={() => setShowMemoModal(false)}
                            className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
                        >
                            닫기
                        </button>
                    </div>
                </div>
            </div>
        );
    };

    const QuoteModal = () => {
        const [draftLink, setDraftLink] = useState('');

        const handleAddQuote = async () => {
            if (draftLink) {
                await addQuoteLink('초안', draftLink);
                setDraftLink('');
            }
        };

        return (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white p-6 rounded-lg w-[600px] max-h-[80vh] overflow-y-auto">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-bold">견적서 관리</h3>
                        <button
                            onClick={() => setShowQuoteModal(false)}
                            className="text-gray-500 hover:text-gray-700"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    <div className="mb-6">
                        <h4 className="font-medium mb-2">견적서 링크 추가</h4>
                        <div className="flex space-x-2">
                            <input
                                type="url"
                                value={draftLink}
                                onChange={(e) => setDraftLink(e.target.value)}
                                className="flex-1 p-2 border rounded"
                                placeholder="견적서 링크 입력"
                            />
                            <button
                                onClick={handleAddQuote}
                                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                            >
                                추가
                            </button>
                        </div>
                    </div>

                    <div className="flex justify-end">
                        <button
                            onClick={() => setShowQuoteModal(false)}
                            className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
                        >
                            닫기
                        </button>
                    </div>
                </div>
            </div>
        );
    };

    // 메인 리스트 페이지
    const QuoteListPage = () => (
        <div className="p-6">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">견적의뢰 관리</h1>
                <div className="flex space-x-2">
                    {selectedRows.length > 0 && (
                        <button
                            onClick={handleDeleteSelected}
                            className="bg-red-500 text-white px-4 py-2 rounded flex items-center hover:bg-red-600"
                        >
                            선택 삭제 ({selectedRows.length})
                        </button>
                    )}
                    <button
                        onClick={() => window.open('https://docs.google.com/forms/d/e/1FAIpQLSfOnhe1eBTRM5bb-r_XA6epsUkPctmqexzcwJk-MC5KlC3F4g/viewform', '_blank')}
                        className="bg-blue-500 text-white px-4 py-2 rounded flex items-center hover:bg-blue-600"
                    >
                        <Plus className="w-4 h-4 mr-2" />
                        추가
                    </button>
                </div>
            </div>

            {error && (
                <div className="mb-4 p-4 bg-red-100 text-red-700 rounded">
                    {error}
                </div>
            )}

            {loading ? (
                <div className="text-center py-8">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                    <p className="mt-2">데이터 로딩 중...</p>
                </div>
            ) : (
                <div className="overflow-x-auto">
                    <table className="w-full border-collapse border border-gray-300">
                        <thead>
                            <tr className="bg-gray-100">
                                <th className="border p-2 w-10">
                                    <input
                                        type="checkbox"
                                        onChange={handleSelectAll}
                                        checked={selectedRows.length === quoteRequestsData.length && quoteRequestsData.length > 0}
                                    />
                                </th>
                                <th className="border p-2">접수일시</th>
                                <th className="border p-2 w-40">지정</th>
                                <th className="border p-2">별명</th>
                                <th className="border p-2">네이버ID</th>
                                <th className="border p-2">이름</th>
                                <th className="border p-2">전화번호</th>
                                <th className="border p-2">의뢰게시글</th>
                                <th className="border p-2 w-32">공사지역</th>
                                <th className="border p-2">공사예정일</th>
                                <th className="border p-2">공사내용</th>
                                <th className="border p-2">할당업체명</th>
                                <th className="border p-2">최근할당상태</th>
                                <th className="border p-2">재의뢰</th>
                                <th className="border p-2">견적</th>
                                <th className="border p-2">메모</th>
                                <th className="border p-2">액션</th>
                            </tr>
                        </thead>
                        <tbody>
                            {quoteRequestsData
                                .sort((a, b) => new Date(b.receiptDate) - new Date(a.receiptDate))
                                .map(item => (
                                <React.Fragment key={item.id}>
                                    <tr className={`hover:bg-gray-50 ${selectedRows.includes(item.id) ? 'bg-blue-50' : ''}`}>
                                        <td className="border p-2 text-center">
                                            <input
                                                type="checkbox"
                                                checked={selectedRows.includes(item.id)}
                                                onChange={() => handleSelectRow(item.id)}
                                            />
                                        </td>
                                        <td className="border p-2 text-sm">{item.receiptDate}</td>
                                        <td
                                            className="border p-2 text-xs max-w-40 cursor-pointer hover:bg-yellow-50"
                                            onDoubleClick={() => openEditModal(item.id, 'designation', item.designation)}
                                        >
                                            <div className="break-words">{item.designation}</div>
                                        </td>
                                        <td
                                            className="border p-2 cursor-pointer hover:bg-yellow-50"
                                            onDoubleClick={() => openEditModal(item.id, 'nickname', item.nickname)}
                                        >
                                            {item.nickname}
                                        </td>
                                        <td
                                            className="border p-2 cursor-pointer hover:bg-yellow-50"
                                            onDoubleClick={() => openEditModal(item.id, 'naverId', item.naverId)}
                                        >
                                            {item.naverId}
                                        </td>
                                        <td
                                            className="border p-2 cursor-pointer hover:bg-yellow-50"
                                            onDoubleClick={() => openEditModal(item.id, 'name', item.name)}
                                        >
                                            {item.name}
                                        </td>
                                        <td
                                            className="border p-2 cursor-pointer hover:bg-yellow-50"
                                            onDoubleClick={() => openEditModal(item.id, 'phone', item.phone)}
                                        >
                                            {item.phone}
                                        </td>
                                        <td className="border p-2">
                                            {item.postLink ? (
                                                <a
                                                    href={item.postLink}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="text-blue-500 hover:underline"
                                                >
                                                    {extractPostNumber(item.postLink) || '링크'}
                                                </a>
                                            ) : (
                                                <span className="bg-orange-500 text-white px-2 py-1 rounded text-xs">
                                                    대기중
                                                </span>
                                            )}
                                        </td>
                                        <td
                                            className="border p-2 text-sm cursor-pointer hover:bg-yellow-50"
                                            onDoubleClick={() => openEditModal(item.id, 'area', item.area)}
                                        >
                                            {item.area}
                                        </td>
                                        <td
                                            className="border p-2 cursor-pointer hover:bg-yellow-50"
                                            onDoubleClick={() => openEditModal(item.id, 'scheduledDate', item.scheduledDate)}
                                        >
                                            {item.scheduledDate}
                                        </td>
                                        <td
                                            className="border p-2 cursor-pointer hover:bg-yellow-50"
                                            onDoubleClick={() => openEditModal(item.id, 'workContent', item.workContent)}
                                        >
                                            {item.workContent}
                                        </td>
                                        <td
                                            className="border p-2 cursor-pointer hover:bg-blue-100"
                                            onClick={() => toggleRowExpansion(item.id)}
                                        >
                                            {item.assignedCompany ? (
                                                <span className="text-blue-600 underline">{item.assignedCompany}</span>
                                            ) : (
                                                <button className="bg-orange-500 text-white px-2 py-1 rounded text-xs hover:bg-orange-600">
                                                    대기중
                                                </button>
                                            )}
                                        </td>
                                        <td
                                            className="border p-2 cursor-pointer hover:bg-blue-100"
                                            onClick={() => openStatusModal(item.id)}
                                        >
                                            <span className={`px-2 py-1 rounded text-xs ${
                                                item.recentStatus === '대기중' ? 'bg-gray-100 text-gray-700' :
                                                item.recentStatus === '할당' ? 'bg-blue-100 text-blue-700' :
                                                item.recentStatus === '반려' ? 'bg-red-100 text-red-700' :
                                                item.recentStatus === '취소' ? 'bg-gray-100 text-gray-700' :
                                                item.recentStatus === '제외' ? 'bg-gray-100 text-gray-700' :
                                                item.recentStatus === '업체미비' ? 'bg-yellow-100 text-yellow-700' :
                                                item.recentStatus === '중복접수' ? 'bg-purple-100 text-purple-700' :
                                                item.recentStatus === '연락처오류' ? 'bg-orange-100 text-orange-700' :
                                                item.recentStatus === '가능문의' ? 'bg-blue-100 text-blue-700' :
                                                item.recentStatus === '불가능답변(X)' ? 'bg-red-100 text-red-700' :
                                                item.recentStatus === '고객문의' ? 'bg-green-100 text-green-700' :
                                                item.recentStatus === '계약' ? 'bg-green-100 text-green-700' :
                                                'bg-gray-100 text-gray-700'
                                            }`}>
                                                {item.recentStatus}
                                            </span>
                                        </td>
                                        <td className="border p-2">
                                            <button className="text-blue-500 hover:underline">
                                                {item.reRequestCount}
                                            </button>
                                        </td>
                                        <td className="border p-2">
                                            <button
                                                className="text-blue-500 hover:underline"
                                                onClick={() => openQuoteModal(item.id)}
                                            >
                                                {item.quoteCount}
                                            </button>
                                        </td>
                                        <td className="border p-2">
                                            <button
                                                className="text-blue-500 hover:underline"
                                                onClick={() => openMemoModal(item.id)}
                                            >
                                                {item.memoCount}
                                            </button>
                                        </td>
                                        <td className="border p-2">
                                            <div className="flex space-x-1">
                                                <button
                                                    onClick={() => copyQuoteRequest(item)}
                                                    className="bg-gray-500 text-white px-2 py-1 rounded text-xs hover:bg-gray-600"
                                                >
                                                    <Copy className="w-3 h-3" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                    {expandedRow === item.id && (
                                        <tr>
                                            <td colSpan="17" className="border-0 p-0">
                                                <div className="bg-blue-50 border-l-4 border-blue-500 p-4 m-2">
                                                    <h3 className="font-bold text-lg mb-4">업체할당 정보</h3>
                                                    <p className="text-sm text-gray-600">
                                                        업체 할당 기능이 여기에 표시됩니다.
                                                    </p>
                                                </div>
                                            </td>
                                        </tr>
                                    )}
                                </React.Fragment>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );

    return (
        <div className="min-h-screen bg-gray-100">
            <nav className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4">
                    <div className="flex justify-between items-center h-16">
                        <h1 className="text-xl font-bold text-gray-900">견적의뢰 관리 시스템</h1>
                    </div>
                </div>
            </nav>

            <QuoteListPage />

            {showEditModal && <EditModal />}
            {showStatusModal && <StatusModal />}
            {showQuoteModal && <QuoteModal />}
            {showMemoModal && <MemoModal />}
        </div>
    );
};

// React 컴포넌트 렌더링
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<QuoteManagementSystem />);