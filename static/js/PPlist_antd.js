// Ant Design 기반 PPlist React Component
const { useState, useEffect, useCallback, useMemo } = React;
const {
    Table, Button, Modal, Form, Input, Select, DatePicker, Space, Tag,
    message, notification, Drawer, Card, Tabs, Badge, Tooltip, Popconfirm,
    Row, Col, Divider, Alert, Spin, Typography, Dropdown, Menu, Checkbox,
    InputNumber, TextArea, Upload, Timeline, Collapse, Descriptions
} = antd;
const {
    SearchOutlined, PlusOutlined, CopyOutlined, FileTextOutlined,
    SendOutlined, EditOutlined, DeleteOutlined, DownloadOutlined,
    TeamOutlined, CalendarOutlined, PhoneOutlined, UserOutlined,
    HomeOutlined, ToolOutlined, MessageOutlined, LinkOutlined,
    CheckCircleOutlined, CloseCircleOutlined, SyncOutlined,
    ExclamationCircleOutlined, ClockCircleOutlined
} = icons;

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { Panel } = Collapse;
const { RangePicker } = DatePicker;

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

    // 에러 처리
    handleError: (error) => {
        if (error.response) {
            const status = error.response.status;
            const errorMessage = error.response.data?.message || error.response.data?.detail;

            switch (status) {
                case 400:
                    message.error(errorMessage || '잘못된 요청입니다.');
                    break;
                case 401:
                    message.error('인증이 필요합니다. 다시 로그인해주세요.');
                    break;
                case 403:
                    message.error('권한이 없습니다.');
                    break;
                case 404:
                    message.error('요청한 데이터를 찾을 수 없습니다.');
                    break;
                case 500:
                    message.error('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
                    break;
                default:
                    message.error(errorMessage || '오류가 발생했습니다.');
            }
        } else if (error.request) {
            message.error('네트워크 연결을 확인해주세요.');
        } else {
            message.error('오류가 발생했습니다.');
        }
    }
};

const QuoteManagementSystem = () => {
    const [loading, setLoading] = useState(false);
    const [tableLoading, setTableLoading] = useState(false);
    const [selectedRowKeys, setSelectedRowKeys] = useState([]);
    const [searchText, setSearchText] = useState('');
    const [searchedColumn, setSearchedColumn] = useState('');
    const [filteredInfo, setFilteredInfo] = useState({});
    const [sortedInfo, setSortedInfo] = useState({});

    // 모달 상태
    const [editModalVisible, setEditModalVisible] = useState(false);
    const [statusModalVisible, setStatusModalVisible] = useState(false);
    const [memoModalVisible, setMemoModalVisible] = useState(false);
    const [quoteModalVisible, setQuoteModalVisible] = useState(false);
    const [companyDrawerVisible, setCompanyDrawerVisible] = useState(false);
    const [currentRecord, setCurrentRecord] = useState(null);

    // 폼
    const [editForm] = Form.useForm();
    const [statusForm] = Form.useForm();
    const [memoForm] = Form.useForm();
    const [quoteForm] = Form.useForm();

    // 데이터
    const [orders, setOrders] = useState([]);
    const [companies, setCompanies] = useState([]);
    const [groupPurchases, setGroupPurchases] = useState([]);
    const [messageTemplates, setMessageTemplates] = useState({});

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

    // 상태별 태그 색상
    const getStatusColor = (status) => {
        const colorMap = {
            '대기중': 'default',
            '할당': 'processing',
            '반려': 'error',
            '취소': 'default',
            '제외': 'default',
            '업체미비': 'warning',
            '중복접수': 'purple',
            '연락처오류': 'orange',
            '가능문의': 'processing',
            '불가능답변(X)': 'error',
            '고객문의': 'success',
            '계약': 'success'
        };
        return colorMap[status] || 'default';
    };

    // 데이터 로드
    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setTableLoading(true);
        try {
            const [ordersData, companiesData, purchasesData, templatesData] = await Promise.all([
                api.getOrders(),
                api.getCompanies(),
                api.getGroupPurchases(),
                api.getMessageTemplates()
            ]);

            // Orders 데이터 변환
            const transformedOrders = (ordersData.results || ordersData).map(order => ({
                key: order.no,
                id: order.no,
                receiptDate: order.receipt_date || order.time,
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

            setOrders(transformedOrders);
            setCompanies(companiesData);
            setGroupPurchases(purchasesData);
            setMessageTemplates(templatesData);
        } catch (error) {
            api.handleError(error);
        } finally {
            setTableLoading(false);
        }
    };

    // 검색 기능
    const handleSearch = (selectedKeys, confirm, dataIndex) => {
        confirm();
        setSearchText(selectedKeys[0]);
        setSearchedColumn(dataIndex);
    };

    const handleReset = (clearFilters) => {
        clearFilters();
        setSearchText('');
    };

    const getColumnSearchProps = (dataIndex, title) => ({
        filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => (
            <div style={{ padding: 8 }}>
                <Input
                    placeholder={`${title} 검색`}
                    value={selectedKeys[0]}
                    onChange={(e) => setSelectedKeys(e.target.value ? [e.target.value] : [])}
                    onPressEnter={() => handleSearch(selectedKeys, confirm, dataIndex)}
                    style={{ marginBottom: 8, display: 'block' }}
                />
                <Space>
                    <Button
                        type="primary"
                        onClick={() => handleSearch(selectedKeys, confirm, dataIndex)}
                        icon={<SearchOutlined />}
                        size="small"
                        style={{ width: 90 }}
                    >
                        검색
                    </Button>
                    <Button
                        onClick={() => handleReset(clearFilters)}
                        size="small"
                        style={{ width: 90 }}
                    >
                        초기화
                    </Button>
                </Space>
            </div>
        ),
        filterIcon: (filtered) => <SearchOutlined style={{ color: filtered ? '#1890ff' : undefined }} />,
        onFilter: (value, record) =>
            record[dataIndex]?.toString().toLowerCase().includes(value.toLowerCase()),
    });

    // 테이블 컬럼 정의
    const columns = [
        {
            title: '접수일시',
            dataIndex: 'receiptDate',
            key: 'receiptDate',
            width: 150,
            sorter: (a, b) => new Date(a.receiptDate) - new Date(b.receiptDate),
            render: (date) => dayjs(date).format('YYYY-MM-DD HH:mm'),
        },
        {
            title: '지정',
            dataIndex: 'designation',
            key: 'designation',
            width: 150,
            ellipsis: true,
            ...getColumnSearchProps('designation', '지정'),
        },
        {
            title: '이름',
            dataIndex: 'name',
            key: 'name',
            width: 100,
            ...getColumnSearchProps('name', '이름'),
            render: (text, record) => (
                <Tooltip title="더블클릭으로 수정">
                    <div
                        style={{ cursor: 'pointer' }}
                        onDoubleClick={() => handleEditField(record, 'name', text)}
                    >
                        {text || '-'}
                    </div>
                </Tooltip>
            ),
        },
        {
            title: '전화번호',
            dataIndex: 'phone',
            key: 'phone',
            width: 120,
            ...getColumnSearchProps('phone', '전화번호'),
            render: (text, record) => (
                <Tooltip title="더블클릭으로 수정">
                    <div
                        style={{ cursor: 'pointer' }}
                        onDoubleClick={() => handleEditField(record, 'phone', text)}
                    >
                        {text || '-'}
                    </div>
                </Tooltip>
            ),
        },
        {
            title: '공사지역',
            dataIndex: 'area',
            key: 'area',
            width: 200,
            ellipsis: true,
            ...getColumnSearchProps('area', '지역'),
            render: (text, record) => (
                <Tooltip title={text}>
                    <div
                        style={{ cursor: 'pointer' }}
                        onDoubleClick={() => handleEditField(record, 'area', text)}
                    >
                        {text || '-'}
                    </div>
                </Tooltip>
            ),
        },
        {
            title: '공사예정일',
            dataIndex: 'scheduledDate',
            key: 'scheduledDate',
            width: 120,
            sorter: (a, b) => new Date(a.scheduledDate) - new Date(b.scheduledDate),
            render: (date, record) => (
                <Tooltip title="더블클릭으로 수정">
                    <div
                        style={{ cursor: 'pointer' }}
                        onDoubleClick={() => handleEditField(record, 'scheduledDate', date)}
                    >
                        {date || '-'}
                    </div>
                </Tooltip>
            ),
        },
        {
            title: '공사내용',
            dataIndex: 'workContent',
            key: 'workContent',
            width: 200,
            ellipsis: true,
            ...getColumnSearchProps('workContent', '공사내용'),
            render: (text, record) => (
                <Tooltip title={text}>
                    <div
                        style={{ cursor: 'pointer' }}
                        onDoubleClick={() => handleEditField(record, 'workContent', text)}
                    >
                        {text || '-'}
                    </div>
                </Tooltip>
            ),
        },
        {
            title: '할당업체',
            dataIndex: 'assignedCompany',
            key: 'assignedCompany',
            width: 150,
            render: (text, record) => (
                <div
                    style={{ cursor: 'pointer' }}
                    onClick={() => handleCompanyDrawer(record)}
                >
                    {text ? (
                        <Text type="secondary" underline>{text}</Text>
                    ) : (
                        <Button type="link" size="small" style={{ padding: 0 }}>
                            <Badge status="warning" text="대기중" />
                        </Button>
                    )}
                </div>
            ),
        },
        {
            title: '상태',
            dataIndex: 'recentStatus',
            key: 'recentStatus',
            width: 100,
            filters: Object.keys(statusTransitions).map(status => ({ text: status, value: status })),
            onFilter: (value, record) => record.recentStatus === value,
            render: (status, record) => (
                <Tag
                    color={getStatusColor(status)}
                    style={{ cursor: 'pointer' }}
                    onClick={() => handleStatusChange(record)}
                >
                    {status}
                </Tag>
            ),
        },
        {
            title: '견적',
            key: 'quoteCount',
            width: 80,
            align: 'center',
            render: (_, record) => (
                <Button
                    type="link"
                    size="small"
                    onClick={() => handleQuoteModal(record)}
                >
                    <Badge count={record.quoteCount} showZero>
                        <FileTextOutlined />
                    </Badge>
                </Button>
            ),
        },
        {
            title: '메모',
            key: 'memoCount',
            width: 80,
            align: 'center',
            render: (_, record) => (
                <Button
                    type="link"
                    size="small"
                    onClick={() => handleMemoModal(record)}
                >
                    <Badge count={record.memoCount} showZero>
                        <MessageOutlined />
                    </Badge>
                </Button>
            ),
        },
        {
            title: '액션',
            key: 'action',
            width: 100,
            fixed: 'right',
            render: (_, record) => (
                <Space>
                    <Tooltip title="복사">
                        <Button
                            type="text"
                            size="small"
                            icon={<CopyOutlined />}
                            onClick={() => handleCopy(record)}
                        />
                    </Tooltip>
                    <Popconfirm
                        title="삭제하시겠습니까?"
                        onConfirm={() => handleDelete([record.id])}
                        okText="예"
                        cancelText="아니오"
                    >
                        <Button
                            type="text"
                            size="small"
                            danger
                            icon={<DeleteOutlined />}
                        />
                    </Popconfirm>
                </Space>
            ),
        },
    ];

    // 테이블 설정
    const rowSelection = {
        selectedRowKeys,
        onChange: (keys) => setSelectedRowKeys(keys),
    };

    // 핸들러 함수들
    const handleEditField = (record, field, currentValue) => {
        setCurrentRecord({ ...record, editField: field, currentValue });
        editForm.setFieldsValue({ [field]: currentValue });
        setEditModalVisible(true);
    };

    const handleEditSubmit = async (values) => {
        const field = currentRecord.editField;
        const newValue = values[field];

        if (newValue !== currentRecord.currentValue) {
            setLoading(true);
            try {
                await api.updateField(currentRecord.id, {
                    field_name: field,
                    field_label: field,
                    new_value: newValue,
                    author: '관리자'
                });

                message.success('수정되었습니다');
                loadData();
            } catch (error) {
                api.handleError(error);
            } finally {
                setLoading(false);
            }
        }
        setEditModalVisible(false);
    };

    const handleStatusChange = (record) => {
        setCurrentRecord(record);
        statusForm.setFieldsValue({
            status: record.recentStatus,
            recipient: '업체+고객'
        });
        setStatusModalVisible(true);
    };

    const handleStatusSubmit = async (values) => {
        setLoading(true);
        try {
            await api.updateStatus(currentRecord.id, {
                ...values,
                author: '관리자'
            });

            message.success('상태가 변경되었습니다');
            loadData();
        } catch (error) {
            api.handleError(error);
        } finally {
            setLoading(false);
        }
        setStatusModalVisible(false);
    };

    const handleMemoModal = (record) => {
        setCurrentRecord(record);
        memoForm.resetFields();
        setMemoModalVisible(true);
    };

    const handleMemoSubmit = async (values) => {
        setLoading(true);
        try {
            await api.addMemo(currentRecord.id, {
                content: values.content,
                author: '관리자'
            });

            message.success('메모가 추가되었습니다');
            loadData();
        } catch (error) {
            api.handleError(error);
        } finally {
            setLoading(false);
        }
        setMemoModalVisible(false);
    };

    const handleQuoteModal = (record) => {
        setCurrentRecord(record);
        quoteForm.resetFields();
        setQuoteModalVisible(true);
    };

    const handleQuoteSubmit = async (values) => {
        setLoading(true);
        try {
            await api.addQuoteLink(currentRecord.id, {
                draft_type: values.draft_type || '초안',
                link: values.link
            });

            message.success('견적서가 추가되었습니다');
            loadData();
        } catch (error) {
            api.handleError(error);
        } finally {
            setLoading(false);
        }
        setQuoteModalVisible(false);
    };

    const handleCompanyDrawer = (record) => {
        setCurrentRecord(record);
        setCompanyDrawerVisible(true);
    };

    const handleCopy = async (record) => {
        setLoading(true);
        try {
            await api.copyOrder(record.id);
            message.success('의뢰가 복사되었습니다');
            loadData();
        } catch (error) {
            api.handleError(error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (ids) => {
        setLoading(true);
        try {
            await api.bulkDelete(ids);
            message.success('삭제되었습니다');
            setSelectedRowKeys([]);
            loadData();
        } catch (error) {
            api.handleError(error);
        } finally {
            setLoading(false);
        }
    };

    const handleBulkDelete = () => {
        if (selectedRowKeys.length === 0) {
            message.warning('삭제할 항목을 선택해주세요');
            return;
        }

        Modal.confirm({
            title: '선택 항목 삭제',
            content: `선택한 ${selectedRowKeys.length}개 항목을 삭제하시겠습니까?`,
            okText: '삭제',
            okType: 'danger',
            cancelText: '취소',
            onOk: () => handleDelete(selectedRowKeys)
        });
    };

    // 필드별 입력 컴포넌트 렌더링
    const renderFieldInput = (field) => {
        switch (field) {
            case 'workContent':
            case 'area':
                return <TextArea rows={4} />;
            case 'scheduledDate':
                return <DatePicker style={{ width: '100%' }} />;
            default:
                return <Input />;
        }
    };

    return (
        <div style={{ padding: 24, background: '#f0f2f5', minHeight: '100vh' }}>
            <Card>
                <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
                    <Col>
                        <Title level={3} style={{ margin: 0 }}>견적의뢰 관리 시스템</Title>
                    </Col>
                    <Col>
                        <Space>
                            {selectedRowKeys.length > 0 && (
                                <Button
                                    danger
                                    icon={<DeleteOutlined />}
                                    onClick={handleBulkDelete}
                                >
                                    선택 삭제 ({selectedRowKeys.length})
                                </Button>
                            )}
                            <Button
                                type="primary"
                                icon={<PlusOutlined />}
                                onClick={() => window.open('https://docs.google.com/forms/d/e/1FAIpQLSfOnhe1eBTRM5bb-r_XA6epsUkPctmqexzcwJk-MC5KlC3F4g/viewform', '_blank')}
                            >
                                의뢰 추가
                            </Button>
                            <Button
                                icon={<SyncOutlined />}
                                onClick={loadData}
                            >
                                새로고침
                            </Button>
                        </Space>
                    </Col>
                </Row>

                <Table
                    rowSelection={rowSelection}
                    columns={columns}
                    dataSource={orders}
                    loading={tableLoading}
                    scroll={{ x: 1500 }}
                    pagination={{
                        showSizeChanger: true,
                        showQuickJumper: true,
                        showTotal: (total) => `총 ${total}개`,
                    }}
                />
            </Card>

            {/* 필드 수정 모달 */}
            <Modal
                title={`${currentRecord?.editField} 수정`}
                open={editModalVisible}
                onOk={editForm.submit}
                onCancel={() => setEditModalVisible(false)}
                confirmLoading={loading}
            >
                <Form
                    form={editForm}
                    layout="vertical"
                    onFinish={handleEditSubmit}
                >
                    <Form.Item
                        label="현재 값"
                    >
                        <Input value={currentRecord?.currentValue} disabled />
                    </Form.Item>
                    <Form.Item
                        name={currentRecord?.editField}
                        label="새로운 값"
                        rules={[{ required: true, message: '값을 입력해주세요' }]}
                    >
                        {currentRecord && renderFieldInput(currentRecord.editField)}
                    </Form.Item>
                </Form>
            </Modal>

            {/* 상태 변경 모달 */}
            <Modal
                title="할당상태 변경"
                open={statusModalVisible}
                onOk={statusForm.submit}
                onCancel={() => setStatusModalVisible(false)}
                confirmLoading={loading}
                width={600}
            >
                <Form
                    form={statusForm}
                    layout="vertical"
                    onFinish={handleStatusSubmit}
                >
                    <Alert
                        message={`현재 상태: ${currentRecord?.recentStatus}`}
                        type="info"
                        style={{ marginBottom: 16 }}
                    />

                    <Form.Item
                        name="status"
                        label="새로운 상태"
                        rules={[{ required: true, message: '상태를 선택해주세요' }]}
                    >
                        <Select>
                            {currentRecord && statusTransitions[currentRecord.recentStatus]?.map(status => (
                                <Option key={status} value={status}>{status}</Option>
                            ))}
                        </Select>
                    </Form.Item>

                    <Form.Item
                        name="message_sent"
                        valuePropName="checked"
                    >
                        <Checkbox>문자 발송</Checkbox>
                    </Form.Item>

                    <Form.Item
                        name="recipient"
                        label="수신자"
                    >
                        <Select>
                            <Option value="업체+고객">업체+고객</Option>
                            <Option value="업체">업체</Option>
                            <Option value="고객">고객</Option>
                        </Select>
                    </Form.Item>

                    <Form.Item
                        name="message_content"
                        label="문자 내용"
                    >
                        <TextArea rows={4} />
                    </Form.Item>
                </Form>
            </Modal>

            {/* 메모 추가 모달 */}
            <Modal
                title="메모 추가"
                open={memoModalVisible}
                onOk={memoForm.submit}
                onCancel={() => setMemoModalVisible(false)}
                confirmLoading={loading}
            >
                <Form
                    form={memoForm}
                    layout="vertical"
                    onFinish={handleMemoSubmit}
                >
                    <Form.Item
                        name="content"
                        label="메모 내용"
                        rules={[{ required: true, message: '메모를 입력해주세요' }]}
                    >
                        <TextArea rows={4} placeholder="메모를 입력하세요..." />
                    </Form.Item>
                </Form>
            </Modal>

            {/* 견적서 추가 모달 */}
            <Modal
                title="견적서 추가"
                open={quoteModalVisible}
                onOk={quoteForm.submit}
                onCancel={() => setQuoteModalVisible(false)}
                confirmLoading={loading}
            >
                <Form
                    form={quoteForm}
                    layout="vertical"
                    onFinish={handleQuoteSubmit}
                >
                    <Form.Item
                        name="draft_type"
                        label="견적서 타입"
                        initialValue="초안"
                    >
                        <Select>
                            <Option value="초안">초안</Option>
                            <Option value="1차">1차</Option>
                            <Option value="2차">2차</Option>
                            <Option value="3차">3차</Option>
                            <Option value="최종">최종</Option>
                        </Select>
                    </Form.Item>
                    <Form.Item
                        name="link"
                        label="견적서 링크"
                        rules={[
                            { required: true, message: '링크를 입력해주세요' },
                            { type: 'url', message: '올바른 URL을 입력해주세요' }
                        ]}
                    >
                        <Input placeholder="https://..." />
                    </Form.Item>
                </Form>
            </Modal>

            {/* 업체 할당 Drawer */}
            <Drawer
                title="업체 할당"
                placement="right"
                onClose={() => setCompanyDrawerVisible(false)}
                open={companyDrawerVisible}
                width={600}
            >
                {currentRecord && (
                    <div>
                        <Descriptions title="의뢰 정보" bordered column={1} style={{ marginBottom: 24 }}>
                            <Descriptions.Item label="고객명">{currentRecord.name}</Descriptions.Item>
                            <Descriptions.Item label="공사지역">{currentRecord.area}</Descriptions.Item>
                            <Descriptions.Item label="공사내용">{currentRecord.workContent}</Descriptions.Item>
                            <Descriptions.Item label="공사예정일">{currentRecord.scheduledDate}</Descriptions.Item>
                        </Descriptions>

                        <Title level={5}>업체 목록</Title>
                        <Alert
                            message="업체 할당 기능은 현재 개발 중입니다."
                            type="info"
                            showIcon
                        />
                    </div>
                )}
            </Drawer>
        </div>
    );
};

// React 컴포넌트 렌더링
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<QuoteManagementSystem />);