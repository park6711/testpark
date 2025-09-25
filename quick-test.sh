#!/bin/bash
echo "🔄 GitHub Secrets 재설정 후 빠른 테스트"
git commit --allow-empty -m "test: Docker Hub authentication retry after secrets update"
git push origin master
echo "✅ 푸시 완료! GitHub Actions 확인: https://github.com/park6711/testpark/actions"