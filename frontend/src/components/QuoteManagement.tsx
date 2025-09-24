// 의뢰 관리 시스템 메인 컴포넌트 (Ant Design)

import React, { useState, useEffect } from 'react';
import {
  Layout,
  Card,
  Input,
  Select,
  Button,
  Space,
  Row,
  Col,
  Typography,
  ConfigProvider,
  Statistic,
  Divider,
  DatePicker,
  message
} from 'antd';
import {
  SearchOutlined,
  PlusOutlined,
  TeamOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  DashboardOutlined,
  SyncOutlined,
  GoogleOutlined
} from '@ant-design/icons';
import koKR from 'antd/locale/ko_KR';
import OrderList from './orders/OrderList';
import { useOrders } from '../hooks';
import { STATUS_OPTIONS, AREA_OPTIONS } from '../constants';
const { Header, Content } = Layout;
const { Title, Text } = Typography;
const { Search } = Input;
const { RangePicker } = DatePicker;

const QuoteManagement: React.FC = () => {
  const {
    orders,
    loading,
    error,
    filters,
    setFilters,
    actions
  } = useOrders();

  const [searchValue, setSearchValue] = useState('');
  const [syncLoading, setSyncLoading] = useState(false);

  // 통계 계산
  const statistics = {
    total: orders.length,
    pending: orders.filter(o => o.recent_status === '접수완료').length,
    inProgress: orders.filter(o => ['업체전달', '현장미팅', '견적전달', '시공중'].includes(o.recent_status)).length,
    completed: orders.filter(o => o.recent_status === '완료').length
  };

  const handleSearch = (value: string) => {
    setFilters({ ...filters, searchText: value });
  };

  const handleFilterChange = (filterType: string, value: any) => {
    setFilters({ ...filters, [filterType]: value || undefined });
  };

  const handleDateRangeChange = (dates: any) => {
    if (dates) {
      setFilters({
        ...filters,
        dateFrom: dates[0]?.format('YYYY-MM-DD'),
        dateTo: dates[1]?.format('YYYY-MM-DD')
      });
    } else {
      const { dateFrom, dateTo, ...restFilters } = filters;
      setFilters(restFilters);
    }
  };

  const clearFilters = () => {
    setFilters({});
    setSearchValue('');
  };

  const handleGoogleSync = async () => {
    setSyncLoading(true);
    try {
      const response = await fetch('http://localhost:8000/order/api/sync-google-sheets/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (data.success) {
        message.success(`동기화 완료: ${data.result.created}개 새 의뢰 추가`);
        // 목록 새로고침
        actions.fetchOrders();
      } else {
        message.error(data.message || '동기화 실패');
      }
    } catch (error) {
      message.error('동기화 중 오류가 발생했습니다');
      console.error('Sync error:', error);
    } finally {
      setSyncLoading(false);
    }
  };

  return (
    <ConfigProvider locale={koKR}>
      <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
        {/* 헤더 */}
        <Header style={{ background: '#fff', padding: 0, boxShadow: '0 1px 4px rgba(0,21,41,.08)' }}>
          <Row align="middle" style={{ height: '100%', padding: '0 24px' }}>
            <Col flex="auto">
              <Space align="center">
                <DashboardOutlined style={{ fontSize: 24, color: '#1890ff' }} />
                <Title level={3} style={{ margin: 0 }}>의뢰 관리 시스템</Title>
              </Space>
            </Col>
            <Col>
              <Space>
                <Button
                  icon={<SyncOutlined spin={syncLoading} />}
                  size="large"
                  loading={syncLoading}
                  onClick={handleGoogleSync}
                  style={{ borderColor: '#4285f4', color: '#4285f4' }}
                >
                  구글 시트 동기화
                </Button>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  size="large"
                  onClick={() => {
                    // 구글 폼으로 새 탭에서 열기
                    window.open('https://docs.google.com/forms/d/e/1FAIpQLSfOnhe1eBTRM5bb-r_XA6epsUkPctmqexzcwJk-MC5KlC3F4g/viewform', '_blank');
                  }}
                >
                  새 의뢰
                </Button>
              </Space>
            </Col>
          </Row>
        </Header>

        <Content style={{ padding: '24px' }}>
          {/* 통계 카드 */}
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={6}>
              <Card>
                <Statistic
                  title="전체 의뢰"
                  value={statistics.total}
                  prefix={<FileTextOutlined />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="대기중"
                  value={statistics.pending}
                  prefix={<ClockCircleOutlined />}
                  valueStyle={{ color: '#faad14' }}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="진행중"
                  value={statistics.inProgress}
                  prefix={<TeamOutlined />}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col span={6}>
              <Card>
                <Statistic
                  title="완료"
                  value={statistics.completed}
                  prefix={<CheckCircleOutlined />}
                  valueStyle={{ color: '#13c2c2' }}
                />
              </Card>
            </Col>
          </Row>

          {/* 검색 및 필터 */}
          <Card style={{ marginBottom: 24 }}>
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              {/* 검색 영역 */}
              <Row gutter={16}>
                <Col span={12}>
                  <Search
                    placeholder="고객명, 전화번호, 네이버ID로 검색..."
                    allowClear
                    enterButton={<SearchOutlined />}
                    size="large"
                    value={searchValue}
                    onChange={(e) => setSearchValue(e.target.value)}
                    onSearch={handleSearch}
                  />
                </Col>
                <Col span={12}>
                  <RangePicker
                    style={{ width: '100%' }}
                    size="large"
                    placeholder={['시작일', '종료일']}
                    onChange={handleDateRangeChange}
                    format="YYYY-MM-DD"
                  />
                </Col>
              </Row>

              {/* 필터 영역 */}
              <Row gutter={16} align="middle">
                <Col span={6}>
                  <Select
                    placeholder="상태 선택"
                    style={{ width: '100%' }}
                    allowClear
                    onChange={(value) => handleFilterChange('status', value)}
                    options={[
                      { label: '전체 상태', value: '' },
                      ...STATUS_OPTIONS.map(s => ({ label: s.label, value: s.value }))
                    ]}
                  />
                </Col>
                <Col span={6}>
                  <Select
                    placeholder="지역 선택"
                    style={{ width: '100%' }}
                    allowClear
                    onChange={(value) => handleFilterChange('area', value)}
                    options={[
                      { label: '전체 지역', value: '' },
                      ...AREA_OPTIONS.map(area => ({ label: area, value: area }))
                    ]}
                  />
                </Col>
                <Col span={6}>
                  <Select
                    placeholder="업체 선택"
                    style={{ width: '100%' }}
                    allowClear
                    onChange={(value) => handleFilterChange('company', value)}
                    options={[
                      { label: '전체 업체', value: '' },
                      // TODO: 업체 목록 API에서 가져오기
                      { label: '업체A', value: '업체A' },
                      { label: '업체B', value: '업체B' },
                      { label: '업체C', value: '업체C' }
                    ]}
                  />
                </Col>
                <Col span={6}>
                  <Button onClick={clearFilters}>
                    필터 초기화
                  </Button>
                </Col>
              </Row>

              {/* 활성 필터 표시 */}
              {Object.keys(filters).length > 0 && (
                <>
                  <Divider style={{ margin: '12px 0' }} />
                  <Space wrap>
                    <Text type="secondary">활성 필터:</Text>
                    {filters.searchText && (
                      <Button size="small" type="dashed">
                        검색: {filters.searchText}
                      </Button>
                    )}
                    {filters.status && (
                      <Button size="small" type="dashed">
                        상태: {filters.status}
                      </Button>
                    )}
                    {filters.area && (
                      <Button size="small" type="dashed">
                        지역: {filters.area}
                      </Button>
                    )}
                    {filters.company && (
                      <Button size="small" type="dashed">
                        업체: {filters.company}
                      </Button>
                    )}
                    {filters.dateFrom && filters.dateTo && (
                      <Button size="small" type="dashed">
                        기간: {filters.dateFrom} ~ {filters.dateTo}
                      </Button>
                    )}
                  </Space>
                </>
              )}
            </Space>
          </Card>

          {/* 의뢰 목록 테이블 */}
          <Card>
            <OrderList
              orders={orders}
              loading={loading}
              error={error}
              onRefresh={actions.fetchOrders}
              onDeleteOrders={actions.deleteOrders}
              onUpdateStatus={actions.updateOrderStatus}
              onAddMemo={actions.addMemo}
              onUpdateField={actions.updateOrderField}
            />
          </Card>
        </Content>
      </Layout>
    </ConfigProvider>
  );
};

export default QuoteManagement;