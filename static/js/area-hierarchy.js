// 계층적 지역 관리 로직
document.addEventListener('DOMContentLoaded', function() {
    console.log('계층적 지역 관리 로직 로드됨');

    // 기존 addArea 함수 오버라이드
    window.originalAddArea = window.addArea;
    window.addArea = function(constructionType, areaType, selectId) {
        addAreaWithHierarchy(constructionType, areaType, selectId);
    };
});

// 계층적 지역 추가 함수
function addAreaWithHierarchy(constructionType, areaType, selectId) {
    console.log('계층적 지역 추가 시작:', constructionType, areaType, selectId);

    // hidden input에서 값 가져오기
    const hiddenInputId = getAreaHiddenInputId ? getAreaHiddenInputId(areaType.toString(), constructionType.toString()) :
        `${areaType === 0 ? 'additional' : areaType === 1 ? 'company-exclude' : 'staff-exclude'}-area-${constructionType}`;

    const areaId = document.getElementById(hiddenInputId)?.value;

    if (!currentCompanyId) {
        alert('먼저 업체를 선택해주세요.');
        return;
    }

    if (!areaId) {
        alert('지역을 선택해주세요.');
        return;
    }

    // 입력 정보 저장
    const searchInputId = getAreaSearchInputId ? getAreaSearchInputId(areaType.toString(), constructionType.toString()) :
        `${areaType === 0 ? 'additional' : areaType === 1 ? 'company-exclude' : 'staff-exclude'}-area-search-${constructionType}`;

    const selectedAreaName = document.getElementById(searchInputId)?.value || '선택된 지역';

    // 계층 구조 검사
    const listId = getListId ? getListId(getAreaTypeString(areaType), constructionType.toString()) :
        `${areaType === 0 ? 'additional' : areaType === 1 ? 'company-exclude' : 'staff-exclude'}-list-${constructionType}`;

    const existingAreas = getCurrentAreaList(listId);
    const hierarchyResult = checkAreaHierarchyAdvanced(areaId, existingAreas);

    console.log('계층 구조 검사 결과:', hierarchyResult);

    if (hierarchyResult.shouldReplace && hierarchyResult.conflictAreas.length > 0) {
        // 충돌 지역이 있는 경우 확인 대화상자 표시
        showAreaReplacementDialog({
            selectedAreaId: areaId,
            selectedAreaName: selectedAreaName,
            conflictAreas: hierarchyResult.conflictAreas,
            warnings: hierarchyResult.warnings,
            constructionType: constructionType,
            areaType: areaType,
            searchInputId: searchInputId,
            hiddenInputId: hiddenInputId
        });
        return;
    }

    // 충돌이 없는 경우 바로 추가
    proceedWithAreaAddition({
        selectedAreaId: areaId,
        constructionType: constructionType,
        areaType: areaType,
        searchInputId: searchInputId,
        hiddenInputId: hiddenInputId
    });
}

// 향상된 계층 구조 검사
function checkAreaHierarchyAdvanced(areaId, existingAreas) {
    const result = {
        warnings: [],
        conflictAreas: [],
        shouldReplace: false
    };
    const areaIdNum = parseInt(areaId);

    console.log('계층 구조 검사:', areaIdNum, '기존 지역:', existingAreas);

    // 전국 선택 시
    if (areaIdNum === 0) {
        if (existingAreas.length > 0) {
            result.warnings.push('⚠️ 전국을 선택하면 모든 기존 지역이 삭제됩니다.');
            result.conflictAreas = [...existingAreas];
            result.shouldReplace = true;
        }
        return result;
    }

    // 광역지역 선택 시 하위 시군구/구 검사
    if (areaIdNum >= 1000 && areaIdNum < 10000 && areaIdNum % 1000 === 0) {
        const cityStart = areaIdNum;
        const cityEnd = areaIdNum + 999;
        const conflictAreas = existingAreas.filter(area =>
            area.area_id > cityStart && area.area_id <= cityEnd
        );

        if (conflictAreas.length > 0) {
            result.warnings.push(`⚠️ 하위 지역들이 삭제됩니다: ${conflictAreas.map(a => a.area_name).join(', ')}`);
            result.conflictAreas = conflictAreas;
            result.shouldReplace = true;
        }
    }

    // 통합시 선택 시 하위 구 검사
    const lastDigit = areaIdNum % 10;
    const secondLastDigit = Math.floor((areaIdNum % 100) / 10);
    if (lastDigit === 0 && secondLastDigit >= 1 && secondLastDigit <= 9) {
        const districtStart = areaIdNum;
        const districtEnd = areaIdNum + 9;
        const conflictDistricts = existingAreas.filter(area =>
            area.area_id > districtStart && area.area_id <= districtEnd
        );

        if (conflictDistricts.length > 0) {
            result.warnings.push(`⚠️ 하위 구들이 삭제됩니다: ${conflictDistricts.map(a => a.area_name).join(', ')}`);
            result.conflictAreas = result.conflictAreas.concat(conflictDistricts);
            result.shouldReplace = true;
        }
    }

    // 하위 구/지역 선택 시 상위 지역들 검사
    if (areaIdNum > 1000) {
        // 상위 통합시 검사 (예: 덕양구 선택 시 고양시 체크)
        if (lastDigit >= 1 && lastDigit <= 9 && secondLastDigit >= 1 && secondLastDigit <= 9) {
            const parentCityId = Math.floor(areaIdNum / 10) * 10;
            const conflictParent = existingAreas.find(area => area.area_id === parentCityId);

            if (conflictParent) {
                result.warnings.push(`⚠️ 상위 통합시가 삭제됩니다: ${conflictParent.area_name}`);
                result.conflictAreas = result.conflictAreas.concat([conflictParent]);
                result.shouldReplace = true;
            }
        }

        // 상위 광역지역 검사
        const metroId = Math.floor(areaIdNum / 1000) * 1000;
        const conflictMetro = existingAreas.find(area => area.area_id === metroId);

        if (conflictMetro) {
            result.warnings.push(`⚠️ 상위 광역지역이 삭제됩니다: ${conflictMetro.area_name}`);
            result.conflictAreas = result.conflictAreas.concat([conflictMetro]);
            result.shouldReplace = true;
        }

        // 전국 검사
        const conflictNationwide = existingAreas.find(area => area.area_id === 0);
        if (conflictNationwide) {
            result.warnings.push(`⚠️ 전국 지역이 삭제됩니다: ${conflictNationwide.area_name}`);
            result.conflictAreas = result.conflictAreas.concat([conflictNationwide]);
            result.shouldReplace = true;
        }
    }

    return result;
}

// 지역 교체 확인 대화상자
async function showAreaReplacementDialog(params) {
    const {
        selectedAreaId,
        selectedAreaName,
        conflictAreas,
        warnings,
        constructionType,
        areaType,
        searchInputId,
        hiddenInputId
    } = params;

    const conflictNames = conflictAreas.map(area => area.area_name).join(', ');
    const message = `
⚠️ 계층 구조 충돌 감지

선택한 지역: ${selectedAreaName}
삭제될 지역: ${conflictNames}

${warnings.join('\n')}

계속 진행하면 충돌되는 지역들이 자동으로 삭제되고,
선택한 지역이 추가됩니다.

[확인]을 클릭하시겠습니까?
    `;

    if (await confirm(message)) {
        console.log('사용자가 지역 교체를 확인했습니다.');
        // 충돌 지역들 먼저 삭제
        deleteConflictAreas(conflictAreas, function() {
            // 삭제 완료 후 새 지역 추가
            proceedWithAreaAddition({
                selectedAreaId: selectedAreaId,
                constructionType: constructionType,
                areaType: areaType,
                searchInputId: searchInputId,
                hiddenInputId: hiddenInputId
            });
        });
    } else {
        console.log('사용자가 지역 교체를 취소했습니다.');
    }
}

// 충돌 지역들 삭제
function deleteConflictAreas(conflictAreas, callback) {
    let deletedCount = 0;
    const totalCount = conflictAreas.length;

    console.log(`${totalCount}개의 충돌 지역 삭제 시작`);

    if (totalCount === 0) {
        callback();
        return;
    }

    conflictAreas.forEach(area => {
        const data = { possi_id: area.id };

        fetch('/possiblearea/data/', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            deletedCount++;
            if (data.success) {
                console.log(`충돌 지역 삭제 성공: ${area.area_name}`);
            } else {
                console.error(`충돌 지역 삭제 실패: ${area.area_name}`, data.error);
            }

            // 모든 삭제 완료 시 콜백 실행
            if (deletedCount === totalCount) {
                console.log('모든 충돌 지역 삭제 완료');
                callback();
            }
        })
        .catch(error => {
            deletedCount++;
            console.error('삭제 오류:', error);
            if (deletedCount === totalCount) {
                callback();
            }
        });
    });
}

// 지역 추가 진행
function proceedWithAreaAddition(params) {
    const {
        selectedAreaId,
        constructionType,
        areaType,
        searchInputId,
        hiddenInputId
    } = params;

    console.log('지역 추가 진행:', selectedAreaId);

    // 입력 초기화
    if (document.getElementById(searchInputId)) {
        document.getElementById(searchInputId).value = '';
    }
    if (document.getElementById(hiddenInputId)) {
        document.getElementById(hiddenInputId).value = '';
    }

    const data = {
        company_id: currentCompanyId,
        construction_type: constructionType,
        area_type: areaType,
        area_id: selectedAreaId
    };

    fetch('/possiblearea/data/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('지역 추가 성공:', data);
            // 성공 시 데이터 재로드
            if (typeof loadPossiData === 'function') {
                loadPossiData(currentCompanyId);
            }
        } else {
            alert('추가 실패: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('추가 중 오류가 발생했습니다.');
    });
}

// 현재 지역 목록 가져오기 (개선된 버전)
function getCurrentAreaList(listId) {
    const areas = [];
    const listElement = document.getElementById(listId);

    if (listElement) {
        const items = listElement.querySelectorAll('.area-item');
        items.forEach(item => {
            const deleteBtn = item.querySelector('.area-item-delete');
            const nameElement = item.querySelector('.area-item-name');

            if (deleteBtn && nameElement) {
                const onclick = deleteBtn.getAttribute('onclick');
                const possiId = onclick.match(/deleteArea\((\d+)\)/)?.[1];

                if (possiId) {
                    // 지역 이름에서 ID 추출
                    let areaNameText = nameElement.textContent.trim();
                    let areaId = 0;

                    // ID 정보 추출 (ID: 숫자) 형식
                    const idMatch = areaNameText.match(/\(ID:\s*(\d+)\)/);
                    if (idMatch) {
                        areaId = parseInt(idMatch[1]);
                        // ID 정보 제거
                        areaNameText = areaNameText.replace(/\(ID:\s*\d+\)/, '').trim();
                    } else {
                        // data attribute에서 가져오기
                        areaId = parseInt(item.dataset.areaId) || 0;
                    }

                    // 아이콘 제거
                    areaNameText = areaNameText.replace(/^[🌍🏛️🏢]\s*/, '').trim();

                    // 대체 ID 파싱 (백엔드 ID가 없는 경우)
                    if (areaId === 0) {
                        if (areaNameText.includes('전국')) {
                            areaId = 0;
                        } else if (areaNameText.includes('서울')) {
                            areaId = areaNameText.includes('구') ? 1010 + Math.floor(Math.random() * 200) : 1000;
                        } else if (areaNameText.includes('경기')) {
                            areaId = areaNameText.includes('시') || areaNameText.includes('구') ? 2010 + Math.floor(Math.random() * 200) : 2000;
                        } else if (areaNameText.includes('고양')) {
                            areaId = areaNameText.includes('덕양') ? 2021 : areaNameText.includes('일산') ? 2022 : 2020;
                        } else if (areaNameText.includes('성남')) {
                            areaId = areaNameText.includes('분당') ? 2121 : areaNameText.includes('수정') ? 2122 : 2120;
                        } else {
                            // 기본값
                            areaId = 1000 + Math.floor(Math.random() * 8000);
                        }
                    }

                    areas.push({
                        id: possiId,
                        area_name: areaNameText,
                        area_id: areaId
                    });
                }
            }
        });
    }

    console.log('현재 지역 목록:', areas);
    return areas;
}