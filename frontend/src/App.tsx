import React from 'react';
import './App.css';
import QuoteManagement from './components/QuoteManagement';

// 기존 PPlist 컴포넌트는 타입 에러가 있어 임시로 주석처리
// 나중에 수정 후 사용 가능:
// import QuoteManagementSystem from './components/PPlist';

function App() {
  return (
    <div className="App">
      {/* 새로운 리팩토링된 컴포넌트 (Ant Design 적용) */}
      <QuoteManagement />
    </div>
  );
}

export default App;