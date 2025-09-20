// 드롭다운 선택 기능 수정
document.addEventListener('DOMContentLoaded', function() {
    console.log('드롭다운 수정 스크립트 로드됨');

    // 업체 드롭다운 버튼 클릭 이벤트
    const companyDropdownBtn = document.getElementById('company-dropdown-btn');
    if (companyDropdownBtn) {
        console.log('업체 드롭다운 버튼 찾음');
        companyDropdownBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('업체 드롭다운 버튼 클릭됨');

            const dropdown = document.getElementById('company-dropdown');
            if (dropdown) {
                if (dropdown.style.display === 'block') {
                    dropdown.style.display = 'none';
                } else {
                    // 전체 업체 표시
                    if (typeof showAllCompanies === 'function') {
                        showAllCompanies();
                    } else {
                        dropdown.style.display = 'block';
                    }
                }
            }
        });
    }

    // 지역 드롭다운 버튼들 클릭 이벤트
    setTimeout(function() {
        const areaDropdownBtns = document.querySelectorAll('.area-dropdown-btn');
        console.log('지역 드롭다운 버튼 개수:', areaDropdownBtns.length);

        areaDropdownBtns.forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                const areaType = this.dataset.areaType;
                const constType = this.dataset.constType;
                console.log('지역 드롭다운 버튼 클릭:', areaType, constType);

                const dropdownId = getAreaDropdownId ? getAreaDropdownId(areaType, constType) :
                    `${areaType === '0' ? 'additional' : areaType === '1' ? 'company-exclude' : 'staff-exclude'}-area-dropdown-${constType}`;

                const dropdown = document.getElementById(dropdownId);
                if (dropdown) {
                    if (dropdown.style.display === 'block') {
                        dropdown.style.display = 'none';
                    } else {
                        if (typeof showAllAreas === 'function') {
                            showAllAreas(areaType, constType);
                        } else {
                            dropdown.style.display = 'block';
                        }
                    }
                }
            });
        });
    }, 1000);

    // 드롭다운 항목 클릭 이벤트 개선
    document.addEventListener('click', function(e) {
        // 업체 드롭다운 항목 클릭
        if (e.target.closest('.company-item') && !e.target.closest('.no-result')) {
            e.preventDefault();
            e.stopPropagation();
            console.log('업체 항목 클릭됨');

            const item = e.target.closest('.company-item');
            const companyId = item.dataset.companyId;
            const companyName = item.dataset.companyName;
            const companyType = item.dataset.companyType;

            if (companyId && companyName && companyType) {
                console.log('업체 선택:', companyName);
                if (typeof selectCompany === 'function') {
                    selectCompany(companyId, companyName, companyType);
                }
            }
        }

        // 지역 드롭다운 항목 클릭
        if (e.target.closest('.area-item') && !e.target.closest('.no-result')) {
            e.preventDefault();
            e.stopPropagation();
            console.log('지역 항목 클릭됨');

            const item = e.target.closest('.area-item');
            const areaId = item.dataset.areaId;
            const areaName = item.dataset.areaName;

            // 부모 드롭다운에서 areaType과 constType 찾기
            const dropdown = item.closest('.area-dropdown');
            if (dropdown && areaId && areaName) {
                const dropdownId = dropdown.id;
                let areaType, constType;

                // 드롭다운 ID에서 타입 추출
                if (dropdownId.includes('additional-area-dropdown-')) {
                    areaType = '0';
                    constType = dropdownId.replace('additional-area-dropdown-', '');
                } else if (dropdownId.includes('company-exclude-area-dropdown-')) {
                    areaType = '1';
                    constType = dropdownId.replace('company-exclude-area-dropdown-', '');
                } else if (dropdownId.includes('staff-exclude-area-dropdown-')) {
                    areaType = '2';
                    constType = dropdownId.replace('staff-exclude-area-dropdown-', '');
                }

                if (areaType && constType) {
                    console.log('지역 선택:', areaName, 'type:', areaType, 'const:', constType);
                    if (typeof selectArea === 'function') {
                        selectArea(areaId, areaName, areaType, constType);
                    }
                }
            }
        }
    });

    console.log('드롭다운 수정 스크립트 초기화 완료');
});