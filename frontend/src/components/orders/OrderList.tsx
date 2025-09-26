// 의뢰 목록 컴포넌트 (Ant Design)

import React, { useState } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Popconfirm,
  message,
  Tooltip,
  Typography,
  Row,
  Col,
  Dropdown,
  Badge,
  Card
} from 'antd';
import type { ColumnsType, TableRowSelection } from 'antd/es/table/interface';
import {
  DeleteOutlined,
  ReloadOutlined,
  DownloadOutlined,
  EditOutlined,
  MessageOutlined,
  MoreOutlined,
  EyeOutlined,
  PhoneOutlined,
  EnvironmentOutlined,
  CalendarOutlined,
  TeamOutlined,
  CopyOutlined,
  LinkOutlined,
  UserOutlined
} from '@ant-design/icons';
import { MemoModal, StatusModal } from '../modals';
import { OrderData } from '../../types';
import { STATUS_OPTIONS } from '../../constants';

const { Text } = Typography;

interface OrderListProps {
  orders: OrderData[];
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
  onDeleteOrders: (orderIds: number[]) => Promise<{ success: boolean; error?: string }>;
  onUpdateStatus: (orderId: number, status: string, note?: string) => Promise<{ success: boolean; error?: string }>;
  onAddMemo: (orderId: number, content: string) => Promise<{ success: boolean; error?: string }>;
  onUpdateField: (orderId: number, fieldName: string, fieldLabel: string, newValue: any) => Promise<{ success: boolean; error?: string }>;
}

const OrderList: React.FC<OrderListProps> = ({
  orders,
  loading,
  error,
  onRefresh,
  onDeleteOrders,
  onUpdateStatus,
  onAddMemo,
  onUpdateField
}) => {
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<OrderData | null>(null);
  const [memoModalOpen, setMemoModalOpen] = useState(false);
  const [statusModalOpen, setStatusModalOpen] = useState(false);


  const handleDeleteSelected = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('삭제할 항목을 선택해주세요.');
      return;
    }

    const result = await onDeleteOrders(selectedRowKeys as number[]);
    if (result.success) {
      message.success(`${selectedRowKeys.length}개 항목이 삭제되었습니다.`);
      setSelectedRowKeys([]);
    } else {
      message.error(result.error || '삭제 중 오류가 발생했습니다.');
    }
  };

  const handleCopyOrder = async (order: OrderData) => {
    // 새로운 의뢰 생성 (같은 정보로 복사)
    const copiedOrder = {
      ...order,
      no: undefined, // 새로운 번호 할당을 위해
      time: new Date().toISOString(),
      recent_status: '대기중',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    try {
      // TODO: API 호출로 새 의뢰 생성
      message.success('의뢰가 복사되었습니다');
      onRefresh(); // 목록 새로고침
    } catch (error) {
      message.error('복사 중 오류가 발생했습니다');
    }
  };

  const handleExport = () => {
    const headers = ['번호', '접수일시', '고객명', '전화번호', '지역', '공사내용', '업체', '상태'];
    const csvContent = [
      headers.join(','),
      ...orders.map(order => [
        order.no,
        order.time,
        order.sName,
        order.sPhone,
        order.sArea,
        `"${order.sConstruction.replace(/"/g, '""')}"`,
        order.assigned_company || '',
        order.recent_status
      ].join(','))
    ].join('\n');

    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `orders_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    message.success('내보내기가 완료되었습니다.');
  };

  const openMemoModal = (order: OrderData) => {
    setSelectedOrder(order);
    setMemoModalOpen(true);
  };

  const openStatusModal = (order: OrderData) => {
    setSelectedOrder(order);
    setStatusModalOpen(true);
  };

  const columns: ColumnsType<OrderData> = [
    {
      title: '접수일시',
      dataIndex: 'time',
      key: 'time',
      width: 120,  // 너비를 약간 늘림
      sorter: (a, b) => new Date(a.time).getTime() - new Date(b.time).getTime(),
      render: (time) => {
        const date = new Date(time);
        return (
          <Space direction="vertical" size={0}>
            <Text style={{ fontSize: 11 }}>{date.toLocaleDateString('ko-KR')}</Text>
            <Text type="secondary" style={{ fontSize: 10 }}>
              {date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}
            </Text>
          </Space>
        );
      }
    },
    {
      title: '지정여부',
      dataIndex: 'designation_type',
      key: 'designation_type',
      width: 110,  // 너비를 약간 늘림
      filters: [
        { text: '지정없음', value: '지정없음' },
        { text: '업체지정', value: '업체지정' },
        { text: '공동구매', value: '공동구매' },
      ],
      onFilter: (value, record) => record.designation_type === value,
      render: (type, record) => (
        <Space direction="vertical" size={0}>
          <Tag color={type === '업체지정' ? 'blue' : type === '공동구매' ? 'green' : 'default'}>
            {type}
          </Tag>
          {record.designation && (
            <Text style={{ fontSize: 10 }}>{record.designation}</Text>
          )}
        </Space>
      )
    },
    {
      title: '고객정보',
      key: 'customer_info',
      width: 160,  // 너비 최적화
      render: (_, record) => (
        <Space direction="vertical" size={0}>
          <Space size={4}>
            <UserOutlined style={{ fontSize: 11 }} />
            <Text strong style={{ fontSize: 12 }}>{record.sName}</Text>
            {record.sNick && <Tag color="orange" style={{ fontSize: 10 }}>{record.sNick}</Tag>}
          </Space>
          {record.sNaverID && (
            <Text type="secondary" style={{ fontSize: 11 }}>ID: {record.sNaverID}</Text>
          )}
          <Tooltip title="전화 걸기">
            <a href={`tel:${record.sPhone}`} style={{ fontSize: 11 }}>
              <PhoneOutlined /> {record.sPhone}
            </a>
          </Tooltip>
        </Space>
      )
    },
    {
      title: '의뢰게시글',
      dataIndex: 'post_link',
      key: 'post_link',
      width: 90,  // 너비 최적화
      render: (link, record) => (
        <Space direction="vertical" size={0}>
          {record.sPost && (
            <Text ellipsis style={{ maxWidth: 90, fontSize: 11 }}>{record.sPost}</Text>
          )}
          {link && (
            <Tooltip title={link}>
              <a href={link} target="_blank" rel="noopener noreferrer">
                <LinkOutlined /> 보기
              </a>
            </Tooltip>
          )}
        </Space>
      )
    },
    {
      title: '공사지역',
      dataIndex: 'sArea',
      key: 'sArea',
      width: 100,  // 너비를 약간 늘림
      filters: Array.from(new Set(orders.map(o => o.sArea))).map(area => ({ text: area, value: area })),
      onFilter: (value, record) => record.sArea === value,
      render: (area) => (
        <Tag color="blue" style={{ fontSize: 11 }}>
          <EnvironmentOutlined /> {area}
        </Tag>
      )
    },
    {
      title: '공사예정일',
      dataIndex: 'dateSchedule',
      key: 'dateSchedule',
      width: 110,  // 너비를 약간 늘림
      sorter: (a, b) => {
        if (!a.dateSchedule) return 1;
        if (!b.dateSchedule) return -1;
        return new Date(a.dateSchedule).getTime() - new Date(b.dateSchedule).getTime();
      },
      render: (date) => {
        if (!date) return <Text type="secondary" style={{ fontSize: 11 }}>미정</Text>;
        const scheduleDate = new Date(date);
        const today = new Date();
        const diffDays = Math.ceil((scheduleDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

        let color = 'default';
        if (diffDays < 0) color = 'red';
        else if (diffDays === 0) color = 'orange';
        else if (diffDays <= 3) color = 'gold';
        else color = 'green';

        return (
          <Tag color={color} style={{ fontSize: 11 }}>
            <CalendarOutlined /> {scheduleDate.toLocaleDateString('ko-KR', { month: '2-digit', day: '2-digit' })}
            {diffDays === 0 && ' (오늘)'}
          </Tag>
        );
      }
    },
    {
      title: '공사내용',
      dataIndex: 'sConstruction',
      key: 'sConstruction',
      // width 제거 - 남은 공간을 모두 차지하도록 함
      ellipsis: {
        showTitle: false,
      },
      render: (construction) => (
        <Tooltip placement="topLeft" title={construction}>
          <Text ellipsis style={{ maxWidth: '100%', fontSize: 11 }}>
            {construction}
          </Text>
        </Tooltip>
      )
    },
    {
      title: '업체할당',
      dataIndex: 'assigned_company',
      key: 'assigned_company',
      width: 100,  // 너비 최적화
      filters: Array.from(new Set(orders.map(o => o.assigned_company).filter(Boolean))).map(company => ({ text: company, value: company })),
      onFilter: (value, record) => record.assigned_company === value,
      render: (company) => company ? (
        <Tag color="purple" style={{ fontSize: 11 }}>
          <TeamOutlined /> {company}
        </Tag>
      ) : (
        <Button type="dashed" size="small" style={{ fontSize: 10 }}>
          할당하기
        </Button>
      )
    },
    {
      title: '할당상태',
      dataIndex: 'recent_status',
      key: 'recent_status',
      width: 85,  // 너비 최적화
      filters: STATUS_OPTIONS.map(s => ({ text: s.label, value: s.value })),
      onFilter: (value, record) => record.recent_status === value,
      render: (status) => {
        const statusOption = STATUS_OPTIONS.find(s => s.value === status);
        return (
          <Tag
            color={statusOption?.color}
            style={{ cursor: 'pointer', fontSize: 11 }}
            onClick={() => openStatusModal({ recent_status: status } as OrderData)}
          >
            {status}
          </Tag>
        );
      }
    },
    {
      title: '재의뢰',
      dataIndex: 're_request_count',
      key: 're_request_count',
      width: 65,  // 너비 최적화
      align: 'center',
      render: (count) => count > 0 ? (
        <Badge count={count} style={{ backgroundColor: '#ff4d4f' }} />
      ) : (
        <Text type="secondary" style={{ fontSize: 11 }}>0</Text>
      )
    },
    {
      title: '견적서링크',
      key: 'quote_links',
      width: 90,  // 너비 최적화
      render: (_, record) => (
        <Space>
          {record.quote_links && record.quote_links.length > 0 ? (
            <Badge count={record.quote_links.length}>
              <Button size="small" icon={<LinkOutlined />} style={{ fontSize: 10 }}>
                보기
              </Button>
            </Badge>
          ) : (
            <Button size="small" type="dashed" style={{ fontSize: 10 }}>
              추가
            </Button>
          )}
        </Space>
      )
    },
    {
      title: '메모',
      key: 'memo',
      width: 60,  // 너비 최적화
      align: 'center',
      render: (_, record) => (
        <Tooltip title="메모 관리">
          <Button
            type="text"
            size="small"
            icon={<MessageOutlined />}
            onClick={() => openMemoModal(record)}
            style={{ fontSize: 11 }}
          />
        </Tooltip>
      )
    },
    {
      title: '복사',
      key: 'copy',
      width: 60,
      fixed: 'right',
      align: 'center',
      render: (_, record) => (
        <Tooltip title="같은 정보로 복사">
          <Button
            type="text"
            size="small"
            icon={<CopyOutlined />}
            onClick={() => handleCopyOrder(record)}
            style={{ fontSize: 11 }}
          />
        </Tooltip>
      )
    }
  ];

  const rowSelection: TableRowSelection<OrderData> = {
    selectedRowKeys,
    onChange: (newSelectedRowKeys) => {
      setSelectedRowKeys(newSelectedRowKeys);
    },
    selections: [
      Table.SELECTION_ALL,
      Table.SELECTION_INVERT,
      Table.SELECTION_NONE,
    ]
  };

  if (error && !loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px 0' }}>
        <Text type="danger" style={{ fontSize: 16, display: 'block', marginBottom: 20 }}>
          {error}
        </Text>
        <Button type="primary" onClick={onRefresh} icon={<ReloadOutlined />}>
          다시 시도
        </Button>
      </div>
    );
  }

  return (
    <>
      {/* 툴바 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col flex="auto">
          <Space>
            <Popconfirm
              title="선택한 항목을 삭제하시겠습니까?"
              onConfirm={handleDeleteSelected}
              okText="삭제"
              cancelText="취소"
              disabled={selectedRowKeys.length === 0}
            >
              <Button
                danger
                icon={<DeleteOutlined />}
                disabled={selectedRowKeys.length === 0}
              >
                삭제 ({selectedRowKeys.length})
              </Button>
            </Popconfirm>
            <Button
              icon={<DownloadOutlined />}
              onClick={handleExport}
            >
              내보내기
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={onRefresh}
            >
              새로고침
            </Button>
          </Space>
        </Col>
        <Col>
          <Badge count={orders.length} showZero color="#1890ff" />
        </Col>
      </Row>

      {/* 테이블 */}
      <Table
        rowSelection={rowSelection}
        columns={columns}
        dataSource={orders}
        rowKey="no"
        loading={loading}
        scroll={{
          x: 'max-content',  // 콘텐츠에 맞게 자동 조정
          y: 'calc(100vh - 400px)'  // 세로 스크롤 높이 설정
        }}
        size="middle"
        bordered
        pagination={{
          defaultPageSize: 20,
          showSizeChanger: true,
          showTotal: (total, range) => `${range[0]}-${range[1]} / 총 ${total}개`,
          pageSizeOptions: ['10', '20', '50', '100'],
          showQuickJumper: true
        }}
        expandable={{
          expandedRowRender: (record) => (
            <div style={{ padding: '16px', background: '#fafafa', borderRadius: 8 }}>
              <Row gutter={[24, 16]}>
                <Col span={8}>
                  <Card size="small" title="개인정보 동의" bordered={false}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Row justify="space-between">
                        <Text>마케팅 동의:</Text>
                        <Tag color={record.bPrivacy1 ? 'green' : 'red'}>
                          {record.bPrivacy1 ? '동의' : '미동의'}
                        </Tag>
                      </Row>
                      <Row justify="space-between">
                        <Text>개인정보 동의:</Text>
                        <Tag color={record.bPrivacy2 ? 'green' : 'red'}>
                          {record.bPrivacy2 ? '동의' : '미동의'}
                        </Tag>
                      </Row>
                    </Space>
                  </Card>
                </Col>
                <Col span={8}>
                  <Card size="small" title="추가 정보" bordered={false}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      {record.post_link && (
                        <Row>
                          <Text strong>게시글: </Text>
                          <a href={record.post_link} target="_blank" rel="noopener noreferrer">
                            링크 보기
                          </a>
                        </Row>
                      )}
                      <Row>
                        <Text>등록 경로: {record.designation_type || '-'}</Text>
                      </Row>
                    </Space>
                  </Card>
                </Col>
                <Col span={8}>
                  <Card size="small" title="메모" bordered={false}>
                    <Button type="link" onClick={() => openMemoModal(record)}>
                      메모 추가/확인
                    </Button>
                  </Card>
                </Col>
              </Row>
            </div>
          ),
          rowExpandable: (record) => true,
          expandRowByClick: false
        }}
      />

      {/* 모달들 */}
      {selectedOrder && (
        <>
          <MemoModal
            isOpen={memoModalOpen}
            onClose={() => setMemoModalOpen(false)}
            orderId={selectedOrder.no}
            orderName={selectedOrder.sName}
            memos={[]} // TODO: API에서 메모 가져오기
            onAddMemo={async (content) => onAddMemo(selectedOrder.no, content)}
          />
          <StatusModal
            isOpen={statusModalOpen}
            onClose={() => setStatusModalOpen(false)}
            orderId={selectedOrder.no}
            orderName={selectedOrder.sName}
            currentStatus={selectedOrder.recent_status}
            onStatusUpdate={async (status, note) => onUpdateStatus(selectedOrder.no, status, note)}
          />
        </>
      )}
    </>
  );
};

export default OrderList;