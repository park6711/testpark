/**
 * Toast 알림 시스템
 * alert()를 대체하는 사용자 친화적인 알림
 */

(function() {
    'use strict';

    /**
     * Toast 타입별 설정
     */
    const TOAST_TYPES = {
        success: {
            icon: '✅',
            color: '#10b981',
            bgColor: '#d1fae5',
            borderColor: '#059669'
        },
        error: {
            icon: '❌',
            color: '#ef4444',
            bgColor: '#fee2e2',
            borderColor: '#dc2626'
        },
        warning: {
            icon: '⚠️',
            color: '#f59e0b',
            bgColor: '#fef3c7',
            borderColor: '#d97706'
        },
        info: {
            icon: 'ℹ️',
            color: '#3b82f6',
            bgColor: '#dbeafe',
            borderColor: '#2563eb'
        }
    };

    /**
     * Toast 컨테이너 생성
     */
    function createToastContainer() {
        let container = document.getElementById('toast-container');

        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.setAttribute('role', 'region');
            container.setAttribute('aria-label', '알림 메시지');
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 12px;
                max-width: 400px;
                pointer-events: none;
            `;
            document.body.appendChild(container);
        }

        return container;
    }

    /**
     * Toast 메시지 표시
     * @param {string} message - 표시할 메시지
     * @param {string} type - 타입 (success, error, warning, info)
     * @param {number} duration - 표시 시간 (밀리초, 0이면 자동 닫힘 없음)
     */
    function showToast(message, type = 'info', duration = 3000) {
        const container = createToastContainer();
        const config = TOAST_TYPES[type] || TOAST_TYPES.info;

        // Toast 요소 생성
        const toast = document.createElement('div');
        toast.className = 'toast-message';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'polite');
        toast.setAttribute('aria-atomic', 'true');

        toast.style.cssText = `
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px 20px;
            background: ${config.bgColor};
            border-left: 4px solid ${config.borderColor};
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            font-family: 'Noto Sans KR', sans-serif;
            font-size: 14px;
            color: #1f2937;
            pointer-events: auto;
            cursor: pointer;
            animation: slideInRight 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            transition: all 0.3s ease;
            max-width: 100%;
        `;

        // 아이콘
        const icon = document.createElement('span');
        icon.textContent = config.icon;
        icon.style.cssText = `
            font-size: 20px;
            flex-shrink: 0;
        `;

        // 메시지
        const messageText = document.createElement('span');
        messageText.textContent = message;
        messageText.style.cssText = `
            flex: 1;
            word-break: break-word;
            line-height: 1.5;
        `;

        // 닫기 버튼
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '×';
        closeBtn.setAttribute('aria-label', '알림 닫기');
        closeBtn.style.cssText = `
            background: none;
            border: none;
            color: #6b7280;
            font-size: 24px;
            line-height: 1;
            cursor: pointer;
            padding: 0;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
            transition: all 0.2s;
            flex-shrink: 0;
        `;

        closeBtn.addEventListener('mouseenter', () => {
            closeBtn.style.background = 'rgba(0, 0, 0, 0.1)';
        });

        closeBtn.addEventListener('mouseleave', () => {
            closeBtn.style.background = 'none';
        });

        // Toast 조립
        toast.appendChild(icon);
        toast.appendChild(messageText);
        toast.appendChild(closeBtn);

        // 닫기 함수
        const closeToast = () => {
            toast.style.animation = 'slideOutRight 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        };

        // 클릭 시 닫기
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closeToast();
        });

        toast.addEventListener('click', closeToast);

        // 컨테이너에 추가
        container.appendChild(toast);

        // 자동 닫기
        if (duration > 0) {
            setTimeout(closeToast, duration);
        }

        return toast;
    }

    /**
     * 편의 메서드들
     */
    const Toast = {
        success: (message, duration = 3000) => showToast(message, 'success', duration),
        error: (message, duration = 4000) => showToast(message, 'error', duration),
        warning: (message, duration = 3500) => showToast(message, 'warning', duration),
        info: (message, duration = 3000) => showToast(message, 'info', duration),
        show: showToast
    };

    // 애니메이션 스타일 추가
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }

        .toast-message:hover {
            transform: translateX(-5px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2) !important;
        }

        /* 모바일 대응 */
        @media (max-width: 768px) {
            #toast-container {
                left: 10px;
                right: 10px;
                top: 10px;
                max-width: calc(100% - 20px);
            }
        }
    `;
    document.head.appendChild(style);

    // 전역 객체로 노출
    window.Toast = Toast;

})();
