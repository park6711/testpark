// 통계 컴포넌트

import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  DatePicker,
  Select,
  Space,
  Progress,
  Table,
  Tag,
  Segmented,
  Button,
  Tooltip,
  Badge,
  Empty
} from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  AreaChartOutlined,
  BarChartOutlined,
  PieChartOutlined,
  LineChartOutlined,
  CalendarOutlined,
  TeamOutlined,
  FileTextOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
  DownloadOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { orderService } from '../services/orderService';
import { OrderStatistics } from '../types/order.types';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;

const Statistics: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [statistics, setStatistics] = useState<OrderStatistics | null>(null);
  const [viewType, setViewType] = useState<'overview' | 'status' | 'area' | 'trend'>('overview');
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().subtract(30, 'day'),
    dayjs()
  ]);

  useEffect(() => {
    loadStatistics();
  }, [dateRange]);

  const loadStatistics = async () => {
    try {
      setLoading(true);
      const stats = await orderService.getStatistics([
        dateRange[0].format('YYYY-MM-DD'),
        dateRange[1].format('YYYY-MM-DD')
      ]);
      setStatistics(stats);
    } catch (error) {
      console.error('통계 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const blob = await orderService.exportToExcel({
        dateRange: [
          dateRange[0].format('YYYY-MM-DD'),
          dateRange[1].format('YYYY-MM-DD')
        ]
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `의뢰통계_${dayjs().format('YYYYMMDD')}.xlsx`;
      a.click();
    } catch (error) {
      console.error('Excel 내보내기 실패:', error);
    }
  };

  // 상태별 통계 데이터
  const statusData = statistics ? Object.entries(statistics.byStatus).map(([status, count]) => ({
    status,
    count,
    percentage: Math.round((count / statistics.total) * 100)
  })) : [];

  // 지역별 통계 데이터
  const areaData = statistics ? Object.entries(statistics.byArea)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([area, count]) => ({
      area,
      count,
      percentage: Math.round((count / statistics.total) * 100)
    })) : [];

  const renderOverview = () => (
    <Row gutter={[16, 16]}>
      <Col xs={24} sm={12} lg={6}>
        <Card>
          <Statistic
            title="전체 의뢰"
            value={statistics?.total || 0}
            prefix={<FileTextOutlined />}
          />
          <div style={{ marginTop: 8 }}>
            <span style={{ fontSize: 12, color: '#999' }}>
              선택 기간 내 총 의뢰 수
            </span>
          </div>
        </Card>
      </Col>
      <Col xs={24} sm={12} lg={6}>
        <Card>
          <Statistic
            title="오늘 의뢰"
            value={statistics?.byDate.today || 0}
            valueStyle={{ color: '#3f8600' }}
            prefix={<CalendarOutlined />}
            suffix={
              <span style={{ fontSize: 14, color: '#3f8600' }}>
                <ArrowUpOutlined /> 12%
              </span>
            }
          />
          <Progress percent={30} size="small" showInfo={false} />
        </Card>
      </Col>
      <Col xs={24} sm={12} lg={6}>
        <Card>
          <Statistic
            title="전환율"
            value={statistics?.conversionRate || 0}
            precision={1}
            valueStyle={{ color: '#cf1322' }}
            suffix="%"
            prefix={<TrophyOutlined />}
          />
          <div style={{ marginTop: 8 }}>
            <Tag color="red">의뢰 → 계약</Tag>
          </div>
        </Card>
      </Col>
      <Col xs={24} sm={12} lg={6}>
        <Card>
          <Statistic
            title="평균 응답 시간"
            value={statistics?.averageResponseTime || 0}
            suffix="시간"
            prefix={<ClockCircleOutlined />}
          />
          <div style={{ marginTop: 8 }}>
            <Badge status="processing" text="실시간 업데이트" />
          </div>
        </Card>
      </Col>
    </Row>
  );

  const renderStatusChart = () => (
    <Card title="상태별 분포" loading={loading}>
      <Table
        dataSource={statusData}
        pagination={false}
        columns={[
          {
            title: '상태',
            dataIndex: 'status',
            key: 'status',
            render: (status) => (
              <Tag color={getStatusColor(status)}>{status}</Tag>
            )
          },
          {
            title: '건수',
            dataIndex: 'count',
            key: 'count',
            align: 'right'
          },
          {
            title: '비율',
            dataIndex: 'percentage',
            key: 'percentage',
            render: (percentage) => (
              <Progress
                percent={percentage}
                size="small"
                strokeColor={{
                  '0%': '#87d068',
                  '50%': '#ffe58f',
                  '100%': '#ffccc7'
                }}
              />
            )
          }
        ]}
      />
    </Card>
  );

  const renderAreaChart = () => (
    <Card title="지역별 TOP 10" loading={loading}>
      {areaData.length > 0 ? (
        <Table
          dataSource={areaData}
          pagination={false}
          columns={[
            {
              title: '순위',
              key: 'rank',
              render: (_, __, index) => (
                <Badge
                  count={index + 1}
                  style={{
                    backgroundColor: index < 3 ? '#52c41a' : '#999'
                  }}
                />
              )
            },
            {
              title: '지역',
              dataIndex: 'area',
              key: 'area',
              render: (area) => <strong>{area}</strong>
            },
            {
              title: '건수',
              dataIndex: 'count',
              key: 'count',
              align: 'right'
            },
            {
              title: '비율',
              dataIndex: 'percentage',
              key: 'percentage',
              render: (percentage) => `${percentage}%`
            }
          ]}
        />
      ) : (
        <Empty description="데이터가 없습니다" />
      )}
    </Card>
  );

  const renderTrendChart = () => (
    <Card title="일별 추이" loading={loading}>
      <div style={{ textAlign: 'center', padding: '40px 0' }}>
        <AreaChartOutlined style={{ fontSize: 48, color: '#1890ff' }} />
        <p style={{ marginTop: 16, color: '#999' }}>
          차트 컴포넌트는 별도 라이브러리 설치가 필요합니다
        </p>
        <p style={{ color: '#666' }}>
          Recharts 또는 Chart.js를 설치하여 구현하세요
        </p>
      </div>
    </Card>
  );

  const getStatusColor = (status: string): string => {
    const colorMap: Record<string, string> = {
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

  return (
    <div style={{ padding: 24 }}>
      {/* 헤더 */}
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <h1 style={{ margin: 0 }}>통계</h1>
        </Col>
        <Col>
          <Space>
            <RangePicker
              value={dateRange}
              onChange={(dates) => dates && setDateRange(dates as [dayjs.Dayjs, dayjs.Dayjs])}
              presets={[
                { label: '오늘', value: [dayjs(), dayjs()] },
                { label: '이번 주', value: [dayjs().startOf('week'), dayjs()] },
                { label: '이번 달', value: [dayjs().startOf('month'), dayjs()] },
                { label: '최근 30일', value: [dayjs().subtract(30, 'day'), dayjs()] },
                { label: '최근 90일', value: [dayjs().subtract(90, 'day'), dayjs()] }
              ]}
            />
            <Button
              icon={<ReloadOutlined />}
              onClick={loadStatistics}
              loading={loading}
            >
              새로고침
            </Button>
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={handleExport}
            >
              Excel 내보내기
            </Button>
          </Space>
        </Col>
      </Row>

      {/* 뷰 타입 선택 */}
      <Segmented
        options={[
          { label: '개요', value: 'overview', icon: <BarChartOutlined /> },
          { label: '상태별', value: 'status', icon: <PieChartOutlined /> },
          { label: '지역별', value: 'area', icon: <AreaChartOutlined /> },
          { label: '추이', value: 'trend', icon: <LineChartOutlined /> }
        ]}
        value={viewType}
        onChange={(value) => setViewType(value as any)}
        block
        style={{ marginBottom: 24 }}
      />

      {/* 콘텐츠 렌더링 */}
      {viewType === 'overview' && renderOverview()}
      {viewType === 'status' && (
        <Row gutter={[16, 16]}>
          <Col span={24}>{renderStatusChart()}</Col>
        </Row>
      )}
      {viewType === 'area' && (
        <Row gutter={[16, 16]}>
          <Col span={24}>{renderAreaChart()}</Col>
        </Row>
      )}
      {viewType === 'trend' && (
        <Row gutter={[16, 16]}>
          <Col span={24}>{renderTrendChart()}</Col>
        </Row>
      )}
    </div>
  );
};

export default Statistics;