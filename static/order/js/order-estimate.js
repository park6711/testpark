/**
 * 견적서 관리 모달
 * order-assign.js와 동일한 패턴으로 구현
 */

(function() {
    'use strict';

    const { getCookie, apiCall, formatDate } = window.OrderUtils;

    // 상태 관리
    let currentEstimateOrderNo = null;
    let currentEstimateOrderData = null;
    let allEstimates = [];

    /**
     * 견적서 관리 모달 열기
     * @param {number} orderNo - 의뢰 번호
     */
    window.showEstimates = function(orderNo) {
        currentEstimateOrderNo = orderNo;

        // API URL 가져오기
        const orderApiUrl = window.ApiConfig
            ? window.ApiConfig.endpoints.orders.detail(orderNo)
            : `/order/api/orders/${orderNo}/`;

        // 의뢰 정보 가져오기
        apiCall(orderApiUrl)
            .then(data => {
                currentEstimateOrderData = data;
                displayEstimateOrderInfo(data);
                loadEstimates(orderNo);

                // 모달 표시
                const modal = document.getElementById('estimateModal');
                if (modal) {
                    modal.classList.add('active');
                }
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

    /**
     * 견적서 관리 모달 닫기
     */
    window.closeEstimateModal = function() {
        const modal = document.getElementById('estimateModal');
        if (modal) {
            modal.classList.remove('active');
        }

        currentEstimateOrderNo = null;
        currentEstimateOrderData = null;
        allEstimates = [];

        // 입력 필드 초기화
        const postInput = document.getElementById('estimatePost');
        if (postInput) postInput.value = '';
    };

    /**
     * 의뢰 정보 표시
     * @param {Object} data - 의뢰 데이터
     */
    function displayEstimateOrderInfo(data) {
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
                <span class="info-label">공사예정일:</span>
                <span class="info-value">${data.dateSchedule || '미정'}</span>
            </div>
            ${data.assigned_company ? `
            <div class="info-item">
                <span class="info-label">할당업체:</span>
                <span class="info-value" style="color: #3b82f6; font-weight: 600;">${data.assigned_company}</span>
            </div>
            ` : ''}
        `;

        const container = document.getElementById('estimateOrderInfo');
        if (container) {
            container.innerHTML = infoHtml;
        }
    }

    /**
     * 견적서 목록 로드
     * @param {number} orderNo - 의뢰 번호
     */
    function loadEstimates(orderNo) {
        const apiUrl = window.ApiConfig
            ? window.ApiConfig.endpoints.estimates.byOrder(orderNo)
            : `/order/api/estimates/?noOrder=${orderNo}`;

        apiCall(apiUrl)
            .then(data => {
                allEstimates = data.results || data;
                renderEstimateList();
            })
            .catch(error => {
                console.error('Error loading estimates:', error);
                if (window.Toast) {
                    window.Toast.error('견적서 목록을 불러오는데 실패했습니다.');
                }

                const listContainer = document.getElementById('estimateList');
                if (listContainer) {
                    listContainer.innerHTML = `
                        <div style="text-align: center; padding: 2rem; color: #dc3545;">
                            견적서 목록을 불러오는데 실패했습니다.
                        </div>
                    `;
                }
            });
    }

    /**
     * 견적서 목록 렌더링
     */
    function renderEstimateList() {
        const listContainer = document.getElementById('estimateList');
        if (!listContainer) return;

        // 견적서 개수 업데이트
        const countSpan = document.getElementById('estimateCount');
        if (countSpan) {
            countSpan.textContent = `(${allEstimates.length}개)`;
        }

        if (allEstimates.length === 0) {
            listContainer.innerHTML = `
                <div class="empty-state-text">
                    <div class="icon">💰</div>
                    <p>등록된 견적서가 없습니다.</p>
                    <p style="font-size: 0.875rem; color: #6b7280; margin-top: 0.5rem;">
                        위의 양식을 사용하여 첫 견적서를 등록해보세요.
                    </p>
                </div>
            `;
            return;
        }

        // 최신순으로 정렬
        const sortedEstimates = [...allEstimates].sort((a, b) => {
            return new Date(b.time || b.created_at) - new Date(a.time || a.created_at);
        });

        listContainer.innerHTML = sortedEstimates.map(estimate => {
            const estimateDate = estimate.time || estimate.created_at;
            const formattedDate = estimateDate ? formatDate(estimateDate) : '-';
            const isRecent = estimate.is_recent;

            return `
                <div class="estimate-card">
                    <div class="estimate-header">
                        <div class="estimate-info">
                            <strong>견적서 #${estimate.no}</strong>
                            ${isRecent ? '<span class="info-badge success" style="margin-left: 0.5rem;">최근</span>' : ''}
                        </div>
                        <div class="estimate-actions">
                            <button class="btn-small btn-danger" onclick="deleteEstimate(${estimate.no})" title="삭제">
                                🗑️ 삭제
                            </button>
                        </div>
                    </div>
                    <div class="estimate-body">
                        <div class="estimate-meta">
                            <div><strong>등록일:</strong> ${formattedDate}</div>
                            ${estimate.company_name ? `<div><strong>업체:</strong> ${estimate.company_name}</div>` : ''}
                        </div>
                        ${estimate.sPost ? `
                            <div class="estimate-link">
                                <strong>견적서 링크:</strong>
                                <a href="${estimate.sPost}" target="_blank" rel="noopener noreferrer" style="color: #10b981; text-decoration: underline;">
                                    ${estimate.sPost}
                                </a>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }).join('');
    }

    /**
     * 견적서 추가
     */
    window.addEstimate = function() {
        const postInput = document.getElementById('estimatePost');
        if (!postInput) return;

        const sPost = postInput.value.trim();

        // 유효성 검사
        if (!sPost) {
            if (window.Toast) {
                window.Toast.warning('견적서 게시글 링크를 입력해주세요.');
            } else {
                alert('견적서 게시글 링크를 입력해주세요.');
            }
            postInput.focus();
            return;
        }

        // URL 형식 검사 (선택적)
        if (!isValidUrl(sPost)) {
            if (window.Toast) {
                window.Toast.warning('올바른 URL 형식을 입력해주세요.');
            } else {
                alert('올바른 URL 형식을 입력해주세요.');
            }
            postInput.focus();
            return;
        }

        // API 호출
        const apiUrl = window.ApiConfig
            ? window.ApiConfig.endpoints.estimates.create
            : '/order/api/estimates/';

        const estimateData = {
            noOrder: currentEstimateOrderNo,
            noAssign: 0, // TODO(human): 현재 할당 정보가 없으면 0으로 설정. 할당 선택 기능을 추가할 수 있습니다.
            sPost: sPost
        };

        apiCall(apiUrl, 'POST', estimateData)
            .then(data => {
                if (window.Toast) {
                    window.Toast.success('견적서가 등록되었습니다.');
                }

                // 입력 필드 초기화
                postInput.value = '';

                // 목록 새로고침
                loadEstimates(currentEstimateOrderNo);
            })
            .catch(error => {
                console.error('Error:', error);
                if (window.Toast) {
                    window.Toast.error('견적서 등록에 실패했습니다: ' + error.message);
                } else {
                    alert('견적서 등록에 실패했습니다: ' + error.message);
                }
            });
    };

    /**
     * 견적서 삭제
     * @param {number} estimateNo - 견적서 번호
     */
    window.deleteEstimate = function(estimateNo) {
        if (!confirm('이 견적서를 삭제하시겠습니까?')) {
            return;
        }

        const apiUrl = window.ApiConfig
            ? window.ApiConfig.endpoints.estimates.delete(estimateNo)
            : `/order/api/estimates/${estimateNo}/`;

        apiCall(apiUrl, 'DELETE')
            .then(() => {
                if (window.Toast) {
                    window.Toast.success('견적서가 삭제되었습니다.');
                }

                // 목록 새로고침
                loadEstimates(currentEstimateOrderNo);
            })
            .catch(error => {
                console.error('Error:', error);
                if (window.Toast) {
                    window.Toast.error('견적서 삭제에 실패했습니다.');
                } else {
                    alert('견적서 삭제에 실패했습니다.');
                }
            });
    };

    /**
     * URL 유효성 검사
     * @param {string} url - 검사할 URL
     * @returns {boolean} 유효 여부
     */
    function isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch (e) {
            return false;
        }
    }

    /**
     * 이벤트 리스너 등록 (DOM 로드 후)
     */
    document.addEventListener('DOMContentLoaded', function() {
        // 모달 닫기 버튼
        const closeBtn = document.getElementById('estimateModalCloseBtn');
        if (closeBtn) {
            closeBtn.addEventListener('click', closeEstimateModal);
        }

        // 모달 외부 클릭
        const modal = document.getElementById('estimateModal');
        if (modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === this) {
                    closeEstimateModal();
                }
            });
        }

        // 견적서 추가 버튼
        const addBtn = document.getElementById('addEstimateBtn');
        if (addBtn) {
            addBtn.addEventListener('click', addEstimate);
        }

        // Enter 키 이벤트
        const postInput = document.getElementById('estimatePost');
        if (postInput) {
            postInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    addEstimate();
                }
            });
        }

        console.log('견적서 관리 모듈 초기화 완료');
    });

    // TestPark 전역 네임스페이스에 등록
    if (window.TestPark && window.TestPark.apps.order) {
        window.TestPark.apps.order.actions.showEstimates = showEstimates;
        window.TestPark.apps.order.actions.closeEstimateModal = closeEstimateModal;
        window.TestPark.apps.order.actions.addEstimate = addEstimate;
        window.TestPark.apps.order.actions.deleteEstimate = deleteEstimate;
    }

})();
