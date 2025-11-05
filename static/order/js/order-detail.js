/**
 * 의뢰 상세보기 모달
 * 의뢰 정보, 할당 내역, 견적서, 메모를 탭으로 표시
 */

(function() {
    'use strict';

    const { formatDate, formatPhone, getStatusBadgeHtml, apiCall } = window.OrderUtils;

    // 상세보기 모달 열기
    window.viewOrder = function(orderNo) {
        const modal = document.getElementById('orderModal');
        const modalContent = document.getElementById('modalContent');

        // 모달 표시
        modal.classList.add('active');

        // 로딩 표시
        modalContent.innerHTML = '<div class="loading-spinner"></div>';

        // API 호출하여 상세 정보 가져오기
        const apiUrl = window.ApiConfig
            ? window.ApiConfig.endpoints.orders.detail(orderNo)
            : `/order/api/orders/${orderNo}/`;

        apiCall(apiUrl)
            .then(data => {
                modalContent.innerHTML = generateOrderDetailHTML(data);
            })
            .catch(error => {
                console.error('Error:', error);

                // Toast 알림 사용
                if (window.Toast) {
                    window.Toast.error('데이터를 불러오는데 실패했습니다: ' + error.message);
                }

                modalContent.innerHTML = `
                    <div style="text-align: center; padding: 40px; color: #dc3545;">
                        <h3>❌ 데이터를 불러오는데 실패했습니다</h3>
                        <p>${error.message}</p>
                    </div>
                `;
            });
    };

    // 모달 닫기
    window.closeModal = function() {
        const modal = document.getElementById('orderModal');
        modal.classList.remove('active');
    };

    // 탭 전환
    window.switchTab = function(event, tabId) {
        // 모든 탭 버튼에서 active 제거
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });

        // 모든 탭 컨텐츠에서 active 제거
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });

        // 클릭된 탭 버튼에 active 추가
        event.target.classList.add('active');

        // 해당 탭 컨텐츠에 active 추가
        document.getElementById(tabId).classList.add('active');
    };

    // 상세 정보 HTML 생성
    function generateOrderDetailHTML(data) {
        const formatDateTime = (dateTimeStr) => {
            if (!dateTimeStr) return '-';
            const date = new Date(dateTimeStr);
            return date.toLocaleString('ko-KR');
        };

        const getStatusBadge = (status) => {
            const statusMap = {
                '대기중': 'warning',
                '할당': 'success',
                '반려': 'danger',
                '취소': 'danger',
                '제외': 'danger',
                '계약': 'success',
                '업체미비': 'info',
                '중복접수': 'warning',
                '가능문의': 'info',
                '불가능답변': 'danger'
            };
            const badgeClass = statusMap[status] || 'info';
            return `<span class="info-badge ${badgeClass}">${status}</span>`;
        };

        // 할당 목록 HTML
        const generateAssignsHTML = () => {
            if (!data.assigns || data.assigns.length === 0) {
                return `
                    <div class="empty-state-text">
                        <div class="icon">📋</div>
                        <p>할당 내역이 없습니다</p>
                    </div>
                `;
            }

            return data.assigns.map(assign => `
                <div class="assign-card">
                    <div class="assign-header">
                        <div class="assign-company">${assign.company_name || '업체 정보 없음'}</div>
                        ${getStatusBadge(assign.assign_type_display)}
                    </div>
                    <div class="assign-meta">
                        <div><strong>공사 종류:</strong> ${assign.construction_type_display || '-'}</div>
                        <div><strong>할당일:</strong> ${formatDateTime(assign.time)}</div>
                        ${assign.sWorker ? `<div><strong>담당자:</strong> ${assign.sWorker}</div>` : ''}
                        ${assign.area_name ? `<div><strong>지역:</strong> ${assign.area_name}</div>` : ''}
                    </div>
                </div>
            `).join('');
        };

        // 견적 목록 HTML
        const generateEstimatesHTML = () => {
            if (!data.estimates || data.estimates.length === 0) {
                return `
                    <div class="empty-state-text">
                        <div class="icon">💰</div>
                        <p>견적서가 없습니다</p>
                    </div>
                `;
            }

            return data.estimates.map(estimate => `
                <div class="assign-card">
                    <div class="assign-header">
                        <div class="assign-company">${estimate.company_name || '업체 정보 없음'}</div>
                        ${estimate.is_recent ? '<span class="info-badge success">최근</span>' : ''}
                    </div>
                    <div class="assign-meta">
                        <div><strong>등록일:</strong> ${formatDateTime(estimate.time)}</div>
                        ${estimate.sPost ? `
                            <div>
                                <strong>견적서:</strong>
                                <a href="${estimate.sPost}" target="_blank" style="color: #10b981;">보기 🔗</a>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `).join('');
        };

        // 메모 목록 HTML
        const generateMemosHTML = () => {
            if (!data.memos || data.memos.length === 0) {
                return `
                    <div class="empty-state-text">
                        <div class="icon">📝</div>
                        <p>메모가 없습니다</p>
                    </div>
                `;
            }

            return data.memos.map(memo => `
                <div class="assign-card">
                    <div class="assign-header">
                        <div class="assign-company">${memo.sWorker || '작성자 없음'}</div>
                        <div style="font-size: 0.875rem; color: #6b7280;">
                            ${formatDateTime(memo.time)}
                        </div>
                    </div>
                    <div style="margin-top: 0.75rem; line-height: 1.6; color: #374151;">
                        ${memo.sMemo || '-'}
                    </div>
                    ${memo.is_important ? '<div style="margin-top: 0.5rem;"><span class="info-badge danger">⚠️ 중요</span></div>' : ''}
                </div>
            `).join('');
        };

        return `
            <!-- 상태 정보 -->
            <div class="detail-section">
                <div class="badge-group">
                    ${getStatusBadge(data.recent_status)}
                    ${data.designation_type ? `<span class="info-badge info">${data.designation_type}</span>` : ''}
                    ${data.privacy_status ? `<span class="info-badge ${data.privacy_status === '전체 동의' ? 'success' : 'danger'}">${data.privacy_status}</span>` : ''}
                    ${data.is_urgent ? '<span class="info-badge danger">⚠️ 긴급</span>' : ''}
                </div>
            </div>

            <!-- 기본 정보 -->
            <div class="detail-section">
                <h3>📋 기본 정보</h3>
                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="detail-label">의뢰 번호</span>
                        <span class="detail-value">#${data.no}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">고객명</span>
                        <span class="detail-value">${data.sName || '-'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">연락처</span>
                        <span class="detail-value">${formatPhone(data.sPhone)}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">공사 예정일</span>
                        <span class="detail-value">${formatDate(data.dateSchedule)}</span>
                    </div>
                </div>
            </div>

            <!-- 공사 정보 -->
            <div class="detail-section">
                <h3>🏗️ 공사 정보</h3>
                <div class="detail-item" style="margin-bottom: 1rem;">
                    <span class="detail-label">공사 지역</span>
                    <span class="detail-value">${data.sArea || '-'}</span>
                </div>
                ${data.sConstruction ? `
                    <div class="detail-item">
                        <span class="detail-label">공사 내용</span>
                        <div class="construction-text" style="margin-top: 0.5rem;">${data.sConstruction}</div>
                    </div>
                ` : ''}
                ${data.post_link ? `
                    <div class="detail-item" style="margin-top: 1rem;">
                        <a href="${data.post_link}" target="_blank" class="btn-action-primary">
                            카페 게시글 보기 🔗
                        </a>
                    </div>
                ` : ''}
            </div>

            <!-- 탭 메뉴 -->
            <div class="tabs-container">
                <div class="tabs">
                    <button class="tab-button active" onclick="switchTab(event, 'tab-assigns')">
                        할당 내역 (${data.assigns ? data.assigns.length : 0})
                    </button>
                    <button class="tab-button" onclick="switchTab(event, 'tab-estimates')">
                        견적서 (${data.estimates ? data.estimates.length : 0})
                    </button>
                    <button class="tab-button" onclick="switchTab(event, 'tab-memos')">
                        메모 (${data.memos ? data.memos.length : 0})
                    </button>
                </div>
            </div>

            <!-- 탭 컨텐츠 -->
            <div id="tab-assigns" class="tab-content active">
                ${generateAssignsHTML()}
            </div>

            <div id="tab-estimates" class="tab-content">
                ${generateEstimatesHTML()}
            </div>

            <div id="tab-memos" class="tab-content">
                ${generateMemosHTML()}
            </div>

            <!-- 액션 버튼 -->
            <div class="action-buttons-group">
                <button class="btn-action btn-action-primary" onclick="assignToCompany(${data.no})">
                    🏢 업체 할당
                </button>
                <button class="btn-action btn-action-primary" onclick="addMemo(${data.no})">
                    📝 메모 작성
                </button>
                <button class="btn-action btn-action-secondary" onclick="editOrder(${data.no})">
                    ✏️ 수정
                </button>
            </div>
        `;
    }

})();
