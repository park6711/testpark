#!/bin/bash

# TestPark 네트워크 환경 검증 스크립트
# 실행: ./network-test.sh

echo "======================================"
echo "🔍 TestPark 네트워크 환경 검증 시작"
echo "======================================"
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 결과 저장 변수
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 테스트 함수
run_test() {
    local test_name=$1
    local command=$2

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "⏳ $test_name... "

    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 성공${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ 실패${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo "1️⃣ Docker 컨테이너 상태 확인"
echo "------------------------------"
run_test "testpark 컨테이너 실행 확인" "docker ps | grep -q testpark"
run_test "testpark-frontend 컨테이너 실행 확인" "docker ps | grep -q testpark-frontend"
echo ""

echo "2️⃣ Docker 네트워크 확인"
echo "------------------------"
run_test "testpark-network 존재 확인" "docker network ls | grep -q testpark-network"

# 네트워크 상세 정보
echo "   📊 네트워크 정보:"
docker network inspect testpark-network 2>/dev/null | grep -A 5 "testpark" | head -10 | sed 's/^/      /'
echo ""

echo "3️⃣ 컨테이너 간 통신 테스트"
echo "---------------------------"
run_test "frontend → testpark ping" "docker exec testpark-frontend ping -c 1 testpark"
run_test "frontend → testpark:8000 연결" "docker exec testpark-frontend wget -O /dev/null -q http://testpark:8000/order/api/orders/"
echo ""

echo "4️⃣ 호스트에서 서비스 접근 테스트"
echo "---------------------------------"
run_test "Django 서버 (localhost:8000)" "curl -f -s -o /dev/null -w '%{http_code}' http://localhost:8000 | grep -q 200"
run_test "React 서버 (localhost:3000)" "curl -f -s -o /dev/null -w '%{http_code}' http://localhost:3000 | grep -q 200"
echo ""

echo "5️⃣ API 엔드포인트 테스트"
echo "------------------------"
run_test "/order/api/orders/ 접근" "curl -f -s http://localhost:8000/order/api/orders/ | grep -q 'results'"
run_test "/order/api/companies/ 접근" "curl -f -s http://localhost:8000/order/api/companies/"

# API 데이터 개수 확인
ORDER_COUNT=$(curl -s http://localhost:8000/order/api/orders/ 2>/dev/null | python -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null || echo 0)
echo "   📊 현재 의뢰 수: ${ORDER_COUNT}개"
echo ""

echo "6️⃣ CORS 설정 확인"
echo "-----------------"
# CORS 헤더 확인 (OPTIONS 메서드 사용)
CORS_CHECK=$(curl -s -I -X OPTIONS http://localhost:8000/order/api/orders/ -H "Origin: http://localhost:3000" 2>/dev/null | grep -i "access-control-allow-origin" | wc -l)
if [ $CORS_CHECK -gt 0 ]; then
    echo -e "   ${GREEN}✅ CORS 헤더 설정됨${NC}"
else
    echo -e "   ${YELLOW}⚠️  CORS 헤더가 OPTIONS 요청에 없음 (Django 설정 확인 필요)${NC}"
fi
echo ""

echo "7️⃣ 포트 바인딩 확인"
echo "-------------------"
echo "   📊 열린 포트:"
netstat -tuln | grep -E ":8000|:3000" | sed 's/^/      /'
echo ""

echo "8️⃣ 환경 변수 확인"
echo "-----------------"
echo "   📊 React 환경 변수:"
if [ -f /var/www/testpark/frontend/.env.development ]; then
    grep REACT_APP_API_URL /var/www/testpark/frontend/.env.development | sed 's/^/      /'
fi
echo ""

echo "9️⃣ DNS 해석 테스트"
echo "------------------"
# 컨테이너 내부에서 DNS 해석
DNS_RESULT=$(docker exec testpark-frontend getent hosts testpark 2>/dev/null | awk '{print $1}')
if [ ! -z "$DNS_RESULT" ]; then
    echo -e "   ${GREEN}✅ testpark → $DNS_RESULT${NC}"
else
    echo -e "   ${RED}❌ DNS 해석 실패${NC}"
fi
echo ""

echo "🔟 실제 API 호출 시뮬레이션"
echo "---------------------------"
# React에서 Django API 호출 시뮬레이션
echo "   📊 API 응답 테스트:"
docker exec testpark-frontend node -e "
const http = require('http');
http.get('http://testpark:8000/order/api/orders/', (res) => {
  console.log('      Status Code:', res.statusCode);
  console.log('      Content-Type:', res.headers['content-type']);
  if (res.statusCode === 200) {
    console.log('      ✅ API 통신 정상');
  } else {
    console.log('      ❌ API 통신 오류');
  }
}).on('error', (err) => {
  console.error('      ❌ Error:', err.message);
});
" 2>/dev/null

echo ""
echo "======================================"
echo "📊 검증 결과 요약"
echo "======================================"
echo "총 테스트: $TOTAL_TESTS"
echo -e "${GREEN}성공: $PASSED_TESTS${NC}"
echo -e "${RED}실패: $FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 모든 네트워크 테스트 통과!${NC}"
    echo "✅ Docker 네트워크 환경이 정상적으로 구성되어 있습니다."
    echo "✅ React(frontend) ↔ Django(testpark) 통신이 원활합니다."
else
    echo ""
    echo -e "${YELLOW}⚠️  일부 테스트가 실패했습니다.${NC}"
    echo "위의 실패한 항목들을 확인하고 수정이 필요합니다."
fi

echo ""
echo "💡 추가 확인 사항:"
echo "  1. React 앱에서 API 호출 시 http://testpark:8000 사용 확인"
echo "  2. Django CORS 설정에 http://testpark-frontend:3000 포함 확인"
echo "  3. Docker 컨테이너들이 같은 네트워크(testpark-network)에 있는지 확인"
echo ""