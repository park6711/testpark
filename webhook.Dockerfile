# TestPark 웹훅 서버 Dockerfile
FROM node:18-alpine

# 필수 패키지 설치 (Docker CLI 포함)
RUN apk add --no-cache curl docker-cli bash

# 작업 디렉토리를 /var/www/testpark로 설정 (마운트된 경로와 일치)
WORKDIR /var/www/testpark

# 의존성 파일 복사 및 설치 (컨테이너 내에서)
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# 스크립트 파일들을 올바른 위치에 복사
COPY scripts/webhook-server-docker.js ./scripts/webhook-server.js
COPY scripts/deploy-docker.sh ./scripts/deploy-docker.sh

# 실행 권한 부여
RUN chmod +x ./scripts/deploy-docker.sh

# 환경 변수 설정
ENV NODE_ENV=production
ENV WEBHOOK_PORT=8080
ENV WEBHOOK_SECRET=testpark-webhook-secret
ENV DEPLOY_SCRIPT=/var/www/testpark/scripts/deploy-docker.sh

# 포트 노출
EXPOSE 8080

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# 실행
CMD ["node", "scripts/webhook-server.js"]