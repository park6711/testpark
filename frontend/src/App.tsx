import React, { useState, useEffect } from 'react';
import {
  Layout,
  Card,
  Statistic,
  Table,
  Tag,
  Button,
  Space,
  Row,
  Col,
  Typography,
  Badge,
  Spin,
  message,
  ConfigProvider
} from 'antd';
import {
  UserOutlined,
  ShopOutlined,
  FileTextOutlined,
  DollarOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  SyncOutlined,
  TeamOutlined,
  DatabaseOutlined,
  ApiOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import koKR from 'antd/locale/ko_KR';

const { Header, Content } = Layout;
const { Title, Text } = Typography;

interface UserData {
  id: number;
  username: string;
  email: string;
  date_joined: string;
}

interface ApiStatus {
  status: string;
  message: string;
  user_count: number;
  version: string;
}

function App() {
  const [users, setUsers] = useState<UserData[]>([]);
  const [apiStatus, setApiStatus] = useState<ApiStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const fetchData = async () => {
    setRefreshing(true);
    try {
      // API 상태 확인
      const statusResponse = await fetch(`${API_URL}/api/status/`);
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setApiStatus(statusData);
      }

      // 사용자 목록 가져오기
      const usersResponse = await fetch(`${API_URL}/api/users/`, {
        credentials: 'include',
      });

      if (usersResponse.ok) {
        const usersData = await usersResponse.json();
        setUsers(usersData.results || usersData);
        message.success('데이터를 성공적으로 불러왔습니다.');
      } else {
        message.error('사용자 데이터를 가져오는데 실패했습니다.');
      }
    } catch (err) {
      message.error('API 연결에 실패했습니다.');
      console.error('API Error:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // 테이블 컬럼 정의
  const columns: ColumnsType<UserData> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
      render: (id) => <Tag color="blue">#{id}</Tag>
    },
    {
      title: '사용자명',
      dataIndex: 'username',
      key: 'username',
      render: (text) => (
        <Space>
          <UserOutlined />
          <strong>{text}</strong>
        </Space>
      ),
    },
    {
      title: '이메일',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: '가입일',
      dataIndex: 'date_joined',
      key: 'date_joined',
      render: (date) => new Date(date).toLocaleDateString('ko-KR'),
    },
    {
      title: '상태',
      key: 'status',
      render: () => (
        <Badge status="success" text="활성" />
      ),
    },
  ];

  // 인테리어 플랫폼 통계 데이터 (예시)
  const platformStats = {
    totalContracts: 156,
    activeProjects: 23,
    totalCompanies: 89,
    monthlyRevenue: 285000000,
  };

  return (
    <ConfigProvider locale={koKR}>
      <Layout className="app-container">
        <Header style={{
          background: '#fff',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <Title level={3} style={{ margin: 0 }}>
            🏠 TestPark 인테리어 플랫폼
          </Title>
          <Space>
            <Badge dot={apiStatus?.status === 'ok'}>
              <Button icon={<ApiOutlined />} type="text">
                API 상태
              </Button>
            </Badge>
            <Button
              type="primary"
              icon={refreshing ? <SyncOutlined spin /> : <ReloadOutlined />}
              onClick={fetchData}
              loading={refreshing}
            >
              새로고침
            </Button>
          </Space>
        </Header>

        <Content style={{ padding: '24px' }}>
          {/* 메인 통계 카드 */}
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} lg={6}>
              <Card hoverable>
                <Statistic
                  title="전체 계약"
                  value={platformStats.totalContracts}
                  prefix={<FileTextOutlined />}
                  suffix="건"
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card hoverable>
                <Statistic
                  title="진행중 프로젝트"
                  value={platformStats.activeProjects}
                  prefix={<CheckCircleOutlined />}
                  suffix="건"
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card hoverable>
                <Statistic
                  title="등록 업체"
                  value={platformStats.totalCompanies}
                  prefix={<ShopOutlined />}
                  suffix="개"
                  valueStyle={{ color: '#722ed1' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card hoverable>
                <Statistic
                  title="월 매출"
                  value={platformStats.monthlyRevenue}
                  prefix={<DollarOutlined />}
                  suffix="원"
                  precision={0}
                  valueStyle={{ color: '#fa8c16' }}
                />
              </Card>
            </Col>
          </Row>

          {/* API 상태 정보 */}
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={24}>
              <Card
                title="시스템 상태"
                extra={
                  apiStatus?.status === 'ok' ? (
                    <Tag color="success">정상 작동중</Tag>
                  ) : (
                    <Tag color="error">오류</Tag>
                  )
                }
              >
                <Row gutter={16}>
                  <Col span={6}>
                    <Statistic
                      title="API 버전"
                      value={apiStatus?.version || '1.0.0'}
                      prefix={<DatabaseOutlined />}
                    />
                  </Col>
                  <Col span={6}>
                    <Statistic
                      title="등록 사용자"
                      value={apiStatus?.user_count || users.length}
                      prefix={<TeamOutlined />}
                    />
                  </Col>
                  <Col span={12}>
                    <Text type="secondary">
                      Django Backend: {API_URL}
                    </Text>
                  </Col>
                </Row>
              </Card>
            </Col>
          </Row>

          {/* 사용자 테이블 */}
          <Card
            title="사용자 관리"
            extra={
              <Space>
                <Tag color="blue">총 {users.length}명</Tag>
                <Button type="primary">사용자 추가</Button>
              </Space>
            }
          >
            <Spin spinning={loading}>
              <Table
                columns={columns}
                dataSource={users}
                rowKey="id"
                pagination={{
                  pageSize: 10,
                  showTotal: (total) => `총 ${total}명`,
                  showSizeChanger: true,
                }}
              />
            </Spin>
          </Card>
        </Content>
      </Layout>
    </ConfigProvider>
  );
}

export default App;