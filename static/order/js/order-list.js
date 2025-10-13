/**
 * 의뢰 리스트 페이지 전용 스크립트
 * order_list.html의 인라인 스크립트를 외부 파일로 분리
 */

(function() {
    'use strict';

    const { getCookie, apiCall } = window.OrderUtils;

    // 전체 선택 체크박스 핸들러
    window.handleSelectAll = function(checkbox) {
        const checkboxes = document.querySelectorAll('.row-checkbox');
        checkboxes.forEach(cb => {
            cb.checked = checkbox.checked;
            const row = cb.closest('tr');
            if (row) {
                row.classList.toggle('selected', checkbox.checked);
            }
        });
    };

    // 의뢰 수정 함수
    window.editOrder = function(orderNo) {
        if (window.Toast) {
            window.Toast.info(`의뢰 #${orderNo} 수정 기능은 다음 단계에서 구현됩니다.`);
        } else {
            alert(`의뢰 #${orderNo} 수정 기능은 다음 단계에서 구현됩니다.`);
        }
    };

    // 상세보기 모달 표시
    window.showDetailModal = function(orderNo) {
        if (typeof window.viewOrder === 'function') {
            window.viewOrder(orderNo);
        } else {
            console.error('viewOrder 함수를 찾을 수 없습니다.');
        }
    };

    // 의뢰 복사 함수
    window.copyOrder = function(orderNo) {
        if (!confirm('이 의뢰를 복사하시겠습니까?')) {
            return;
        }

        const apiUrl = window.ApiConfig
            ? window.ApiConfig.endpoints.orders.copy(orderNo)
            : `/order/api/orders/${orderNo}/copy/`;

        apiCall(apiUrl, 'POST')
            .then(data => {
                if (window.Toast) {
                    window.Toast.success(`의뢰가 복사되었습니다! 새 의뢰번호: #${data.no}`);
                } else {
                    alert(`의뢰가 복사되었습니다! 새 의뢰번호: #${data.no}`);
                }
                setTimeout(() => location.reload(), 1500);
            })
            .catch(error => {
                console.error('Error:', error);
                if (window.Toast) {
                    window.Toast.error('의뢰 복사에 실패했습니다.');
                } else {
                    alert('의뢰 복사에 실패했습니다.');
                }
            });
    };

    // 견적서 보기 함수
    window.showEstimates = function(orderNo) {
        if (window.Toast) {
            window.Toast.info(`의뢰 #${orderNo}의 견적서 관리 기능은 다음 단계에서 구현됩니다.`);
        } else {
            alert(`의뢰 #${orderNo}의 견적서 관리 기능은 다음 단계에서 구현됩니다.`);
        }
    };

    // 메모 보기 함수
    window.showMemos = function(orderNo) {
        if (typeof window.addMemo === 'function') {
            window.addMemo(orderNo);
        } else {
            if (window.Toast) {
                window.Toast.info(`의뢰 #${orderNo}의 메모 관리 기능은 다음 단계에서 구현됩니다.`);
            } else {
                alert(`의뢰 #${orderNo}의 메모 관리 기능은 다음 단계에서 구현됩니다.`);
            }
        }
    };

    // 상태별 CSS 클래스 반환
    window.getStatusClass = function(status) {
        const statusMap = {
            '대기중': 'waiting',
            '할당': 'assigned',
            '반려': 'rejected',
            '취소': 'cancelled',
            '제외': 'cancelled',
            '계약': 'completed'
        };
        return statusMap[status] || 'waiting';
    };

    // DOM 로드 후 초기화
    document.addEventListener('DOMContentLoaded', function() {
        // 행 체크박스 이벤트
        const rowCheckboxes = document.querySelectorAll('.row-checkbox');
        rowCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const row = this.closest('tr');
                if (row) {
                    row.classList.toggle('selected', this.checked);
                }

                // 전체 선택 체크박스 상태 업데이트
                const selectAllCheckbox = document.getElementById('selectAll');
                if (selectAllCheckbox) {
                    const allChecked = Array.from(rowCheckboxes).every(cb => cb.checked);
                    selectAllCheckbox.checked = allChecked;
                }
            });
        });

        console.log('의뢰 리스트 페이지 초기화 완료');
    });

})();
