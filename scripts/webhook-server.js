#!/usr/bin/env node

const express = require('express');
const crypto = require('crypto');
const { execSync } = require('child_process');
const app = express();

// 환경 변수 설정 (카페24 환경에서는 프록시 설정 필요)
const PORT = process.env.WEBHOOK_PORT || 8080;
const SECRET = process.env.WEBHOOK_SECRET || 'testpark-webhook-secret';
const DEPLOY_SCRIPT = process.env.DEPLOY_SCRIPT || '/var/www/testpark/scripts/deploy.sh';

app.use(express.raw({ type: 'application/json' }));

// GitHub Webhook 핸들러 (비활성화 - GitHub Actions가 빌드만 담당)
// app.post('/webhook/github', (req, res) => {
//     const signature = req.get('X-Hub-Signature-256');
//     const body = req.body;

//     // 서명 검증
//     const expectedSignature = 'sha256=' + crypto
//         .createHmac('sha256', SECRET)
//         .update(body)
//         .digest('hex');

//     if (!crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSignature))) {
//         console.log('❌ GitHub Webhook 서명 검증 실패');
//         return res.status(401).send('Unauthorized');
//     }

//     const payload = JSON.parse(body.toString());

//     // push 이벤트만 처리
//     if (payload.ref === 'refs/heads/master' || payload.ref === 'refs/heads/main') {
//         console.log('🚀 GitHub push 이벤트 감지 - 배포를 시작합니다...');
//         console.log(`📝 커밋: ${payload.head_commit.message}`);
//         console.log(`👤 작성자: ${payload.head_commit.author.name}`);

//         try {
//             // 배포 스크립트 실행
//             const output = execSync(`bash ${DEPLOY_SCRIPT}`, { encoding: 'utf8' });
//             console.log('✅ 배포 완료:', output);
//             res.status(200).send('Deployment successful');
//         } catch (error) {
//             console.error('❌ 배포 실패:', error.message);
//             res.status(500).send('Deployment failed');
//         }
//     } else {
//         console.log('ℹ️ 무시된 브랜치:', payload.ref);
//         res.status(200).send('Ignored branch');
//     }
// });

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
            console.log('✅ 배포 완료:', output);
            res.status(200).send('Deployment successful');
        } catch (error) {
            console.error('❌ 배포 실패:', error.message);
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
    console.log(`📦 프로젝트: ${payload.project}`);
    console.log(`📝 커밋: ${payload.commit}`);
    console.log(`🌿 브랜치: ${payload.branch}`);
    console.log(`🐳 이미지: ${payload.image}`);

    try {
        const output = execSync(`bash ${DEPLOY_SCRIPT}`, { encoding: 'utf8' });
        console.log('✅ GitHub Actions 배포 완료:', output);
        res.status(200).json({
            success: true,
            message: 'GitHub Actions deployment successful',
            output: output,
            deployInfo: {
                project: payload.project,
                commit: payload.commit,
                branch: payload.branch,
                image: payload.image
            }
        });
    } catch (error) {
        console.error('❌ GitHub Actions 배포 실패:', error.message);
        res.status(500).json({
            success: false,
            message: 'GitHub Actions deployment failed',
            error: error.message,
            deployInfo: {
                project: payload.project,
                commit: payload.commit,
                branch: payload.branch,
                image: payload.image
            }
        });
    }
});

// 수동 배포 엔드포인트
app.post('/deploy', (req, res) => {
    console.log('🔄 수동 배포 요청을 받았습니다...');

    try {
        const output = execSync(`bash ${DEPLOY_SCRIPT}`, { encoding: 'utf8' });
        console.log('✅ 수동 배포 완료:', output);
        res.status(200).json({
            success: true,
            message: 'Manual deployment successful',
            output: output
        });
    } catch (error) {
        console.error('❌ 수동 배포 실패:', error.message);
        res.status(500).json({
            success: false,
            message: 'Manual deployment failed',
            error: error.message
        });
    }
});

// 헬스 체크
app.get('/health', (req, res) => {
    res.json({
        status: 'OK',
        service: 'TestPark Webhook Server',
        uptime: process.uptime()
    });
});

// 서버 시작
app.listen(PORT, () => {
    console.log(`🔗 TestPark Webhook 서버가 포트 ${PORT}에서 실행중입니다`);
    console.log(`🚀 GitHub Actions 배포 URL: https://carpenterhosting.cafe24.com/deploy-from-github`);
    console.log(`🐳 Docker Hub Webhook URL: https://carpenterhosting.cafe24.com/webhook/dockerhub`);
    console.log(`🔄 수동 배포 URL: https://carpenterhosting.cafe24.com/deploy`);
    console.log(`🔍 헬스체크 URL: https://carpenterhosting.cafe24.com/health`);
});

// 프로세스 종료 시 정리
process.on('SIGINT', () => {
    console.log('\n🛑 Webhook 서버를 종료합니다...');
    process.exit(0);
});