import React from 'react';
import { Layout, Menu, Typography } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  FileTextOutlined,
  TeamOutlined,
  BarChartOutlined
} from '@ant-design/icons';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '대시보드',
      onClick: () => navigate('/dashboard')
    },
    {
      key: 'order',
      icon: <FileTextOutlined />,
      label: '의뢰할당',
      children: [
        {
          key: '/order/list',
          label: '의뢰리스트',
          onClick: () => navigate('/order/list')
        },
        {
          key: '/order/company',
          label: '업체관리',
          onClick: () => navigate('/order/company')
        },
        {
          key: '/order/statistics',
          label: '통계',
          onClick: () => navigate('/order/statistics')
        }
      ]
    },
    {
      key: 'member',
      icon: <TeamOutlined />,
      label: '회원관리',
      children: [
        {
          key: '/member/list',
          label: '회원목록',
          onClick: () => navigate('/member/list')
        },
        {
          key: '/member/company',
          label: '업체목록',
          onClick: () => navigate('/member/company')
        }
      ]
    },
    {
      key: 'report',
      icon: <BarChartOutlined />,
      label: '리포트',
      onClick: () => navigate('/report')
    }
  ];

  // 현재 경로에 맞는 메뉴 선택
  const selectedKeys = [location.pathname];
  const openKeys = location.pathname.startsWith('/order') ? ['order'] :
                   location.pathname.startsWith('/member') ? ['member'] : [];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        width={250}
        theme="dark"
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          <Title level={4} style={{ color: '#fff', margin: 0 }}>
            인테리어 플랫폼
          </Title>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={selectedKeys}
          defaultOpenKeys={openKeys}
          items={menuItems}
          style={{ borderRight: 0 }}
        />
      </Sider>
      <Layout style={{ marginLeft: 250 }}>
        <Content style={{ margin: 0, overflow: 'initial' }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;