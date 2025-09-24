// 업체 목록 컴포넌트 (회원관리)

import React from 'react';
import { Card, Empty, Button } from 'antd';
import { TeamOutlined, PlusOutlined } from '@ant-design/icons';

const CompanyList: React.FC = () => {
  return (
    <div style={{ padding: 24 }}>
      <h1 style={{ marginBottom: 24 }}>업체 목록</h1>
      <Card>
        <Empty
          image={<TeamOutlined style={{ fontSize: 64, color: '#d9d9d9' }} />}
          description={
            <span>
              업체 회원 관리 기능은 준비 중입니다.
              <br />
              기존 Django 관리자 페이지를 이용해주세요.
            </span>
          }
        >
          <Button type="primary" icon={<PlusOutlined />}>
            업체 추가
          </Button>
        </Empty>
      </Card>
    </div>
  );
};

export default CompanyList;