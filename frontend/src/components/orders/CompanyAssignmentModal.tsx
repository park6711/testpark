// 스마트 업체 할당 모달 컴포넌트

import React, { useState, useEffect } from 'react';
import {
  Modal,
  Table,
  Tag,
  Space,
  Button,
  Badge,
  Tooltip,
  Progress,
  Alert,
  Row,
  Col,
  Statistic,
  Card,
  Divider,
  Checkbox,
  message,
  Spin,
  Empty,
  Typography,
  List,
  Avatar,
  Timeline
} from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  EnvironmentOutlined,
  CalendarOutlined,
  TeamOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  StopOutlined,
  ThunderboltOutlined,
  HomeOutlined,
  ShopOutlined,
  BuildOutlined,
  ToolOutlined,
  ClockCircleOutlined,
  UserOutlined,
  PhoneOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { Order } from '../../types/order.types';
import { orderService } from '../../services/orderService';
import dayjs from 'dayjs';

const { Text, Title, Paragraph } = Typography;

interface CompanyRecommendation {
  company_id: number;
  company_name: string;
  match_score: number; // 매칭 점수 (0-100)
  available: boolean;
  reasons: {
    area_match: boolean;
    construction_type_match: boolean;
    schedule_available: boolean;
    capacity_available: boolean;
    status_normal: boolean;
  };
  details: {
    areas: string[];
    construction_types: string[];
    current_capacity: number;
    max_capacity: number;
    stop_period?: { start: string; end: string };
    impossible_dates?: string[];
    distance_km?: number;
  };
  warnings?: string[];
  recommendations?: string[];
}

interface AssignmentModalProps {
  visible: boolean;
  order: Order | null;
  onClose: () => void;
  onAssign: (companyId: number) => void;
}

const CompanyAssignmentModal: React.FC<AssignmentModalProps> = ({
  visible,
  order,
  onClose,
  onAssign
}) => {
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<CompanyRecommendation[]>([]);
  const [selectedCompanies, setSelectedCompanies] = useState<number[]>([]);
  const [assignmentMode, setAssignmentMode] = useState<'single' | 'multiple'>('single');

  useEffect(() => {
    if (visible && order) {
      loadRecommendations();
    }
  }, [visible, order]);

  const loadRecommendations = async () => {
    if (!order) return;

    setLoading(true);
    try {
      // API 호출하여 추천 업체 목록 가져오기
      const response = await fetch('/order/api/recommend_companies/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': (window as any).__DJANGO_CONTEXT__?.csrfToken || ''
        },
        body: JSON.stringify({
          order_id: order.no,
          area: order.sArea,
          construction_type: order.sConstruction,
          scheduled_date: order.dateSchedule,
          designation: order.designation
        })
      });

      if (response.ok) {
        const data = await response.json();
        setRecommendations(data.recommendations || []);
      }
    } catch (error) {
      console.error('업체 추천 로드 실패:', error);
      // 더미 데이터로 테스트
      setRecommendations(getMockRecommendations());
    } finally {
      setLoading(false);
    }
  };

  // 테스트용 더미 데이터
  const getMockRecommendations = (): CompanyRecommendation[] => [
    {
      company_id: 1,
      company_name: '한솔인테리어',
      match_score: 95,
      available: true,
      reasons: {
        area_match: true,
        construction_type_match: true,
        schedule_available: true,
        capacity_available: true,
        status_normal: true
      },
      details: {
        areas: ['서울 강남구', '서울 서초구', '서울 송파구'],
        construction_types: ['올수리', '부분수리'],
        current_capacity: 12,
        max_capacity: 20,
        distance_km: 3.5
      },
      recommendations: ['최근 고객 만족도 98%', '해당 지역 경험 많음']
    },
    {
      company_id: 2,
      company_name: '드림하우스',
      match_score: 82,
      available: true,
      reasons: {
        area_match: true,
        construction_type_match: true,
        schedule_available: true,
        capacity_available: true,
        status_normal: true
      },
      details: {
        areas: ['서울 강남구', '서울 강동구'],
        construction_types: ['올수리'],
        current_capacity: 8,
        max_capacity: 15,
        distance_km: 5.2
      },
      warnings: ['현재 처리량 53% (약간 높음)']
    },
    {
      company_id: 3,
      company_name: '모던스페이스',
      match_score: 65,
      available: false,
      reasons: {
        area_match: true,
        construction_type_match: true,
        schedule_available: false,
        capacity_available: true,
        status_normal: true
      },
      details: {
        areas: ['서울 전체'],
        construction_types: ['올수리', '부분수리', '신축'],
        current_capacity: 5,
        max_capacity: 10,
        impossible_dates: ['2024-01-15', '2024-01-16', '2024-01-17']
      },
      warnings: ['해당 일정 공사 불가']
    }
  ];

  const handleAssign = () => {
    if (selectedCompanies.length === 0) {
      message.warning('할당할 업체를 선택해주세요.');
      return;
    }

    if (assignmentMode === 'single') {
      onAssign(selectedCompanies[0]);
      message.success('업체가 할당되었습니다.');
    } else {
      // 다중 할당 로직
      selectedCompanies.forEach(companyId => onAssign(companyId));
      message.success(`${selectedCompanies.length}개 업체가 할당되었습니다.`);
    }
    onClose();
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return '#52c41a';
    if (score >= 70) return '#1890ff';
    if (score >= 50) return '#faad14';
    return '#ff4d4f';
  };

  const getConstructionIcon = (type: string) => {
    if (type.includes('올수리')) return <HomeOutlined />;
    if (type.includes('부분')) return <ToolOutlined />;
    if (type.includes('신축')) return <BuildOutlined />;
    if (type.includes('상가') || type.includes('상업')) return <ShopOutlined />;
    return <ToolOutlined />;
  };

  const columns: ColumnsType<CompanyRecommendation> = [
    {
      title: '선택',
      key: 'select',
      width: 60,
      fixed: 'left',
      render: (_, record) => (
        <Checkbox
          checked={selectedCompanies.includes(record.company_id)}
          disabled={!record.available}
          onChange={(e) => {
            if (e.target.checked) {
              if (assignmentMode === 'single') {
                setSelectedCompanies([record.company_id]);
              } else {
                setSelectedCompanies([...selectedCompanies, record.company_id]);
              }
            } else {
              setSelectedCompanies(selectedCompanies.filter(id => id !== record.company_id));
            }
          }}
        />
      )
    },
    {
      title: '업체명',
      key: 'company',
      width: 200,
      render: (_, record) => (
        <Space direction="vertical" size={0}>
          <Space>
            <Avatar icon={<TeamOutlined />} size="small" />
            <Text strong>{record.company_name}</Text>
          </Space>
          {record.details.distance_km && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              <EnvironmentOutlined /> {record.details.distance_km}km
            </Text>
          )}
        </Space>
      )
    },
    {
      title: '매칭 점수',
      key: 'score',
      width: 120,
      sorter: (a, b) => a.match_score - b.match_score,
      defaultSortOrder: 'descend',
      render: (_, record) => (
        <div style={{ textAlign: 'center' }}>
          <Progress
            type="circle"
            percent={record.match_score}
            width={50}
            strokeColor={getScoreColor(record.match_score)}
            format={(percent) => `${percent}점`}
          />
          {record.match_score >= 90 && (
            <div style={{ marginTop: 4 }}>
              <Badge status="success" text="최적" />
            </div>
          )}
        </div>
      )
    },
    {
      title: '매칭 상태',
      key: 'status',
      width: 300,
      render: (_, record) => (
        <Space direction="vertical" size={4} style={{ width: '100%' }}>
          <Space wrap>
            <Tooltip title="지역 매칭">
              <Tag
                color={record.reasons.area_match ? 'green' : 'red'}
                icon={record.reasons.area_match ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
              >
                지역
              </Tag>
            </Tooltip>
            <Tooltip title="공사 종류 매칭">
              <Tag
                color={record.reasons.construction_type_match ? 'green' : 'red'}
                icon={record.reasons.construction_type_match ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
              >
                공사
              </Tag>
            </Tooltip>
            <Tooltip title="일정 가능">
              <Tag
                color={record.reasons.schedule_available ? 'green' : 'red'}
                icon={record.reasons.schedule_available ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
              >
                일정
              </Tag>
            </Tooltip>
            <Tooltip title={`처리능력: ${record.details.current_capacity}/${record.details.max_capacity}`}>
              <Tag
                color={record.reasons.capacity_available ? 'green' : 'red'}
                icon={record.reasons.capacity_available ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
              >
                능력
              </Tag>
            </Tooltip>
          </Space>
          {record.warnings && record.warnings.length > 0 && (
            <Alert
              message={record.warnings[0]}
              type="warning"
              showIcon
              style={{ padding: '2px 8px', fontSize: 12 }}
            />
          )}
        </Space>
      )
    },
    {
      title: '가능 지역',
      key: 'areas',
      width: 200,
      render: (_, record) => (
        <Space direction="vertical" size={2}>
          {record.details.areas.slice(0, 3).map(area => (
            <Tag key={area} icon={<EnvironmentOutlined />} color="blue">
              {area}
            </Tag>
          ))}
          {record.details.areas.length > 3 && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              외 {record.details.areas.length - 3}개 지역
            </Text>
          )}
        </Space>
      )
    },
    {
      title: '가능 공사',
      key: 'construction',
      width: 150,
      render: (_, record) => (
        <Space wrap>
          {record.details.construction_types.map(type => (
            <Tag key={type} icon={getConstructionIcon(type)}>
              {type}
            </Tag>
          ))}
        </Space>
      )
    },
    {
      title: '처리 능력',
      key: 'capacity',
      width: 120,
      render: (_, record) => {
        const percentage = (record.details.current_capacity / record.details.max_capacity) * 100;
        return (
          <Tooltip title={`현재 ${record.details.current_capacity}건 / 최대 ${record.details.max_capacity}건`}>
            <Progress
              percent={percentage}
              size="small"
              status={percentage >= 80 ? 'exception' : 'normal'}
              format={() => `${record.details.current_capacity}/${record.details.max_capacity}`}
            />
          </Tooltip>
        );
      }
    }
  ];

  const expandedRowRender = (record: CompanyRecommendation) => (
    <Row gutter={16}>
      <Col span={8}>
        <Card size="small" title="추천 이유">
          <List
            size="small"
            dataSource={record.recommendations || []}
            renderItem={item => (
              <List.Item>
                <Space>
                  <ThunderboltOutlined style={{ color: '#52c41a' }} />
                  <Text>{item}</Text>
                </Space>
              </List.Item>
            )}
          />
        </Card>
      </Col>
      <Col span={8}>
        <Card size="small" title="주의 사항">
          {record.warnings && record.warnings.length > 0 ? (
            <List
              size="small"
              dataSource={record.warnings}
              renderItem={item => (
                <List.Item>
                  <Space>
                    <WarningOutlined style={{ color: '#faad14' }} />
                    <Text>{item}</Text>
                  </Space>
                </List.Item>
              )}
            />
          ) : (
            <Empty description="특별한 주의사항 없음" />
          )}
        </Card>
      </Col>
      <Col span={8}>
        <Card size="small" title="공사 불가일">
          {record.details.impossible_dates && record.details.impossible_dates.length > 0 ? (
            <Timeline>
              {record.details.impossible_dates.map(date => (
                <Timeline.Item
                  key={date}
                  color="red"
                  dot={<CloseCircleOutlined />}
                >
                  {dayjs(date).format('YYYY년 MM월 DD일')}
                </Timeline.Item>
              ))}
            </Timeline>
          ) : (
            <Empty description="공사 불가일 없음" />
          )}
        </Card>
      </Col>
    </Row>
  );

  return (
    <Modal
      title={
        <Space>
          <TeamOutlined />
          <span>스마트 업체 할당</span>
          <Badge count={`추천 ${recommendations.filter(r => r.available).length}개`} />
        </Space>
      }
      open={visible}
      onCancel={onClose}
      width={1400}
      footer={[
        <Button key="cancel" onClick={onClose}>
          취소
        </Button>,
        <Button
          key="assign"
          type="primary"
          onClick={handleAssign}
          disabled={selectedCompanies.length === 0}
          icon={<CheckCircleOutlined />}
        >
          선택한 업체 할당 ({selectedCompanies.length}개)
        </Button>
      ]}
    >
      {order && (
        <>
          {/* 의뢰 정보 요약 */}
          <Card size="small" style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col span={6}>
                <Statistic
                  title="고객명"
                  value={order.sName || '-'}
                  prefix={<UserOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="공사 지역"
                  value={order.sArea || '-'}
                  prefix={<EnvironmentOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="공사 예정일"
                  value={order.dateSchedule || '-'}
                  prefix={<CalendarOutlined />}
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="공사 내용"
                  value={order.sConstruction || '-'}
                  prefix={<ToolOutlined />}
                />
              </Col>
            </Row>
          </Card>

          {/* 할당 모드 선택 */}
          <Alert
            message={
              <Space>
                <Text>할당 모드:</Text>
                <Button
                  size="small"
                  type={assignmentMode === 'single' ? 'primary' : 'default'}
                  onClick={() => {
                    setAssignmentMode('single');
                    setSelectedCompanies([]);
                  }}
                >
                  단일 할당
                </Button>
                <Button
                  size="small"
                  type={assignmentMode === 'multiple' ? 'primary' : 'default'}
                  onClick={() => {
                    setAssignmentMode('multiple');
                    setSelectedCompanies([]);
                  }}
                >
                  다중 할당 (공동구매)
                </Button>
              </Space>
            }
            type="info"
            style={{ marginBottom: 16 }}
          />

          <Divider>추천 업체 목록</Divider>

          {/* 업체 추천 테이블 */}
          <Table
            columns={columns}
            dataSource={recommendations}
            rowKey="company_id"
            loading={loading}
            expandable={{
              expandedRowRender,
              expandRowByClick: false
            }}
            pagination={false}
            scroll={{ x: 1200, y: 400 }}
            rowClassName={(record) => !record.available ? 'disabled-row' : ''}
          />

          {/* 범례 */}
          <div style={{ marginTop: 16, padding: 12, background: '#f5f5f5', borderRadius: 4 }}>
            <Space wrap>
              <Text type="secondary">매칭 점수:</Text>
              <Badge status="success" text="90점 이상 (최적)" />
              <Badge status="processing" text="70-89점 (적합)" />
              <Badge status="warning" text="50-69점 (보통)" />
              <Badge status="error" text="50점 미만 (부적합)" />
            </Space>
          </div>
        </>
      )}
    </Modal>
  );
};

export default CompanyAssignmentModal;