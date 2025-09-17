# Node.js 기반 애플리케이션
FROM node:18-alpine

# 작업 디렉토리 설정
WORKDIR /app

# package.json과 package-lock.json 복사 (있는 경우)
COPY package*.json ./

# 의존성 설치
RUN npm install

# 애플리케이션 소스 복사
COPY . .

# 포트 노출
EXPOSE 3000

# 애플리케이션 시작
CMD ["npm", "start"]