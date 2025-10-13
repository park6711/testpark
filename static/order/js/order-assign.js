/**
 * 업체 할당 모달
 * 11.tsx 로직과 동일하게 구현
 */

(function() {
    'use strict';

    const { getCookie, apiCall } = window.OrderUtils;

    // 상태 관리
    let currentAssignOrderNo = null;
    let currentAssignOrderData = null;
    let selectedCompanyIds = [];
    let allCompanies = [];
    let allGroupPurchases = [];

    // 업체 할당 모달 열기
    window.assignToCompany = function(orderNo) {
        currentAssignOrderNo = orderNo;
        selectedCompanyIds = [];

        // API URL 가져오기
        const apiUrl = window.ApiConfig
            ? window.ApiConfig.endpoints.orders.detail(orderNo)
            : `/order/api/orders/${orderNo}/`;

        // 의뢰 정보 가져오기
        apiCall(apiUrl)
            .then(data => {
                currentAssignOrderData = data;
                displayAssignOrderInfo(data);
                loadCompanies();
                loadGroupPurchases();

                document.getElementById('assignModal').classList.add('active');
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

    // 업체 할당 모달 닫기
    window.closeAssignModal = function() {
        document.getElementById('assignModal').classList.remove('active');
        currentAssignOrderNo = null;
        currentAssignOrderData = null;
        selectedCompanyIds = [];

        // 라디오 버튼 초기화
        const defaultRadio = document.querySelector('input[name="designationType"][value="지정없음"]');
        if (defaultRadio) defaultRadio.checked = true;

        const gpSelect = document.getElementById('gpSelect');
        if (gpSelect) gpSelect.style.display = 'none';

        const gpSection = document.getElementById('gpInfoSection');
        if (gpSection) gpSection.style.display = 'none';
    };

    // 업체 선택 토글
    window.toggleCompanySelection = function(companyNo) {
        const index = selectedCompanyIds.indexOf(companyNo);
        if (index > -1) {
            selectedCompanyIds.splice(index, 1);
        } else {
            selectedCompanyIds.push(companyNo);
        }

        updateSelectedCount();
        renderCompanyTable();
    };

    // 의뢰 정보 표시
    function displayAssignOrderInfo(data) {
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
                <span class="info-label">기할당업체:</span>
                <span class="info-value" style="color: #3b82f6; font-weight: 600;">${data.assigned_company}</span>
            </div>
            ` : ''}
        `;

        document.getElementById('assignOrderInfo').innerHTML = infoHtml;
    }

    // 업체 목록 로드
    function loadCompanies() {
        const apiUrl = window.ApiConfig
            ? window.ApiConfig.endpoints.companies.list
            : '/order/api/companies/';

        apiCall(apiUrl)
            .then(data => {
                allCompanies = data.results || data;
                renderCompanyTable();
            })
            .catch(error => {
                console.error('Error loading companies:', error);
                if (window.Toast) {
                    window.Toast.error('업체 목록을 불러오는데 실패했습니다.');
                }
                const tbody = document.getElementById('companyTableBody');
                if (tbody) {
                    tbody.innerHTML = `
                        <tr><td colspan="7" style="text-align: center; padding: 2rem; color: #dc3545;">
                            업체 목록을 불러오는데 실패했습니다.
                        </td></tr>
                    `;
                }
            });
    }

    // 공동구매 목록 로드
    function loadGroupPurchases() {
        const apiUrl = window.ApiConfig
            ? window.ApiConfig.endpoints.groupPurchases.list
            : '/order/api/group-purchases/';

        apiCall(apiUrl)
            .then(data => {
                allGroupPurchases = data.results || data;
                const gpSelect = document.getElementById('gpSelect');
                if (gpSelect) {
                    gpSelect.innerHTML = '<option value="">공동구매 선택</option>';
                    allGroupPurchases.forEach(gp => {
                        gpSelect.innerHTML += `<option value="${gp.no}">${gp.round} - ${gp.name}</option>`;
                    });
                }
            })
            .catch(error => {
                console.error('Error loading group purchases:', error);
                if (window.Toast) {
                    window.Toast.error('공동구매 목록을 불러오는데 실패했습니다.');
                }
            });
    }

    // 업체 테이블 렌더링
    function renderCompanyTable() {
        const searchInput = document.getElementById('companySearch');
        const regionSelect = document.getElementById('regionFilter');
        const typeSelect = document.getElementById('constructionTypeFilter');

        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        const regionFilter = regionSelect ? regionSelect.value : '';
        const typeFilter = typeSelect ? typeSelect.value : '';

        let filteredCompanies = allCompanies.filter(company => {
            const matchSearch = !searchTerm || company.sCompanyName.toLowerCase().includes(searchTerm);
            const matchRegion = !regionFilter || (company.sArea && company.sArea.includes(regionFilter));
            const matchType = !typeFilter || (company.sArea && company.sArea.includes(typeFilter));
            return matchSearch && matchRegion && matchType;
        });

        // 등급순으로 정렬
        filteredCompanies.sort((a, b) => (a.grade || 999) - (b.grade || 999));

        const tbody = document.getElementById('companyTableBody');
        if (!tbody) return;

        if (filteredCompanies.length === 0) {
            tbody.innerHTML = `
                <tr><td colspan="7" style="text-align: center; padding: 2rem; color: #6b7280;">
                    검색 조건에 맞는 업체가 없습니다.
                </td></tr>
            `;
            return;
        }

        tbody.innerHTML = filteredCompanies.map(company => {
            const isSelected = selectedCompanyIds.includes(company.no);
            const isAssigned = currentAssignOrderData && currentAssignOrderData.assigned_company === company.sCompanyName;

            return `
                <tr class="${isSelected ? 'selected' : ''} ${isAssigned ? 'already-assigned' : ''}">
                    <td style="text-align: center;">
                        <input type="checkbox"
                            ${isAssigned ? 'disabled' : ''}
                            ${isSelected ? 'checked' : ''}
                            onchange="toggleCompanySelection(${company.no})"
                        >
                    </td>
                    <td style="font-weight: 500;">
                        ${company.sCompanyName}
                        ${isAssigned ? '<span class="tag tag-assigned">기할당</span>' : ''}
                    </td>
                    <td style="text-align: center;">
                        <span class="grade-badge grade-${company.grade || 4}">
                            ${company.grade || '-'}등급
                        </span>
                    </td>
                    <td style="text-align: center;">${company.assignCount || 0}</td>
                    <td style="text-align: center;">${company.license || '-'}</td>
                    <td>${company.sArea || '-'}</td>
                    <td style="font-size: 0.7rem;">${company.specialty || '-'}</td>
                </tr>
            `;
        }).join('');
    }

    // 선택된 업체 수 업데이트
    function updateSelectedCount() {
        const countSpan = document.getElementById('selectedCount');
        const assignBtn = document.getElementById('assignBtn');

        if (countSpan) countSpan.textContent = selectedCompanyIds.length;
        if (assignBtn) assignBtn.disabled = selectedCompanyIds.length === 0;
    }

    // 공동구매 정보 표시
    function displayGroupPurchaseInfo(gp) {
        const orderArea = currentAssignOrderData.sArea || '';
        const orderDate = currentAssignOrderData.dateSchedule || '';

        const areaAvailable = gp.available_areas && gp.available_areas.some(area => orderArea.includes(area));
        const dateAvailable = !gp.unavailable_dates || !gp.unavailable_dates.includes(orderDate);

        const tableHtml = `
            <thead>
                <tr>
                    <th>회차</th>
                    <th>공사가능지역</th>
                    <th>공사불가능일정</th>
                    <th>업체명</th>
                    <th>공동구매이름</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>${gp.round}</td>
                    <td class="${areaAvailable ? 'available' : 'unavailable'}">
                        <div style="font-weight: 600; margin-bottom: 0.25rem;">
                            ${(gp.available_areas || []).join(', ')}
                        </div>
                        <div style="font-size: 0.75rem;">
                            고객: ${orderArea} → ${areaAvailable ? '✅ 가능' : '❌ 불가능'}
                        </div>
                    </td>
                    <td class="${dateAvailable ? 'available' : 'unavailable'}">
                        <div style="font-weight: 600; margin-bottom: 0.25rem;">
                            ${(gp.unavailable_dates || []).slice(0, 3).join(', ')}
                            ${(gp.unavailable_dates || []).length > 3 ? '...' : ''}
                        </div>
                        <div style="font-size: 0.75rem;">
                            고객: ${orderDate} → ${dateAvailable ? '✅ 가능' : '❌ 불가능'}
                        </div>
                    </td>
                    <td style="font-weight: 600;">${gp.company_name}</td>
                    <td>
                        ${gp.link ? `<a href="${gp.link}" target="_blank" style="color: #3b82f6; text-decoration: underline;">${gp.name}</a>` : gp.name}
                    </td>
                </tr>
            </tbody>
        `;

        const gpInfoTable = document.getElementById('gpInfoTable');
        const gpInfoSection = document.getElementById('gpInfoSection');

        if (gpInfoTable) gpInfoTable.innerHTML = tableHtml;
        if (gpInfoSection) gpInfoSection.style.display = 'block';

        // 경고 표시
        const warning = document.getElementById('gpWarning');
        if (warning) {
            if (!areaAvailable || !dateAvailable) {
                const issues = [];
                if (!areaAvailable) issues.push('공사지역');
                if (!dateAvailable) issues.push('공사일정');

                warning.innerHTML = `<p>⚠️ 주의: 고객의 ${issues.join('과 ')}이 공동구매 조건과 맞지 않습니다.</p>`;
                warning.style.display = 'block';
            } else {
                warning.style.display = 'none';
            }
        }
    }

    // 할당 실행
    function executeAssignment() {
        if (selectedCompanyIds.length === 0) {
            if (window.Toast) {
                window.Toast.warning('할당할 업체를 선택해주세요.');
            } else {
                alert('할당할 업체를 선택해주세요.');
            }
            return;
        }

        const designationType = document.querySelector('input[name="designationType"]:checked').value;
        const gpSelect = document.getElementById('gpSelect');
        const gpNo = designationType === '공동구매' ? parseInt(gpSelect.value) : null;

        if (designationType === '공동구매' && !gpNo) {
            if (window.Toast) {
                window.Toast.warning('공동구매를 선택해주세요.');
            } else {
                alert('공동구매를 선택해주세요.');
            }
            return;
        }

        // API URL 가져오기
        const apiUrl = window.ApiConfig
            ? window.ApiConfig.endpoints.orders.assignCompanies
            : '/order/api/orders/assign_companies/';

        // 할당 API 호출
        const assignData = {
            order_no: currentAssignOrderNo,
            company_ids: selectedCompanyIds,
            designation_type: designationType,
            group_purchase_id: gpNo
        };

        apiCall(apiUrl, 'POST', assignData)
            .then(data => {
                if (data.success) {
                    if (window.Toast) {
                        window.Toast.success(`${selectedCompanyIds.length}개 업체가 할당되었습니다.`);
                    } else {
                        alert(`${selectedCompanyIds.length}개 업체가 할당되었습니다.`);
                    }
                    closeAssignModal();
                    setTimeout(() => location.reload(), 1000);
                } else {
                    if (window.Toast) {
                        window.Toast.error('할당 실패: ' + (data.message || '알 수 없는 오류'));
                    } else {
                        alert('할당 실패: ' + (data.message || '알 수 없는 오류'));
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (window.Toast) {
                    window.Toast.error('할당 중 오류가 발생했습니다.');
                } else {
                    alert('할당 중 오류가 발생했습니다.');
                }
            });
    }

    // 이벤트 리스너 등록 (DOM 로드 후)
    document.addEventListener('DOMContentLoaded', function() {
        // 모달 닫기 버튼
        const closeBtn = document.getElementById('assignModalCloseBtn');
        if (closeBtn) closeBtn.addEventListener('click', closeAssignModal);

        // 모달 외부 클릭
        const modal = document.getElementById('assignModal');
        if (modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === this) closeAssignModal();
            });
        }

        // 지정 타입 라디오 버튼
        document.querySelectorAll('input[name="designationType"]').forEach(radio => {
            radio.addEventListener('change', function() {
                const gpSelect = document.getElementById('gpSelect');
                const gpSection = document.getElementById('gpInfoSection');

                if (this.value === '공동구매') {
                    if (gpSelect) gpSelect.style.display = 'inline-block';
                } else {
                    if (gpSelect) gpSelect.style.display = 'none';
                    if (gpSection) gpSection.style.display = 'none';
                }

                // 라디오 레이블 active 클래스 토글
                document.querySelectorAll('.radio-label').forEach(label => {
                    label.classList.remove('active');
                });
                this.parentElement.classList.add('active');
            });
        });

        // 공동구매 선택
        const gpSelect = document.getElementById('gpSelect');
        if (gpSelect) {
            gpSelect.addEventListener('change', function() {
                const gpNo = parseInt(this.value);
                if (!gpNo) {
                    const gpSection = document.getElementById('gpInfoSection');
                    if (gpSection) gpSection.style.display = 'none';
                    return;
                }

                const gp = allGroupPurchases.find(g => g.no === gpNo);
                if (gp) displayGroupPurchaseInfo(gp);
            });
        }

        // 검색 및 필터
        const searchInput = document.getElementById('companySearch');
        const regionFilter = document.getElementById('regionFilter');
        const typeFilter = document.getElementById('constructionTypeFilter');

        if (searchInput) searchInput.addEventListener('input', renderCompanyTable);
        if (regionFilter) regionFilter.addEventListener('change', renderCompanyTable);
        if (typeFilter) typeFilter.addEventListener('change', renderCompanyTable);

        // 할당 버튼
        const assignBtn = document.getElementById('assignBtn');
        if (assignBtn) assignBtn.addEventListener('click', executeAssignment);
    });

})();
