/**
 * 메모 작성 모달
 */
(function() {
    'use strict';
    
    const { getCookie, apiCall } = window.OrderUtils;
    
    let currentMemoOrderNo = null;
    let currentMemoOrderData = null;
    
    // 메모 모달 열기
    window.addMemo = function(orderNo) {
        currentMemoOrderNo = orderNo;

        const apiUrl = window.ApiConfig
            ? window.ApiConfig.endpoints.orders.detail(orderNo)
            : `/order/api/orders/${orderNo}/`;

        apiCall(apiUrl)
            .then(data => {
                currentMemoOrderData = data;
                displayMemoOrderInfo(data);
                loadExistingMemos();

                document.getElementById('memoContent').value = '';
                document.getElementById('memoModal').classList.add('active');
            })
            .catch(error => {
                console.error('Error:', error);
                if (window.Toast) {
                    window.Toast.error('의뢰 정보를 불러오는데 실패했습니다.');
                } else {
                    alert('의뢰 정보를 불러오는데 실패했습니다.');
                }
            });
    };
    
    // 메모 모달 닫기
    window.closeMemoModal = function() {
        document.getElementById('memoModal').classList.remove('active');
        currentMemoOrderNo = null;
        currentMemoOrderData = null;
    };
    
    function displayMemoOrderInfo(data) {
        const infoHtml = `
            <div class="info-item">
                <span class="info-label">의뢰번호:</span>
                <span class="info-value">#${data.no}</span>
            </div>
            <div class="info-item">
                <span class="info-label">고객명:</span>
                <span class="info-value">${data.sName || '-'}</span>
            </div>
            <div class="info-item">
                <span class="info-label">공사지역:</span>
                <span class="info-value">${data.sArea || '-'}</span>
            </div>
            <div class="info-item">
                <span class="info-label">상태:</span>
                <span class="info-value">${data.recent_status || '대기중'}</span>
            </div>
        `;
        document.getElementById('memoOrderInfo').innerHTML = infoHtml;
    }
    
    function loadExistingMemos() {
        const memoListDiv = document.getElementById('memoList');
        const memoCountSpan = document.getElementById('memoCount');
        
        if (currentMemoOrderData && currentMemoOrderData.memos) {
            const memos = currentMemoOrderData.memos;
            memoCountSpan.textContent = `(${memos.length}개)`;
            
            if (memos.length === 0) {
                memoListDiv.innerHTML = '<div style="text-align: center; padding: 2rem; color: #9ca3af;">등록된 메모가 없습니다.</div>';
            } else {
                memoListDiv.innerHTML = memos.map(memo => `
                    <div style="padding: 12px; border: 1px solid #e5e7eb; border-radius: 0.5rem; margin-bottom: 8px; background: #f9fafb;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                            <span style="font-weight: 600; color: #374151;">${memo.author || '작성자 미상'}</span>
                            <span style="font-size: 0.875rem; color: #6b7280;">${memo.datetime || ''}</span>
                        </div>
                        <div style="color: #4b5563; white-space: pre-wrap;">${memo.content || ''}</div>
                    </div>
                `).join('');
            }
        }
    }
    
    // 메모 저장 버튼 이벤트
    document.addEventListener('DOMContentLoaded', function() {
        document.getElementById('saveMemoBtn').addEventListener('click', function() {
            const content = document.getElementById('memoContent').value.trim();
            const author = document.getElementById('memoAuthor').value.trim() || '관리자';

            if (!content) {
                if (window.Toast) {
                    window.Toast.warning('메모 내용을 입력해주세요.');
                } else {
                    alert('메모 내용을 입력해주세요.');
                }
                return;
            }

            const apiUrl = window.ApiConfig
                ? window.ApiConfig.endpoints.orders.addMemo(currentMemoOrderNo)
                : `/order/api/orders/${currentMemoOrderNo}/add_memo/`;

            apiCall(apiUrl, 'POST', {
                content: content,
                author: author
            })
            .then(data => {
                if (data.status === 'success') {
                    if (window.Toast) {
                        window.Toast.success('메모가 저장되었습니다.');
                    } else {
                        alert('메모가 저장되었습니다.');
                    }
                    closeMemoModal();
                    setTimeout(() => location.reload(), 1000);
                } else {
                    if (window.Toast) {
                        window.Toast.error('메모 저장 실패: ' + (data.message || '알 수 없는 오류'));
                    } else {
                        alert('메모 저장 실패: ' + (data.message || '알 수 없는 오류'));
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (window.Toast) {
                    window.Toast.error('메모 저장 중 오류가 발생했습니다.');
                } else {
                    alert('메모 저장 중 오류가 발생했습니다.');
                }
            });
        });
        
        document.getElementById('memoModalCloseBtn').addEventListener('click', closeMemoModal);
        document.getElementById('memoModal').addEventListener('click', function(e) {
            if (e.target === this) closeMemoModal();
        });
    });
})();
