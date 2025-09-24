// 업체 관리 컴포넌트

import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Input,
  Modal,
  Form,
  Select,
  message,
  Popconfirm,
  Badge,
  Tooltip,
  Row,
  Col,
  Statistic,
  Progress
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  UserOutlined,
  PhoneOutlined,
  EnvironmentOutlined,
  CheckCircleOutlined,
  StopOutlined,
  ReloadOutlined,
  TeamOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { orderService } from '../services/orderService';
import { Company } from '../types/order.types';

const { Search } = Input;

const CompanyManagement: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCompany, setEditingCompany] = useState<Company | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    try {
      setLoading(true);
      const data = await orderService.getCompanies();
      setCompanies(data);
    } catch (error) {
      message.error('업체 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setEditingCompany(null);
    form.resetFields();
    setIsModalOpen(true);
  };

  const handleEdit = (company: Company) => {
    setEditingCompany(company);
    form.setFieldsValue(company);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    try {
      // API 호출 (구현 필요)
      message.success('업체가 삭제되었습니다.');
      loadCompanies();
    } catch (error) {
      message.error('삭제에 실패했습니다.');
    }
  };

  const handleSubmit = async (values: any) => {
    try {
      if (editingCompany) {
        // 수정 API 호출
        message.success('업체 정보가 수정되었습니다.');
      } else {
        // 추가 API 호출
        message.success('새 업체가 추가되었습니다.');
      }
      setIsModalOpen(false);
      loadCompanies();
    } catch (error) {
      message.error('저장에 실패했습니다.');
    }
  };

  const filteredCompanies = companies.filter(company =>
    company.name.toLowerCase().includes(searchText.toLowerCase())
  );

  const columns: ColumnsType<Company> = [
    {
      title: '업체명',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
          <TeamOutlined />
          <strong>{text}</strong>
          {record.is_active ? (
            <Badge status="success" text="활성" />
          ) : (
            <Badge status="error" text="비활성" />
          )}
        </Space>
      )
    },
    {
      title: '연락처',
      dataIndex: 'contact',
      key: 'contact',
      render: (text) => (
        <Space>
          <PhoneOutlined />
          {text || '-'}
        </Space>
      )
    },
    {
      title: '가능 지역',
      dataIndex: 'area',
      key: 'area',
      render: (areas: string[]) => (
        <>
          {areas?.map(area => (
            <Tag key={area} color="blue">
              <EnvironmentOutlined /> {area}
            </Tag>
          )) || '-'}
        </>
      )
    },
    {
      title: '처리 능력',
      key: 'capacity',
      render: (_, record) => {
        const percentage = record.capacity ?
          ((record.current_orders || 0) / record.capacity) * 100 : 0;

        return (
          <Tooltip title={`${record.current_orders || 0} / ${record.capacity || 0}`}>
            <Progress
              percent={percentage}
              size="small"
              status={percentage >= 100 ? 'exception' : 'normal'}
              strokeColor={{
                '0%': '#87d068',
                '50%': '#faad14',
                '100%': '#ff4d4f'
              }}
            />
          </Tooltip>
        );
      }
    },
    {
      title: '상태',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? (
            <>
              <CheckCircleOutlined /> 활성
            </>
          ) : (
            <>
              <StopOutlined /> 비활성
            </>
          )}
        </Tag>
      )
    },
    {
      title: '액션',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Tooltip title="수정">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          <Popconfirm
            title="삭제 확인"
            description="정말로 이 업체를 삭제하시겠습니까?"
            onConfirm={() => handleDelete(record.id)}
            okText="예"
            cancelText="아니오"
          >
            <Tooltip title="삭제">
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      )
    }
  ];

  // 통계 카드 데이터
  const statistics = {
    total: companies.length,
    active: companies.filter(c => c.is_active).length,
    inactive: companies.filter(c => !c.is_active).length,
    avgCapacity: Math.round(
      companies.reduce((sum, c) => sum + (c.capacity || 0), 0) / companies.length
    ) || 0
  };

  return (
    <div style={{ padding: 24 }}>
      {/* 헤더 */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <h1 style={{ margin: 0 }}>업체 관리</h1>
        </Col>
        <Col>
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={loadCompanies}
              loading={loading}
            >
              새로고침
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAdd}
            >
              업체 추가
            </Button>
          </Space>
        </Col>
      </Row>

      {/* 통계 카드 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="전체 업체"
              value={statistics.total}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="활성 업체"
              value={statistics.active}
              valueStyle={{ color: '#52c41a' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="비활성 업체"
              value={statistics.inactive}
              valueStyle={{ color: '#ff4d4f' }}
              prefix={<StopOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="평균 처리 능력"
              value={statistics.avgCapacity}
              suffix="건/월"
            />
          </Card>
        </Col>
      </Row>

      {/* 검색 및 테이블 */}
      <Card>
        <Search
          placeholder="업체명으로 검색"
          allowClear
          enterButton={<SearchOutlined />}
          size="large"
          onSearch={setSearchText}
          style={{ marginBottom: 16 }}
        />

        <Table
          columns={columns}
          dataSource={filteredCompanies}
          loading={loading}
          rowKey="id"
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `총 ${total}개의 업체`
          }}
        />
      </Card>

      {/* 업체 추가/수정 모달 */}
      <Modal
        title={editingCompany ? '업체 수정' : '업체 추가'}
        open={isModalOpen}
        onOk={form.submit}
        onCancel={() => setIsModalOpen(false)}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="name"
            label="업체명"
            rules={[{ required: true, message: '업체명을 입력하세요' }]}
          >
            <Input prefix={<TeamOutlined />} placeholder="업체명" />
          </Form.Item>

          <Form.Item
            name="contact"
            label="연락처"
            rules={[
              { required: true, message: '연락처를 입력하세요' },
              { pattern: /^[0-9-]+$/, message: '올바른 전화번호 형식을 입력하세요' }
            ]}
          >
            <Input prefix={<PhoneOutlined />} placeholder="010-0000-0000" />
          </Form.Item>

          <Form.Item
            name="area"
            label="가능 지역"
            rules={[{ required: true, message: '가능 지역을 선택하세요' }]}
          >
            <Select
              mode="multiple"
              placeholder="가능 지역 선택"
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              options={[
                { value: '서울', label: '서울' },
                { value: '경기', label: '경기' },
                { value: '인천', label: '인천' },
                { value: '부산', label: '부산' },
                { value: '대구', label: '대구' },
                { value: '광주', label: '광주' },
                { value: '대전', label: '대전' },
                { value: '울산', label: '울산' },
                { value: '세종', label: '세종' }
              ]}
            />
          </Form.Item>

          <Form.Item
            name="capacity"
            label="월 처리 능력"
            rules={[{ required: true, message: '처리 능력을 입력하세요' }]}
          >
            <Input
              type="number"
              suffix="건/월"
              placeholder="월간 처리 가능한 의뢰 수"
            />
          </Form.Item>

          <Form.Item
            name="is_active"
            label="상태"
            valuePropName="checked"
            initialValue={true}
          >
            <Select>
              <Select.Option value={true}>활성</Select.Option>
              <Select.Option value={false}>비활성</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default CompanyManagement;