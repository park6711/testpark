// 회원 목록 컴포넌트

import React, { useState } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Input,
  Avatar,
  Badge,
  Tooltip,
  Row,
  Col,
  Statistic,
  Dropdown,
  Menu,
  message,
  Modal,
  Form,
  Select,
  DatePicker
} from 'antd';
import {
  UserOutlined,
  SearchOutlined,
  MailOutlined,
  PhoneOutlined,
  CalendarOutlined,
  MoreOutlined,
  ExportOutlined,
  FilterOutlined,
  TeamOutlined,
  UserAddOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { Search } = Input;

interface Member {
  id: number;
  name: string;
  email: string;
  phone: string;
  registeredDate: string;
  lastLogin: string;
  orderCount: number;
  status: 'active' | 'inactive' | 'suspended';
  type: 'customer' | 'company';
  avatar?: string;
}

const MemberList: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [filterModalVisible, setFilterModalVisible] = useState(false);
  const [form] = Form.useForm();

  // 실제 API 연동 시 대체
  const members: Member[] = [];

  const handleExport = () => {
    message.info('회원 목록을 Excel로 내보내기 중...');
  };

  const handleBulkAction = (action: string) => {
    if (selectedRowKeys.length === 0) {
      message.warning('선택된 회원이 없습니다.');
      return;
    }
    message.info(`${selectedRowKeys.length}명의 회원에 대해 ${action} 실행`);
  };

  const columns: ColumnsType<Member> = [
    {
      title: '회원 정보',
      key: 'info',
      render: (_, record) => (
        <Space>
          <Avatar icon={<UserOutlined />} src={record.avatar} />
          <div>
            <div><strong>{record.name}</strong></div>
            <div style={{ fontSize: 12, color: '#999' }}>
              {record.type === 'customer' ? '고객' : '업체'}
            </div>
          </div>
        </Space>
      )
    },
    {
      title: '연락처',
      key: 'contact',
      render: (_, record) => (
        <Space direction="vertical" size={0}>
          <Space>
            <MailOutlined />
            <span style={{ fontSize: 12 }}>{record.email}</span>
          </Space>
          <Space>
            <PhoneOutlined />
            <span style={{ fontSize: 12 }}>{record.phone}</span>
          </Space>
        </Space>
      )
    },
    {
      title: '가입일',
      dataIndex: 'registeredDate',
      key: 'registeredDate',
      render: (date) => (
        <Tooltip title={date}>
          <Space>
            <CalendarOutlined />
            {new Date(date).toLocaleDateString('ko-KR')}
          </Space>
        </Tooltip>
      ),
      sorter: (a, b) => new Date(a.registeredDate).getTime() - new Date(b.registeredDate).getTime()
    },
    {
      title: '최근 접속',
      dataIndex: 'lastLogin',
      key: 'lastLogin',
      render: (date) => {
        const days = Math.floor((Date.now() - new Date(date).getTime()) / (1000 * 60 * 60 * 24));
        return (
          <span style={{ color: days > 30 ? '#ff4d4f' : '#52c41a' }}>
            {days === 0 ? '오늘' : `${days}일 전`}
          </span>
        );
      }
    },
    {
      title: '의뢰 수',
      dataIndex: 'orderCount',
      key: 'orderCount',
      align: 'center',
      render: (count) => <Badge count={count} showZero />
    },
    {
      title: '상태',
      dataIndex: 'status',
      key: 'status',
      render: (status: 'active' | 'inactive' | 'suspended') => {
        const config = {
          active: { color: 'success', icon: <CheckCircleOutlined />, text: '활성' },
          inactive: { color: 'default', icon: <CloseCircleOutlined />, text: '비활성' },
          suspended: { color: 'error', icon: <CloseCircleOutlined />, text: '정지' }
        };
        const { color, icon, text } = config[status];
        return <Tag color={color as any}>{icon} {text}</Tag>;
      }
    },
    {
      title: '액션',
      key: 'action',
      render: (_, record) => (
        <Dropdown
          overlay={
            <Menu>
              <Menu.Item key="view">상세 보기</Menu.Item>
              <Menu.Item key="edit">정보 수정</Menu.Item>
              <Menu.Item key="orders">의뢰 내역</Menu.Item>
              <Menu.Divider />
              <Menu.Item key="suspend" danger>
                계정 정지
              </Menu.Item>
            </Menu>
          }
        >
          <Button type="text" icon={<MoreOutlined />} />
        </Dropdown>
      )
    }
  ];

  const statistics = {
    total: members.length,
    customers: members.filter(m => m.type === 'customer').length,
    companies: members.filter(m => m.type === 'company').length,
    active: members.filter(m => m.status === 'active').length
  };

  return (
    <div style={{ padding: 24 }}>
      {/* 헤더 */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <h1 style={{ margin: 0 }}>회원 목록</h1>
        </Col>
        <Col>
          <Space>
            <Button icon={<FilterOutlined />} onClick={() => setFilterModalVisible(true)}>
              필터
            </Button>
            <Button icon={<ExportOutlined />} onClick={handleExport}>
              내보내기
            </Button>
            <Button type="primary" icon={<UserAddOutlined />}>
              회원 추가
            </Button>
          </Space>
        </Col>
      </Row>

      {/* 통계 카드 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="전체 회원"
              value={statistics.total}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="일반 고객"
              value={statistics.customers}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="업체 회원"
              value={statistics.companies}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="활성 회원"
              value={statistics.active}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 회원 테이블 */}
      <Card>
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Row justify="space-between" align="middle">
            <Col flex="auto">
              <Search
                placeholder="이름, 이메일, 전화번호로 검색"
                allowClear
                enterButton={<SearchOutlined />}
                size="large"
                onSearch={setSearchText}
                style={{ maxWidth: 400 }}
              />
            </Col>
            {selectedRowKeys.length > 0 && (
              <Col>
                <Space>
                  <span>{selectedRowKeys.length}명 선택됨</span>
                  <Button onClick={() => handleBulkAction('메시지 발송')}>
                    메시지 발송
                  </Button>
                  <Button danger onClick={() => handleBulkAction('삭제')}>
                    삭제
                  </Button>
                </Space>
              </Col>
            )}
          </Row>

          <Table
            rowSelection={{
              selectedRowKeys,
              onChange: setSelectedRowKeys
            }}
            columns={columns}
            dataSource={members}
            loading={loading}
            rowKey="id"
            pagination={{
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `총 ${total}명`
            }}
            locale={{
              emptyText: '등록된 회원이 없습니다.'
            }}
          />
        </Space>
      </Card>

      {/* 필터 모달 */}
      <Modal
        title="회원 필터"
        open={filterModalVisible}
        onOk={form.submit}
        onCancel={() => setFilterModalVisible(false)}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={(values) => {
            console.log('Filter values:', values);
            setFilterModalVisible(false);
          }}
        >
          <Form.Item name="type" label="회원 유형">
            <Select placeholder="전체">
              <Select.Option value="all">전체</Select.Option>
              <Select.Option value="customer">고객</Select.Option>
              <Select.Option value="company">업체</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="status" label="상태">
            <Select placeholder="전체">
              <Select.Option value="all">전체</Select.Option>
              <Select.Option value="active">활성</Select.Option>
              <Select.Option value="inactive">비활성</Select.Option>
              <Select.Option value="suspended">정지</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="dateRange" label="가입 기간">
            <DatePicker.RangePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default MemberList;