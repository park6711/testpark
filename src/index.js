const express = require('express');
const app = express();
const PORT = 3000;

app.get('/', (req, res) => {
  res.json({
    message: '🎉 TestPark 애플리케이션이 성공적으로 실행중입니다!',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    docker: true
  });
});

app.get('/health', (req, res) => {
  res.json({ status: 'OK', uptime: process.uptime() });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 TestPark 서버가 포트 ${PORT}에서 실행중입니다!`);
  console.log(`📍 http://localhost:${PORT}`);
});