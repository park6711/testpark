#!/usr/bin/env node

const express = require('express');
const crypto = require('crypto');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const app = express();

// 환경 변수 설정
const PORT = process.env.WEBHOOK_PORT || 8080;
const SECRET = process.env.WEBHOOK_SECRET || 'testpark-webhook-secret';
const DEPLOY_SCRIPT = process.env.DEPLOY_SCRIPT || '/var/www/testpark/scripts/deploy-docker.sh';
const DEPLOY_LOG_FILE = '/var/www/testpark/logs/deploy-history.log';

// 로그 디렉토리 생성
const logDir = path.dirname(DEPLOY_LOG_FILE);
if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
}

// 배포 이력 로깅 함수
function logDeployment(deployInfo) {
    const timestamp = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });
    const logEntry = `[${timestamp}] ${JSON.stringify(deployInfo)}\n`;
    fs.appendFileSync(DEPLOY_LOG_FILE, logEntry);
}

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

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

    const deployTime = payload.deploy_time_kst || new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });

    console.log('🚀 GitHub Actions 배포 요청을 받았습니다...');
    console.log(`📦 프로젝트: ${payload.project || 'undefined'}`);
    console.log(`📝 커밋: ${payload.commit || 'undefined'}`);
    console.log(`🌿 브랜치: ${payload.branch || 'undefined'}`);
    console.log(`🐳 이미지: ${payload.image || 'undefined'}`);
    console.log(`⏰ 배포 시각: ${deployTime}`);

    // 커밋 정보 가져오기 (GitHub에서 보낸 정보 우선 사용)
    let commitInfo = {
        message: payload.commit_message || '',
        author: payload.commit_author || '',
        date: deployTime
    };

    // GitHub에서 정보가 없으면 로컬 git에서 가져오기
    if (!commitInfo.message || !commitInfo.author) {
        try {
            const gitShow = execSync(`cd /var/www/testpark && git show --format="%s|%an|%ai" -s ${payload.commit || 'HEAD'}`, { encoding: 'utf8' });
            const [message, author, date] = gitShow.trim().split('|');
            commitInfo.message = commitInfo.message || message;
            commitInfo.author = commitInfo.author || author;
            commitInfo.date = commitInfo.date || date;
        } catch (e) {
            console.log('⚠️ 로컬 git에서 커밋 정보 가져오기 실패');
        }
    }

    console.log(`📋 커밋 메시지: ${commitInfo.message}`);
    console.log(`👤 작성자: ${commitInfo.author}`);
    console.log(`📅 배포 시각: ${commitInfo.date}`);

    // 배포 이력 로깅
    const deployLogInfo = {
        type: 'github_actions',
        project: payload.project || 'testpark',
        commit: payload.commit,
        branch: payload.branch,
        image: payload.image,
        message: commitInfo.message,
        author: commitInfo.author,
        deployTime: deployTime,
        trigger: payload.trigger || 'github_actions'
    };
    logDeployment(deployLogInfo);
    console.log('📝 배포 이력이 로그 파일에 기록되었습니다.');

    // 잔디 배포 시작 알림 (개선된 형식)
    const jandiWebhook = process.env.JANDI_WEBHOOK || 'https://wh.jandi.com/connect-api/webhook/15016768/cb65bef68396631906dc71e751ff5784';
    try {
        const jandiPayload = {
            body: `🚀 **GitHub Actions 배포 수신**\n\n📍 **위치**: 실서버 (웹훅 서버)\n🔄 **상태**: 배포 스크립트 실행 준비\n\n📋 **배포 정보**:\n• 프로젝트: ${payload.project || 'testpark'}\n• 브랜치: ${payload.branch || 'master'}\n• 커밋: ${payload.commit?.substring(0, 7) || 'unknown'}\n• 이미지: ${payload.image || 'unknown'}\n\n⏰ **배포 시각**: ${deployTime}\n👤 **작성자**: ${commitInfo.author || 'Unknown'}\n📝 **커밋 메시지**: ${commitInfo.message || 'No message'}\n\n▶️ 배포 스크립트 실행 중...`,
            connectColor: '#2196F3'
        };

        execSync(`curl -s -X POST "${jandiWebhook}" -H "Content-Type: application/json" -d '${JSON.stringify(jandiPayload)}'`, { encoding: 'utf8' });
        console.log('✅ 잔디 배포 시작 알림 전송 완료');
    } catch (e) {
        console.log('⚠️ 잔디 시작 알림 실패:', e.message);
    }

    try {
        // 배포 전에 최신 코드 가져오기 (스크립트 업데이트 포함)
        console.log('📥 최신 코드를 가져옵니다 (git pull)...');
        try {
            // 먼저 로컬 변경사항 임시 저장
            console.log('💾 로컬 변경사항 임시 저장 (git stash)...');
            execSync('cd /var/www/testpark && git stash push -m "Auto-stash before deployment $(date +%Y%m%d_%H%M%S)"', { encoding: 'utf8' });

            // git pull 실행
            const gitPullOutput = execSync('cd /var/www/testpark && git pull origin master', { encoding: 'utf8' });
            console.log('✅ Git pull 성공:', gitPullOutput);

            // stash 복구 시도 (충돌 무시)
            try {
                execSync('cd /var/www/testpark && git stash pop', { encoding: 'utf8' });
                console.log('✅ 로컬 변경사항 복구 완료');
            } catch (stashError) {
                console.log('⚠️ 로컬 변경사항 복구 중 충돌 (무시하고 진행)');
            }
        } catch (gitError) {
            console.error('❌ Git pull 실패:', gitError.message);

            // 잔디에 Git pull 오류 알림
            if (process.env.JANDI_WEBHOOK) {
                try {
                    execSync(`curl -X POST "${process.env.JANDI_WEBHOOK}" -H "Content-Type: application/json" -d '{
                        "title": "⚠️ Git Pull 실패",
                        "body": "위치: git pull 단계\\n오류: ${gitError.message.replace(/'/g, "'")}\\n조치: 강제 업데이트 시도 중...",
                        "color": "FF8C00"
                    }'`, { encoding: 'utf8' });
                } catch (e) {
                    console.log('⚠️ 잔디 오류 알림 실패');
                }
            }

            // git pull 실패 시 강제 업데이트 시도
            console.log('🔄 강제 업데이트 시도 (git reset --hard)...');
            try {
                execSync('cd /var/www/testpark && git fetch origin master && git reset --hard origin/master', { encoding: 'utf8' });
                console.log('✅ 강제 업데이트 성공');
            } catch (resetError) {
                console.error('❌ 강제 업데이트도 실패:', resetError.message);

                // 잔디에 완전 실패 알림
                if (process.env.JANDI_WEBHOOK) {
                    try {
                        execSync(`curl -X POST "${process.env.JANDI_WEBHOOK}" -H "Content-Type: application/json" -d '{
                            "title": "❌ 배포 실패",
                            "body": "위치: git reset --hard 단계\\n오류: 코드 업데이트 완전 실패\\n조치: 수동 개입 필요\\n\\n로컬 파일 충돌로 인한 문제일 가능성이 높습니다.",
                            "color": "FF0000"
                        }'`, { encoding: 'utf8' });
                    } catch (e) {
                        console.log('⚠️ 잔디 실패 알림 전송 실패');
                    }
                }

                throw new Error('코드 업데이트 실패 - 수동 개입 필요');
            }
        }

        const output = execSync(`bash ${DEPLOY_SCRIPT}`, { encoding: 'utf8' });
        console.log('✅ GitHub Actions Docker Compose 배포 완료:', output);

        // 잔디에 성공 알림
        if (process.env.JANDI_WEBHOOK) {
            try {
                execSync(`curl -X POST "${process.env.JANDI_WEBHOOK}" -H "Content-Type: application/json" -d '{
                    "title": "✅ 배포 성공",
                    "body": "프로젝트: ${payload.project || 'testpark'}\\n커밋: ${commitInfo.message || payload.commit}\\n작성자: ${commitInfo.author || 'Unknown'}\\n\\n배포가 성공적으로 완료되었습니다!",
                    "color": "00C851"
                }'`, { encoding: 'utf8' });
            } catch (e) {
                console.log('⚠️ 잔디 성공 알림 실패');
            }
        }
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
        res.status(500).json({
            success: false,
            message: 'GitHub Actions Docker Compose deployment failed',
            error: error.message,
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
    const deployTime = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });
    const requestIP = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
    const requestUser = req.body.user || req.query.user || 'Unknown';

    console.log('🔄 수동 Docker Compose 배포 요청을 받았습니다...');
    console.log(`⏰ 요청 시각: ${deployTime}`);
    console.log(`🌐 요청 IP: ${requestIP}`);
    console.log(`👤 요청자: ${requestUser}`);

    // 현재 커밋 정보 가져오기
    let commitInfo = {
        commit: 'unknown',
        message: 'unknown',
        author: 'unknown',
        branch: 'unknown'
    };

    try {
        const currentCommit = execSync('cd /var/www/testpark && git rev-parse HEAD', { encoding: 'utf8' }).trim();
        const currentBranch = execSync('cd /var/www/testpark && git rev-parse --abbrev-ref HEAD', { encoding: 'utf8' }).trim();
        const gitShow = execSync(`cd /var/www/testpark && git show --format="%s|%an" -s HEAD`, { encoding: 'utf8' });
        const [message, author] = gitShow.trim().split('|');

        commitInfo = {
            commit: currentCommit,
            message: message || 'No message',
            author: author || 'Unknown',
            branch: currentBranch
        };
    } catch (e) {
        console.log('⚠️ 커밋 정보 가져오기 실패');
    }

    console.log(`📝 현재 커밋: ${commitInfo.commit.substring(0, 7)}`);
    console.log(`🌿 현재 브랜치: ${commitInfo.branch}`);

    // 배포 이력 로깅
    const deployLogInfo = {
        type: 'manual_deploy',
        deployTime: deployTime,
        requestIP: requestIP,
        requestUser: requestUser,
        commit: commitInfo.commit,
        branch: commitInfo.branch,
        message: commitInfo.message,
        author: commitInfo.author
    };
    logDeployment(deployLogInfo);
    console.log('📝 수동 배포 이력이 로그 파일에 기록되었습니다.');

    // 잔디 수동 배포 시작 알림
    const jandiWebhook = process.env.JANDI_WEBHOOK || 'https://wh.jandi.com/connect-api/webhook/15016768/cb65bef68396631906dc71e751ff5784';
    try {
        const jandiPayload = {
            body: `⚠️ **수동 배포 실행**\n\n📍 **위치**: 실서버 (웹훅 서버)\n🔄 **상태**: 수동 배포 스크립트 실행 중\n\n📋 **배포 정보**:\n• 현재 브랜치: ${commitInfo.branch}\n• 현재 커밋: ${commitInfo.commit.substring(0, 7)}\n• 커밋 메시지: ${commitInfo.message}\n\n⏰ **배포 시각**: ${deployTime}\n👤 **요청자**: ${requestUser}\n🌐 **요청 IP**: ${requestIP}\n\n🛠️ **주의**: 이것은 자동 배포가 아닌 수동 실행입니다.`,
            connectColor: '#FF9800'
        };

        execSync(`curl -s -X POST "${jandiWebhook}" -H "Content-Type: application/json" -d '${JSON.stringify(jandiPayload)}'`, { encoding: 'utf8' });
        console.log('✅ 잔디 수동 배포 시작 알림 전송 완료');
    } catch (e) {
        console.log('⚠️ 잔디 알림 실패:', e.message);
    }

    try {
        // 배포 전에 최신 코드 가져오기 (스크립트 업데이트 포함)
        console.log('📥 최신 코드를 가져옵니다 (git pull)...');
        try {
            const gitPullOutput = execSync('cd /var/www/testpark && git pull origin master', { encoding: 'utf8' });
            console.log('✅ Git pull 성공:', gitPullOutput);
        } catch (gitError) {
            console.error('⚠️ Git pull 실패 (계속 진행):', gitError.message);
        }

        const output = execSync(`bash ${DEPLOY_SCRIPT}`, { encoding: 'utf8' });
        console.log('✅ 수동 Docker Compose 배포 완료:', output);

        // 성공 알림
        try {
            const successPayload = {
                body: `✅ **수동 배포 완료**\n\n⏰ **완료 시각**: ${new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })}\n👤 **요청자**: ${requestUser}\n\n🌐 서비스: https://carpenterhosting.cafe24.com`,
                connectColor: '#4CAF50'
            };
            execSync(`curl -s -X POST "${jandiWebhook}" -H "Content-Type: application/json" -d '${JSON.stringify(successPayload)}'`, { encoding: 'utf8' });
        } catch (e) {
            console.log('⚠️ 성공 알림 실패');
        }

        res.status(200).json({
            success: true,
            message: 'Manual Docker Compose deployment successful',
            output: output,
            method: 'docker-compose',
            deployInfo: deployLogInfo
        });
    } catch (error) {
        console.error('❌ 수동 Docker Compose 배포 실패:', error.message);

        // 실패 알림
        try {
            const failurePayload = {
                body: `❌ **수동 배포 실패**\n\n⏰ **실패 시각**: ${new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })}\n👤 **요청자**: ${requestUser}\n❌ **오류**: ${error.message}\n\n🛠️ 로그를 확인하세요.`,
                connectColor: '#F44336'
            };
            execSync(`curl -s -X POST "${jandiWebhook}" -H "Content-Type: application/json" -d '${JSON.stringify(failurePayload)}'`, { encoding: 'utf8' });
        } catch (e) {
            console.log('⚠️ 실패 알림 전송 실패');
        }

        res.status(500).json({
            success: false,
            message: 'Manual Docker Compose deployment failed',
            error: error.message,
            method: 'docker-compose'
        });
    }
});

// 배포 로그 조회 엔드포인트
app.get('/deploy-logs', (req, res) => {
    const limit = parseInt(req.query.limit) || 50;

    try {
        if (!fs.existsSync(DEPLOY_LOG_FILE)) {
            return res.json({
                success: true,
                logs: [],
                message: '배포 로그가 아직 없습니다.'
            });
        }

        const logContent = fs.readFileSync(DEPLOY_LOG_FILE, 'utf8');
        const logLines = logContent.trim().split('\n').filter(line => line.length > 0);
        const recentLogs = logLines.slice(-limit).reverse();

        const parsedLogs = recentLogs.map(line => {
            try {
                const match = line.match(/^\[(.*?)\] (.*)$/);
                if (match) {
                    return {
                        timestamp: match[1],
                        data: JSON.parse(match[2])
                    };
                }
                return null;
            } catch (e) {
                return null;
            }
        }).filter(log => log !== null);

        res.json({
            success: true,
            count: parsedLogs.length,
            logs: parsedLogs
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: '로그 읽기 실패',
            error: error.message
        });
    }
});

// 헬스 체크
app.get('/health', (req, res) => {
    res.json({
        status: 'OK',
        service: 'TestPark Docker Compose Webhook Server',
        uptime: process.uptime(),
        version: '3.0.0',
        features: [
            'GitHub Actions 배포 (시간, 커밋 메시지 포함)',
            '수동 배포 추적 (요청자, IP 기록)',
            '배포 이력 로깅',
            '배포 로그 조회 API'
        ]
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