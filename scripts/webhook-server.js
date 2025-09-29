#!/usr/bin/env node

const express = require('express');
const crypto = require('crypto');
const { execSync } = require('child_process');
const app = express();

// 환경 변수 설정
const PORT = process.env.WEBHOOK_PORT || 8080;
const SECRET = process.env.WEBHOOK_SECRET || 'testpark-webhook-secret';
const DEPLOY_SCRIPT = process.env.DEPLOY_SCRIPT || '/var/www/testpark/scripts/deploy-docker.sh';

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

    console.log('🚀 GitHub Actions 배포 요청을 받았습니다...');
    console.log(`📦 프로젝트: ${payload.project || 'undefined'}`);
    console.log(`📝 커밋: ${payload.commit || 'undefined'}`);
    console.log(`🌿 브랜치: ${payload.branch || 'undefined'}`);
    console.log(`🐳 이미지: ${payload.image || 'undefined'}`);

    // 커밋 정보 가져오기
    let commitInfo = {
        message: '',
        author: '',
        date: ''
    };

    try {
        const gitShow = execSync(`cd /var/www/testpark && git show --format="%s|%an|%ai" -s ${payload.commit || 'HEAD'}`, { encoding: 'utf8' });
        const [message, author, date] = gitShow.trim().split('|');
        commitInfo = { message, author, date };
        console.log(`📋 커밋 메시지: ${commitInfo.message}`);
        console.log(`👤 작성자: ${commitInfo.author}`);
    } catch (e) {
        console.log('⚠️ 커밋 정보 가져오기 실패');
    }

    // 잔디 배포 시작 알림
    if (process.env.JANDI_WEBHOOK) {
        try {
            execSync(`curl -X POST "${process.env.JANDI_WEBHOOK}" -H "Content-Type: application/json" -d '{
                "title": "🚀 배포 시작",
                "body": "프로젝트: ${payload.project || 'testpark'}\\n브랜치: ${payload.branch || 'master'}\\n커밋: ${commitInfo.message || payload.commit}\\n작성자: ${commitInfo.author || 'Unknown'}",
                "color": "FAC11B"
            }'`, { encoding: 'utf8' });
        } catch (e) {
            console.log('⚠️ 잔디 시작 알림 실패');
        }
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
    console.log('🔄 수동 Docker Compose 배포 요청을 받았습니다...');

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