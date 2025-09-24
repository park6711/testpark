// 메모 모달 컴포넌트 (Ant Design)

import React, { useState } from 'react';
import { Modal, Input, Button, List, Typography, Space, message, Empty, Alert } from 'antd';
import { MessageOutlined, UserOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { MemoData } from '../../types';

const { TextArea } = Input;
const { Text, Title } = Typography;

interface MemoModalProps {
  isOpen: boolean;
  onClose: () => void;
  orderId: number;
  orderName: string;
  memos: MemoData[];
  onAddMemo: (content: string) => Promise<{ success: boolean; error?: string }>;
}

const MemoModal: React.FC<MemoModalProps> = ({
  isOpen,
  onClose,
  orderId,
  orderName,
  memos = [],
  onAddMemo
}) => {
  const [newMemo, setNewMemo] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!newMemo.trim()) {
      message.warning('메모 내용을 입력해주세요.');
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await onAddMemo(newMemo);
      if (result.success) {
        message.success('메모가 추가되었습니다.');
        setNewMemo('');
      } else {
        message.error(result.error || '메모 추가 중 오류가 발생했습니다.');
      }
    } catch (err) {
      message.error('메모 추가 중 오류가 발생했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Modal
      title={
        <Space>
          <MessageOutlined />
          <span>메모 관리 - {orderName}</span>
        </Space>
      }
      open={isOpen}
      onCancel={onClose}
      width={700}
      footer={null}
      destroyOnClose
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* 새 메모 입력 섹션 */}
        <div style={{ background: '#f5f5f5', padding: 16, borderRadius: 8 }}>
          <Title level={5}>새 메모 작성</Title>
          <TextArea
            value={newMemo}
            onChange={(e) => setNewMemo(e.target.value)}
            placeholder="메모 내용을 입력하세요..."
            rows={4}
            disabled={isSubmitting}
            style={{ marginBottom: 12 }}
          />
          <Button
            type="primary"
            onClick={handleSubmit}
            loading={isSubmitting}
            disabled={!newMemo.trim()}
          >
            메모 추가
          </Button>
        </div>

        {/* 기존 메모 목록 */}
        <div>
          <Title level={5}>메모 목록 ({memos.length}개)</Title>
          {memos.length === 0 ? (
            <Empty description="등록된 메모가 없습니다." />
          ) : (
            <List
              dataSource={memos}
              renderItem={(memo) => (
                <List.Item style={{ background: 'white', marginBottom: 8, padding: 16, borderRadius: 8, border: '1px solid #f0f0f0' }}>
                  <List.Item.Meta
                    title={
                      <Space>
                        <UserOutlined />
                        <Text strong>{memo.author}</Text>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          <ClockCircleOutlined style={{ marginRight: 4 }} />
                          {formatDate(memo.created_at)}
                        </Text>
                      </Space>
                    }
                    description={
                      <Text style={{ whiteSpace: 'pre-wrap' }}>{memo.content}</Text>
                    }
                  />
                </List.Item>
              )}
              style={{ maxHeight: 400, overflow: 'auto' }}
            />
          )}
        </div>
      </Space>
    </Modal>
  );
};

export default MemoModal;