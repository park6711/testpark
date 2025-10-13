/**
 * 메모 작성 모달
 */
(function() {
    'use strict';

    const { getCookie, apiCall, formatDate } = window.OrderUtils;

    let currentMemoOrderNo = null;
    let currentMemoAssignNo = null;
    let currentMemoOrderData = null;
    let currentScope = 'assign'; // 'assign' 또는 'order'
    let allMemos = [];

    // 메모 모달 열기
    window.addMemo = function(orderNo, assignNo) {
        currentMemoOrderNo = orderNo;
        currentMemoAssignNo = assignNo;

        const apiUrl = window.ApiConfig
            ? window.ApiConfig.endpoints.orders.detail(orderNo)
            : `/order/api/orders/${orderNo}/`;

        apiCall(apiUrl)
            .then(data => {
                currentMemoOrderData = data;
                displayMemoOrderInfo(data);
                loadMemos(assignNo);

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
        currentMemoAssignNo = null;
        currentMemoOrderData = null;
        currentScope = 'assign';
        allMemos = [];
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
    
    /**
     * 메모 목록 로드
     * @param {number} assignNo - 할당 번호
     * @param {string} scope - 'assign' 또는 'order'
     */
    function loadMemos(assignNo, scope = 'assign') {
        currentScope = scope;

        const apiUrl = window.ApiConfig
            ? `${window.ApiConfig.endpoints.assignMemos.byAssign(assignNo)}&scope=${scope}`
            : `/order/api/assign-memos/?assign_id=${assignNo}&scope=${scope}`;

        // 토글 버튼 상태 업데이트
        updateScopeToggle(scope);

        apiCall(apiUrl)
            .then(data => {
                allMemos = data.results || data;
                renderMemoList();
            })
            .catch(error => {
                console.error('Error loading memos:', error);
                if (window.Toast) {
                    window.Toast.error('메모 목록을 불러오는데 실패했습니다.');
                }

                const listContainer = document.getElementById('memoList');
                if (listContainer) {
                    listContainer.innerHTML = `
                        <div style="text-align: center; padding: 2rem; color: #dc3545;">
                            메모 목록을 불러오는데 실패했습니다.
                        </div>
                    `;
                }
            });
    }

    /**
     * 스코프 토글 버튼 상태 업데이트
     * @param {string} scope - 'assign' 또는 'order'
     */
    function updateScopeToggle(scope) {
        const assignBtn = document.getElementById('scopeMemoAssignBtn');
        const orderBtn = document.getElementById('scopeMemoOrderBtn');

        if (assignBtn && orderBtn) {
            if (scope === 'assign') {
                assignBtn.classList.add('active');
                orderBtn.classList.remove('active');
            } else {
                assignBtn.classList.remove('active');
                orderBtn.classList.add('active');
            }
        }
    }

    /**
     * 스코프 변경
     * @param {string} newScope - 'assign' 또는 'order'
     */
    window.changeScopeMemo = function(newScope) {
        if (currentScope === newScope) return;
        loadMemos(currentMemoAssignNo, newScope);
    };

    /**
     * 메모 목록 렌더링
     */
    function renderMemoList() {
        const listContainer = document.getElementById('memoList');
        const countSpan = document.getElementById('memoCount');

        if (!listContainer) return;

        // 메모 개수 업데이트
        if (countSpan) {
            const scopeLabel = currentScope === 'assign' ? '현재 할당' : '전체 의뢰';
            countSpan.textContent = `(${allMemos.length}개 - ${scopeLabel})`;
        }

        if (allMemos.length === 0) {
            listContainer.innerHTML = `
                <div class="empty-state-text">
                    <div class="icon">📝</div>
                    <p>등록된 메모가 없습니다.</p>
                    <p style="font-size: 0.875rem; color: #6b7280; margin-top: 0.5rem;">
                        위의 양식을 사용하여 첫 메모를 등록해보세요.
                    </p>
                </div>
            `;
            return;
        }

        // 최신순으로 정렬
        const sortedMemos = [...allMemos].sort((a, b) => {
            return new Date(b.time || b.created_at) - new Date(a.time || a.created_at);
        });

        listContainer.innerHTML = sortedMemos.map(memo => {
            const memoDate = memo.time || memo.created_at;
            const formattedDate = memoDate ? formatDate(memoDate) : '-';
            const isCurrentAssign = memo.noAssign === currentMemoAssignNo;

            return `
                <div class="memo-card ${!isCurrentAssign && currentScope === 'order' ? 'other-assign' : ''}">
                    <div class="memo-header">
                        <div class="memo-info">
                            <strong>${memo.sWorker || '작성자 미상'}</strong>
                            ${!isCurrentAssign && currentScope === 'order' ? '<span class="info-badge info" style="margin-left: 0.5rem;">다른 할당</span>' : ''}
                            ${isCurrentAssign && currentScope === 'order' ? '<span class="info-badge primary" style="margin-left: 0.5rem;">현재 할당</span>' : ''}
                        </div>
                        <div class="memo-date">${formattedDate}</div>
                    </div>
                    <div class="memo-body">
                        ${currentScope === 'order' ? `<div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.5rem;"><strong>할당ID:</strong> #${memo.noAssign}</div>` : ''}
                        <div class="memo-content">${memo.sMemo || ''}</div>
                    </div>
                </div>
            `;
        }).join('');
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
                ? window.ApiConfig.endpoints.assignMemos.create
                : `/order/api/assign-memos/`;

            apiCall(apiUrl, 'POST', {
                noOrder: currentMemoOrderNo,
                noAssign: currentMemoAssignNo,
                sMemo: content,
                sWorker: author
            })
            .then(data => {
                if (window.Toast) {
                    window.Toast.success('메모가 저장되었습니다.');
                }

                // 입력 필드 초기화
                document.getElementById('memoContent').value = '';

                // 목록 새로고침 (할당ID 기준)
                loadMemos(currentMemoAssignNo, currentScope);
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
