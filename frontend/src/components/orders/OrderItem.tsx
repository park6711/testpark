// 의뢰 아이템 컴포넌트

import React from 'react';
import { ChevronDown, ChevronUp, MessageSquare, FileText, Edit } from 'lucide-react';
import { OrderData } from '../../types';
import { STATUS_OPTIONS } from '../../constants';

interface OrderItemProps {
  order: OrderData;
  isExpanded: boolean;
  isSelected: boolean;
  onToggleExpand: () => void;
  onToggleSelect: () => void;
  onOpenMemo: () => void;
  onOpenStatus: () => void;
  onOpenEdit: () => void;
}

const OrderItem: React.FC<OrderItemProps> = ({
  order,
  isExpanded,
  isSelected,
  onToggleExpand,
  onToggleSelect,
  onOpenMemo,
  onOpenStatus,
  onOpenEdit
}) => {
  const statusColor = STATUS_OPTIONS.find(s => s.value === order.recent_status)?.color || '#9E9E9E';

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <>
      <tr className={`hover:bg-gray-50 ${isSelected ? 'bg-blue-50' : ''}`}>
        {/* 선택 체크박스 */}
        <td className="px-4 py-3">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={onToggleSelect}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
        </td>

        {/* 번호 */}
        <td className="px-4 py-3 text-sm">{order.no}</td>

        {/* 접수일시 */}
        <td className="px-4 py-3 text-sm text-gray-600">
          {formatDate(order.time)}
        </td>

        {/* 고객 정보 */}
        <td className="px-4 py-3">
          <div className="text-sm">
            <div className="font-medium text-gray-900">{order.sName}</div>
            <div className="text-gray-500">{order.sPhone}</div>
          </div>
        </td>

        {/* 지역 */}
        <td className="px-4 py-3 text-sm">{order.sArea}</td>

        {/* 공사 내용 */}
        <td className="px-4 py-3 text-sm">
          <div className="max-w-xs truncate">{order.sConstruction}</div>
        </td>

        {/* 업체 */}
        <td className="px-4 py-3 text-sm">
          {order.assigned_company || '-'}
        </td>

        {/* 상태 */}
        <td className="px-4 py-3">
          <button
            onClick={onOpenStatus}
            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white transition-opacity hover:opacity-80"
            style={{ backgroundColor: statusColor }}
          >
            {order.recent_status}
          </button>
        </td>

        {/* 액션 버튼 */}
        <td className="px-4 py-3">
          <div className="flex items-center space-x-1">
            <button
              onClick={onOpenMemo}
              className="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
              title="메모"
            >
              <MessageSquare className="h-4 w-4" />
            </button>
            <button
              onClick={onOpenEdit}
              className="p-1.5 text-gray-500 hover:text-green-600 hover:bg-green-50 rounded transition-colors"
              title="수정"
            >
              <Edit className="h-4 w-4" />
            </button>
            <button
              onClick={onToggleExpand}
              className="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded transition-colors"
              title="상세보기"
            >
              {isExpanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </button>
          </div>
        </td>
      </tr>

      {/* 확장 상세 정보 */}
      {isExpanded && (
        <tr>
          <td colSpan={9} className="px-4 py-3 bg-gray-50">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-gray-600">네이버 ID:</span>
                <span className="ml-2 text-gray-900">{order.sNaverID}</span>
              </div>
              <div>
                <span className="font-medium text-gray-600">닉네임:</span>
                <span className="ml-2 text-gray-900">{order.sNick}</span>
              </div>
              <div>
                <span className="font-medium text-gray-600">유형:</span>
                <span className="ml-2 text-gray-900">{order.designation_type}</span>
              </div>
              <div>
                <span className="font-medium text-gray-600">재요청 횟수:</span>
                <span className="ml-2 text-gray-900">{order.re_request_count}회</span>
              </div>
              {order.post_link && (
                <div className="col-span-2">
                  <span className="font-medium text-gray-600">게시글 링크:</span>
                  <a
                    href={order.post_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-2 text-blue-600 hover:underline"
                  >
                    {order.post_link}
                  </a>
                </div>
              )}
              <div className="col-span-2">
                <span className="font-medium text-gray-600">상세 내용:</span>
                <p className="mt-1 text-gray-900">{order.sConstruction}</p>
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
};

export default OrderItem;