import React, { useState, useEffect } from 'react';
import { Modal, Input, Button, Form, Space, message, Tabs } from 'antd';
import { EditOutlined, LinkOutlined, SendOutlined } from '@ant-design/icons';
import { OrderData } from '../../types';

interface NaverCafeModalProps {
  visible: boolean;
  order: OrderData | null;
  onClose: () => void;
  onUpdateLink: (orderId: number, link: string) => void;
  onRefresh: () => void;
}

const NaverCafeModal: React.FC<NaverCafeModalProps> = ({
  visible,
  order,
  onClose,
  onUpdateLink,
  onRefresh
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('edit');
  const [formattedContent, setFormattedContent] = useState({ title: '', content: '' });

  useEffect(() => {
    if (order && visible) {
      // 게시글 링크 설정
      form.setFieldsValue({
        postLink: order.post_link || ''
      });

      // 게시글 내용 포맷팅
      formatPostContent(order);
    }
  }, [order, visible, form]);

  const formatPostContent = (orderData: OrderData) => {
    const title = `[${orderData.sArea || ''}] 인테리어 견적문의 - ${orderData.sName}님`;

    const content = `안녕하세요. 인테리어 견적문의 드립니다.

=====================================
▶ 고객정보
=====================================
- 성함: ${orderData.sName || ''}
- 연락처: ${orderData.sPhone || ''}
- 네이버ID: ${orderData.sNaverID || ''}
- 별명: ${orderData.sNick || ''}

=====================================
▶ 공사정보
=====================================
- 공사지역: ${orderData.sArea || ''}
- 공사예정일: ${orderData.dateSchedule || ''}
- 지정업체: ${orderData.designation || '미정'}

=====================================
▶ 공사내용
=====================================
${orderData.sConstruction || ''}

=====================================
▶ 기타사항
=====================================
- 접수번호: ${orderData.no}
- 접수일시: ${orderData.time}
- 처리상태: ${orderData.recent_status || '대기중'}

=====================================

빠른 견적 부탁드립니다.
감사합니다.`;

    setFormattedContent({ title, content });
    form.setFieldsValue({ title, content });
  };

  const handleLinkUpdate = async () => {
    try {
      const values = await form.validateFields(['postLink']);
      if (order) {
        await onUpdateLink(order.no, values.postLink);
        message.success('게시글 링크가 수정되었습니다');
        onRefresh();
        onClose();
      }
    } catch (error) {
      message.error('링크 수정 중 오류가 발생했습니다');
    }
  };

  const handlePost = async () => {
    try {
      setLoading(true);
      const values = await form.validateFields(['title', 'content']);

      if (!order) return;

      // 네이버 카페 게시 API 호출
      const response = await fetch(`/order/api/orders/${order.no}/post_to_cafe/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          auto_post: true,
          custom_title: values.title,
          custom_content: values.content
        }),
      });

      const data = await response.json();

      if (data.status === 'success') {
        message.success('네이버 카페에 게시되었습니다!');
        if (data.post_link) {
          await onUpdateLink(order.no, data.post_link);
        }
        onRefresh();
        onClose();
      } else if (data.status === 'manual_required') {
        // 수동 게시 필요 - 클립보드에 복사
        const fullContent = `${values.title}\n\n${values.content}`;
        await navigator.clipboard.writeText(fullContent);
        message.info('게시글 내용이 클립보드에 복사되었습니다. 네이버 카페에 직접 게시해주세요.');

        // 네이버 카페 열기
        window.open('https://cafe.naver.com/f-e/cafes/29829680/menus/26', '_blank');
      } else {
        message.error(data.message || '게시 중 오류가 발생했습니다');
      }
    } catch (error) {
      message.error('게시 중 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyContent = async () => {
    try {
      const values = form.getFieldsValue(['title', 'content']);
      const fullContent = `${values.title}\n\n${values.content}`;
      await navigator.clipboard.writeText(fullContent);
      message.success('클립보드에 복사되었습니다');
    } catch (error) {
      message.error('복사 중 오류가 발생했습니다');
    }
  };

  return (
    <Modal
      title="네이버 카페 게시글 관리"
      visible={visible}
      onCancel={onClose}
      width={800}
      footer={null}
    >
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <Tabs.TabPane tab="게시글 링크 수정" key="edit">
          <Form form={form} layout="vertical">
            <Form.Item
              label="게시글 링크"
              name="postLink"
              rules={[{ type: 'url', message: '올바른 URL을 입력해주세요' }]}
            >
              <Input
                prefix={<LinkOutlined />}
                placeholder="https://cafe.naver.com/f-e/29829680/123456"
              />
            </Form.Item>
            <Form.Item>
              <Button type="primary" onClick={handleLinkUpdate}>
                링크 저장
              </Button>
            </Form.Item>
          </Form>
        </Tabs.TabPane>

        <Tabs.TabPane tab="카페 게시글 작성" key="post">
          <Form form={form} layout="vertical">
            <Form.Item
              label="제목"
              name="title"
              rules={[{ required: true, message: '제목을 입력해주세요' }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              label="내용"
              name="content"
              rules={[{ required: true, message: '내용을 입력해주세요' }]}
            >
              <Input.TextArea rows={15} />
            </Form.Item>
            <Form.Item>
              <Space>
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={handlePost}
                  loading={loading}
                >
                  네이버 카페에 게시
                </Button>
                <Button onClick={handleCopyContent}>
                  내용 복사
                </Button>
                <Button
                  type="link"
                  onClick={() => window.open('https://cafe.naver.com/f-e/cafes/29829680/menus/26', '_blank')}
                >
                  카페 바로가기
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Tabs.TabPane>
      </Tabs>
    </Modal>
  );
};

export default NaverCafeModal;