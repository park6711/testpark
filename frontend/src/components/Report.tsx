// 리포트 컴포넌트

import React from 'react';
import { Card, Empty, Button, Space } from 'antd';
import { FileTextOutlined, DownloadOutlined, BarChartOutlined } from '@ant-design/icons';

const Report: React.FC = () => {
  return (
    <div style={{ padding: 24 }}>
      <h1 style={{ marginBottom: 24 }}>리포트</h1>
      <Card>
        <Empty
          image={<BarChartOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />}
          description={
            <span>
              리포트 기능은 준비 중입니다.
              <br />
              통계 페이지에서 기본적인 데이터를 확인하실 수 있습니다.
            </span>
          }
        >
          <Space>
            <Button type="primary" icon={<FileTextOutlined />}>
              리포트 생성
            </Button>
            <Button icon={<DownloadOutlined />}>
              샘플 다운로드
            </Button>
          </Space>
        </Empty>
      </Card>
    </div>
  );
};

export default Report;