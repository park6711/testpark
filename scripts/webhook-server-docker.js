#!/usr/bin/env node

const express = require('express');
const crypto = require('crypto');
const { execSync } = require('child_process');
const app = express();

// 환경 변수 설정
const PORT = process.env.WEBHOOK_PORT || 8080;
const SECRET = process.env.WEBHOOK_SECRET || 'testpark-webhook-secret';
const DEPLOY_SCRIPT = process.env.DEPLOY_SCRIPT || '/app/deploy-docker.sh';

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

    try {
        const output = execSync(`bash ${DEPLOY_SCRIPT}`, { encoding: 'utf8' });
        console.log('✅ GitHub Actions Docker Compose 배포 완료:', output);
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