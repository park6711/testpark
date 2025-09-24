// 대시보드 컴포넌트

import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Space, Progress, Timeline, Table, Tag } from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  TeamOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  TrophyOutlined,
  AlertOutlined
} from '@ant-design/icons';
import { orderService } from '../services/orderService';
import { Order, OrderStatistics } from '../types/order.types';

interface StatisticCard {
  title: string;
  value: number | string;
  icon: React.ReactNode;
  color: string;
  trend?: {
    value: number;
    isUp: boolean;
  };
}

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [statistics, setStatistics] = useState<OrderStatistics | null>(null);
  const [recentOrders, setRecentOrders] = useState<Order[]>([]);
  const [statisticCards, setStatisticCards] = useState<StatisticCard[]>([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [stats, orders] = await Promise.all([
        orderService.getStatistics(),
        orderService.getOrders({ status: '대기중' })
      ]);

      setStatistics(stats);
      setRecentOrders(orders.results.slice(0, 5));

      // TODO(human) - 통계 카드 데이터 생성
      const cards = getStatisticCards();
      setStatisticCards(cards);
    } catch (error) {
      console.error('대시보드 데이터 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatisticCards = (): StatisticCard[] => {
    // TODO(human): 대시보드에 표시할 통계 카드 데이터를 생성하세요
    return [];
  };

  // 최근 활동 타임라인 (실제 데이터 기반)
  const getRecentActivities = () => {
    // 실제 의뢰 데이터에서 최근 활동 추출
    return recentOrders.slice(0, 4).map(order => {
      const time = order.time ? new Date(order.time) : new Date();
      const timeDiff = Date.now() - time.getTime();
      const minutes = Math.floor(timeDiff / 60000);
      const hours = Math.floor(minutes / 60);

      let timeStr = '';
      if (minutes < 60) {
        timeStr = `${minutes}분 전`;
      } else if (hours < 24) {
        timeStr = `${hours}시간 전`;
      } else {
        timeStr = time.toLocaleDateString('ko-KR');
      }

      const statusColorMap: Record<string, string> = {
        '대기중': 'blue',
        '할당': 'green',
        '계약': 'green',
        '취소': 'red',
        '반려': 'orange'
      };

      return {
        time: timeStr,
        content: `의뢰 #${order.no} - ${order.sName || '고객'} (${order.recent_status})`,
        color: statusColorMap[order.recent_status] || 'gray'
      };
    });
  };

  // 최근 의뢰 테이블 컬럼
  const orderColumns = [
    { title: '번호', dataIndex: 'no', key: 'no', width: 80 },
    { title: '고객명', dataIndex: 'sName', key: 'sName' },
    { title: '지역', dataIndex: 'sArea', key: 'sArea' },
    {
      title: '상태',
      dataIndex: 'recent_status',
      key: 'recent_status',
      render: (status: string) => <Tag color="processing">{status}</Tag>
    }
  ];

  return (
    <div style={{ padding: 24 }}>
      <h1 style={{ marginBottom: 24 }}>대시보드</h1>

      {/* 통계 카드 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {statisticCards.map((card, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <Card loading={loading}>
              <Statistic
                title={card.title}
                value={card.value}
                prefix={card.icon}
                valueStyle={{ color: card.color }}
                suffix={
                  card.trend && (
                    <span style={{ fontSize: 14, color: card.trend.isUp ? '#52c41a' : '#f5222d' }}>
                      {card.trend.isUp ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                      {Math.abs(card.trend.value)}%
                    </span>
                  )
                }
              />
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[16, 16]}>
        {/* 처리 현황 */}
        <Col xs={24} lg={8}>
          <Card title="처리 현황" loading={loading}>
            <div style={{ padding: '20px 0' }}>
              <Progress
                type="dashboard"
                percent={statistics?.conversionRate || 0}
                format={(percent) => `${percent}%`}
              />
              <div style={{ textAlign: 'center', marginTop: 16 }}>
                <div>전환율</div>
                <small style={{ color: '#999' }}>의뢰 → 계약</small>
              </div>
            </div>
          </Card>
        </Col>

        {/* 최근 활동 */}
        <Col xs={24} lg={8}>
          <Card title="최근 활동" loading={loading}>
            <Timeline>
              {getRecentActivities().map((activity, index) => (
                <Timeline.Item key={index} color={activity.color}>
                  <p>{activity.content}</p>
                  <small style={{ color: '#999' }}>{activity.time}</small>
                </Timeline.Item>
              ))}
            </Timeline>
          </Card>
        </Col>

        {/* 최근 의뢰 */}
        <Col xs={24} lg={8}>
          <Card title="최근 의뢰" loading={loading}>
            <Table
              dataSource={recentOrders}
              columns={orderColumns}
              pagination={false}
              size="small"
              rowKey="no"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;