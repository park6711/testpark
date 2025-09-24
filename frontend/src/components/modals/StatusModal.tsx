// 상태 변경 모달 컴포넌트 (Ant Design)

import React, { useState } from 'react';
import { Modal, Radio, Input, Button, Space, Typography, Tag, message, Alert } from 'antd';
import { EditOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { STATUS_OPTIONS } from '../../constants';

const { TextArea } = Input;
const { Text, Title } = Typography;

interface StatusModalProps {
  isOpen: boolean;
  onClose: () => void;
  orderId: number;
  orderName: string;
  currentStatus: string;
  onStatusUpdate: (status: string, note?: string) => Promise<{ success: boolean; error?: string }>;
}

const StatusModal: React.FC<StatusModalProps> = ({
  isOpen,
  onClose,
  orderId,
  orderName,
  currentStatus,
  onStatusUpdate
}) => {
  const [selectedStatus, setSelectedStatus] = useState(currentStatus);
  const [note, setNote] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!selectedStatus) {
      message.warning('상태를 선택해주세요.');
      return;
    }

    if (selectedStatus === currentStatus) {
      message.info('현재 상태와 동일합니다.');
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await onStatusUpdate(selectedStatus, note);
      if (result.success) {
        message.success('상태가 변경되었습니다.');
        onClose();
      } else {
        message.error(result.error || '상태 변경 중 오류가 발생했습니다.');
      }
    } catch (err) {
      message.error('상태 변경 중 오류가 발생했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    setSelectedStatus(currentStatus);
    setNote('');
    onClose();
  };

  return (
    <Modal
      title={
        <Space>
          <EditOutlined />
          <span>상태 변경 - {orderName}</span>
        </Space>
      }
      open={isOpen}
      onCancel={handleCancel}
      width={600}
      footer={[
        <Button key="cancel" onClick={handleCancel} disabled={isSubmitting}>
          취소
        </Button>,
        <Button
          key="submit"
          type="primary"
          onClick={handleSubmit}
          loading={isSubmitting}
          disabled={selectedStatus === currentStatus}
          icon={<CheckCircleOutlined />}
        >
          상태 변경
        </Button>
      ]}
      destroyOnClose
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* 현재 상태 표시 */}
        <Alert
          message="현재 상태"
          description={
            <Tag
              color={STATUS_OPTIONS.find(opt => opt.value === currentStatus)?.color}
              style={{ fontSize: 14, padding: '4px 12px' }}
            >
              {currentStatus}
            </Tag>
          }
          type="info"
          showIcon
        />

        {/* 상태 선택 */}
        <div>
          <Title level={5} style={{ marginBottom: 16 }}>변경할 상태</Title>
          <Radio.Group
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            disabled={isSubmitting}
            style={{ width: '100%' }}
          >
            <Space wrap>
              {STATUS_OPTIONS.map((status) => (
                <Radio.Button
                  key={status.value}
                  value={status.value}
                  style={{
                    borderColor: status.color,
                    color: selectedStatus === status.value ? 'white' : status.color,
                    backgroundColor: selectedStatus === status.value ? status.color : 'white',
                    fontWeight: selectedStatus === status.value ? 'bold' : 'normal'
                  }}
                >
                  {status.label}
                </Radio.Button>
              ))}
            </Space>
          </Radio.Group>
        </div>

        {/* 변경 사유 입력 */}
        <div>
          <Title level={5} style={{ marginBottom: 8 }}>변경 사유 (선택사항)</Title>
          <TextArea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="상태 변경 사유를 입력하세요..."
            rows={3}
            disabled={isSubmitting}
          />
        </div>

        {/* 변경 예정 상태 미리보기 */}
        {selectedStatus !== currentStatus && (
          <Alert
            message="변경 예정"
            description={
              <Space>
                <Tag
                  color={STATUS_OPTIONS.find(opt => opt.value === currentStatus)?.color}
                >
                  {currentStatus}
                </Tag>
                <span>→</span>
                <Tag
                  color={STATUS_OPTIONS.find(opt => opt.value === selectedStatus)?.color}
                  style={{ fontSize: 14, padding: '4px 12px' }}
                >
                  {selectedStatus}
                </Tag>
              </Space>
            }
            type="success"
            showIcon
          />
        )}
      </Space>
    </Modal>
  );
};

export default StatusModal;