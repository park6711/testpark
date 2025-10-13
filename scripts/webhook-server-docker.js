#!/usr/bin/env node

const express = require('express');
const crypto = require('crypto');
const { execSync } = require('child_process');
const app = express();

// 환경 변수 설정
const PORT = process.env.WEBHOOK_PORT || 8080;
const SECRET = process.env.WEBHOOK_SECRET || 'testpark-webhook-secret';
const DEPLOY_SCRIPT = process.env.DEPLOY_SCRIPT || '/app/deploy-docker.sh';
const JANDI_WEBHOOK_URL = 'https://wh.jandi.com/connect-api/webhook/15016768/cb65bef68396631906dc71e751ff5784';

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 잔디 알림 전송 함수
function sendJandiNotification(message, color = '#F44336') {
    try {
        execSync(`curl -X POST "${JANDI_WEBHOOK_URL}" \
            -H "Content-Type: application/json" \
            -d '${JSON.stringify({ body: message, connectColor: color })}'`,
            { encoding: 'utf8' }
        );
    } catch (error) {
        console.error('❌ 잔디 알림 전송 실패:', error.message);
    }
}

// 에러 타입별 해결 방법 제공
function getErrorSolution(errorMessage) {
    const errorPatterns = {
        'docker pull': {
            emoji: '🐳',
            title: 'Docker 이미지 다운로드 실패',
            solutions: [
                '1️⃣ Docker Hub에서 이미지가 정상적으로 푸시되었는지 확인',
                '2️⃣ 네트워크 연결 상태 확인',
                '3️⃣ Docker Hub 로그인 상태 확인'
            ]
        },
        'docker-compose': {
            emoji: '🔧',
            title: 'Docker Compose 실행 실패',
            solutions: [
                '1️⃣ docker-compose.yml 파일 문법 확인',
                '2️⃣ 포트 충돌 확인 (다른 컨테이너가 같은 포트 사용 중)',
                '3️⃣ 디스크 공간 확인'
            ]
        },
        'No such file': {
            emoji: '📁',
            title: '파일/디렉토리 없음',
            solutions: [
                '1️⃣ 배포 스크립트 경로 확인',
                '2️⃣ 파일 권한 확인',
                '3️⃣ 디렉토리가 정상적으로 마운트되었는지 확인'
            ]
        },
        'permission denied': {
            emoji: '🔐',
            title: '권한 부족',
            solutions: [
                '1️⃣ 파일 실행 권한 부여: chmod +x 파일명',
                '2️⃣ Docker 소켓 권한 확인',
                '3️⃣ sudo 권한 필요 여부 확인'
            ]
        },
        'port is already allocated': {
            emoji: '🚪',
            title: '포트 충돌',
            solutions: [
                '1️⃣ 기존 컨테이너 중지: docker-compose down',
                '2️⃣ 포트 사용 확인: netstat -tulpn | grep 포트번호',
                '3️⃣ 다른 포트로 변경 고려'
            ]
        }
    };

    // 에러 메시지에서 패턴 찾기
    for (const [pattern, info] of Object.entries(errorPatterns)) {
        if (errorMessage.toLowerCase().includes(pattern.toLowerCase())) {
            return info;
        }
    }

    // 기본 해결 방법
    return {
        emoji: '⚠️',
        title: '알 수 없는 오류',
        solutions: [
            '1️⃣ 실서버 로그 확인: docker logs testpark-webhook',
            '2️⃣ 배포 스크립트 직접 실행해보기',
            '3️⃣ 서버 상태 확인: df -h, free -m'
        ]
    };
}

// Docker Hub Webhook 핸들러
app.post('/webhook/dockerhub', (req, res) => {
    const body = req.body;
    const payload = JSON.parse(body.toString());

    console.log('🐳 Docker Hub webhook 이벤트 감지');
    console.log(`📦 이미지: ${payload.repository.repo_name}`);
    console.log(`🏷️ 태그: ${payload.push_data.tag}`);

    // latest 태그인 경우에만 배포
    if (payload.push_data.tag === 'latest') {
        console.log('🚀 최신 이미지 배포를 시작합니다...');

        try {
            const output = execSync(`bash ${DEPLOY_SCRIPT}`, { encoding: 'utf8' });
            console.log('✅ Docker Compose 배포 완료:', output);
            res.status(200).send('Deployment successful');
        } catch (error) {
            console.error('❌ Docker Compose 배포 실패:', error.message);
            res.status(500).send('Deployment failed');
        }
    } else {
        console.log('ℹ️ 무시된 태그:', payload.push_data.tag);
        res.status(200).send('Ignored tag');
    }
});

// GitHub Actions 배포 엔드포인트
app.post('/deploy-from-github', (req, res) => {
    const body = req.body;
    let payload;

    console.log('🔍 GitHub Actions 원본 요청 데이터:', JSON.stringify(body, null, 2));
    console.log('🔍 Content-Type:', req.headers['content-type']);

    try {
        payload = typeof body === 'string' ? JSON.parse(body) : body;
    } catch (e) {
        console.error('❌ GitHub Actions 요청 파싱 실패:', e.message);
        return res.status(400).json({
            success: false,
            message: 'Invalid JSON payload'
        });
    }

    console.log('🚀 GitHub Actions 배포 요청을 받았습니다...');
    console.log(`📦 프로젝트: ${payload.project || 'undefined'}`);
    console.log(`📝 커밋: ${payload.commit || 'undefined'}`);
    console.log(`🌿 브랜치: ${payload.branch || 'undefined'}`);
    console.log(`🐳 이미지: ${payload.image || 'undefined'}`);

    try {
        const output = execSync(`bash ${DEPLOY_SCRIPT}`, { encoding: 'utf8' });
        console.log('✅ GitHub Actions Docker Compose 배포 완료:', output);

        // 배포 스크립트(deploy-docker.sh)가 70%, 75%, 80%, 90%, 100% 알림을 모두 처리
        // 여기서는 응답만 반환

        res.status(200).json({
            success: true,
            message: 'GitHub Actions Docker Compose deployment successful',
            output: output,
            deployInfo: {
                project: payload.project,
                commit: payload.commit,
                branch: payload.branch,
                image: payload.image,
                method: 'docker-compose'
            }
        });
    } catch (error) {
        console.error('❌ GitHub Actions Docker Compose 배포 실패:', error.message);

        // 에러 분석 및 해결 방법 가져오기
        const errorInfo = getErrorSolution(error.message);
        const KST_TIME = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });

        // 잔디로 상세한 에러 정보 전송
        const errorMessage =
            `🚨 **실서버 배포 실패** ${errorInfo.emoji}\n\n` +
            `📍 **위치**: 실서버 (carpenterhosting.cafe24.com)\n` +
            `📊 **진행률**: ▓▓▓▓▓▓░░░░ (60%에서 중단)\n` +
            `❌ **상태**: 배포 실패\n\n` +
            `🔍 **에러 유형**: ${errorInfo.title}\n` +
            `📝 **에러 메시지**:\n\`\`\`\n${error.message.slice(0, 200)}\n\`\`\`\n\n` +
            `💡 **해결 방법**:\n${errorInfo.solutions.join('\n')}\n\n` +
            `📦 **배포 정보**:\n` +
            `• 프로젝트: ${payload.project || 'N/A'}\n` +
            `• 커밋: ${payload.commit ? payload.commit.slice(0, 8) : 'N/A'}\n` +
            `• 브랜치: ${payload.branch || 'N/A'}\n` +
            `• 이미지: ${payload.image || 'N/A'}\n\n` +
            `⏰ **실패 시각**: ${KST_TIME}`;

        sendJandiNotification(errorMessage, '#F44336');

        res.status(500).json({
            success: false,
            message: 'GitHub Actions Docker Compose deployment failed',
            error: error.message,
            errorType: errorInfo.title,
            solutions: errorInfo.solutions,
            deployInfo: {
                project: payload.project,
                commit: payload.commit,
                branch: payload.branch,
                image: payload.image,
                method: 'docker-compose'
            }
        });
    }
});

// 수동 배포 엔드포인트
app.post('/deploy', (req, res) => {
    console.log('🔄 수동 Docker Compose 배포 요청을 받았습니다...');

    try {
        const output = execSync(`bash ${DEPLOY_SCRIPT}`, { encoding: 'utf8' });
        console.log('✅ 수동 Docker Compose 배포 완료:', output);
        res.status(200).json({
            success: true,
            message: 'Manual Docker Compose deployment successful',
            output: output,
            method: 'docker-compose'
        });
    } catch (error) {
        console.error('❌ 수동 Docker Compose 배포 실패:', error.message);
        res.status(500).json({
            success: false,
            message: 'Manual Docker Compose deployment failed',
            error: error.message,
            method: 'docker-compose'
        });
    }
});

// 헬스 체크
app.get('/health', (req, res) => {
    res.json({
        status: 'OK',
        service: 'TestPark Docker Compose Webhook Server',
        uptime: process.uptime(),
        version: '2.0.0'
    });
});

// 서버 시작
app.listen(PORT, () => {
    console.log(`🔗 TestPark Docker Compose Webhook 서버가 포트 ${PORT}에서 실행중입니다`);
    console.log(`🚀 GitHub Actions 배포 URL: https://carpenterhosting.cafe24.com/deploy-from-github`);
    console.log(`🐳 Docker Hub Webhook URL: https://carpenterhosting.cafe24.com/webhook/dockerhub`);
    console.log(`🔄 수동 배포 URL: https://carpenterhosting.cafe24.com/deploy`);
    console.log(`🔍 헬스체크 URL: https://carpenterhosting.cafe24.com/health`);
    console.log(`📦 배포 방식: Docker Compose`);
});

// 프로세스 종료 시 정리
process.on('SIGINT', () => {
    console.log('\n🛑 Docker Compose Webhook 서버를 종료합니다...');
    process.exit(0);
});