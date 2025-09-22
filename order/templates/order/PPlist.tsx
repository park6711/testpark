import React, { useState } from 'react';
import { Search, Plus, Copy, FileText, Send, X } from 'lucide-react';

const QuoteManagementSystem = () => {
  const [currentPage, setCurrentPage] = useState('list');
  const [expandedRow, setExpandedRow] = useState(null);
  const [showPostModal, setShowPostModal] = useState(false);
  const [showMessageModal, setShowMessageModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showQuoteModal, setShowQuoteModal] = useState(false);
  const [showMemoModal, setShowMemoModal] = useState(false);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [selectedQuoteId, setSelectedQuoteId] = useState(null);
  const [selectedQuoteForModal, setSelectedQuoteForModal] = useState(null);
  const [messageTemplate, setMessageTemplate] = useState('템플릿1');
  const [messageRecipient, setMessageRecipient] = useState('업체+고객');
  const [selectedCompanies, setSelectedCompanies] = useState([]);
  const [selectedServices, setSelectedServices] = useState([]);
  const [selectedRows, setSelectedRows] = useState([]);

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedRows(quoteRequestsData.map(item => item.id));
    } else {
      setSelectedRows([]);
    }
  };

  const handleSelectRow = (id) => {
    if (selectedRows.includes(id)) {
      setSelectedRows(selectedRows.filter(rowId => rowId !== id));
    } else {
      setSelectedRows([...selectedRows, id]);
    }
  };

  const handleDeleteSelected = () => {
    if (selectedRows.length === 0) {
      alert('삭제할 항목을 선택해주세요.');
      return;
    }

    const confirmMessage = selectedRows.length === 1 
      ? '선택한 1개 항목을 삭제하시겠습니까?' 
      : `선택한 ${selectedRows.length}개 항목을 삭제하시겠습니까?`;

    if (window.confirm(confirmMessage)) {
      setQuoteRequestsData(prev => 
        prev.filter(item => !selectedRows.includes(item.id))
      );
      setSelectedRows([]);
    }
  };
  
  const [editField, setEditField] = useState({
    fieldName: '',
    fieldLabel: '',
    currentValue: '',
    newValue: '',
    quoteId: null
  });

  const [statusFormData, setStatusFormData] = useState({
    status: '대기중',
    template: '',
    recipient: '업체+고객',
    messageContent: ''
  });

  const statusOptions = [
    '대기중',
    '할당',
    '반려',
    '취소',
    '제외',
    '업체미비',
    '중복접수',
    '연락처오류',
    '가능문의',
    '불가능답변(X)',
    '고객문의',
    '계약'
  ];

  const statusTransitions = {
    '대기중': ['할당', '업체미비', '중복접수', '연락처오류', '가능문의', '고객문의'],
    '할당': ['반려', '취소', '제외', '연락처오류', '계약'],
    '연락처오류': ['대기중', '할당'],
    '가능문의': ['할당', '불가능답변(X)'],
    '반려': ['대기중', '할당', '계약'],
    '고객문의': ['대기중', '할당'],
    '취소': ['계약'],
    '제외': [],
    '업체미비': ['대기중'],
    '중복접수': [],
    '불가능답변(X)': ['대기중'],
    '계약': []
  };

  const customerInquiryTemplates = {
    '내용문의': '평수만 있거나 공사내용을 알 수 없는 경우에 고객에게 문의',
    '주소문의': '공사 지역이 비어있거나, 건물형태만 있는 경우 또는 시구동만 있는 경우인지 고객에게 문의',
    '주소내용문의': '평수만 있거나 공사내용을 알 수 없는 경우 + 공사 지역이 비어있거나, 건물형태만 있는 경우 또는 시구동만 있는 경우',
    '공사일정문의': '고객이 공사 일정을 적지 않은 경우, 고객께 문의 또는 안내',
    '공사일정먼경우': '고객께 문의 또는 안내',
    '공사일정촉박': '고객께 문의 또는 안내'
  };

  const messageTemplates = {
    '할당': '안녕하세요. {name}님의 {workContent} 견적 요청이 접수되었습니다. 업체에서 곧 연락드릴 예정입니다.',
    '반려': '안녕하세요. {name}님의 견적 요청이 업체 사정으로 반려되었습니다. 다른 업체를 배정해드리겠습니다.',
    '취소': '안녕하세요. {name}님의 견적 요청이 취소되었습니다.',
    '제외': '안녕하세요. {name}님의 견적 요청 처리가 제외되었습니다.',
    '업체미비': '안녕하세요. {name}님의 지역에 현재 가능한 업체가 없습니다. 업체 확보 후 연락드리겠습니다.',
    '중복접수': '안녕하세요. {name}님의 견적 요청이 중복 접수되었습니다.',
    '연락처오류': '안녕하세요. {name}님의 연락처로 연결이 되지 않습니다. 확인 부탁드립니다.',
    '가능문의': '안녕하세요. {name}님의 {workContent} 공사 가능 여부를 업체에 확인중입니다.',
    '불가능답변(X)': '안녕하세요. {name}님의 요청사항은 현재 진행이 어렵습니다. 죄송합니다.',
    '고객문의': '안녕하세요. {name}님의 견적 요청에 추가 확인이 필요합니다.',
    '계약': '안녕하세요. {name}님의 {workContent} 계약이 완료되었습니다. 감사합니다.'
  };

  const [changeHistory, setChangeHistory] = useState([
    {
      id: 1,
      quoteId: 1,
      fieldName: 'workContent',
      datetime: '2025-09-01 10:30',
      author: '관리자1',
      oldValue: '화장실 리모델링',
      newValue: '욕실 리모델링'
    }
  ]);

  const [statusHistory, setStatusHistory] = useState([
    {
      id: 1,
      quoteId: 2,
      datetime: '2025-09-01 16:45',
      author: '관리자1',
      oldStatus: '대기중',
      newStatus: '업체미비',
      messageSent: true
    }
  ]);
  
  const [quoteLinks, setQuoteLinks] = useState([
    {
      id: 1,
      quoteId: 2,
      openQuoteLink: 'https://cafe.naver.com/pcarpenter/841285',
      drafts: [
        { type: '초안', link: 'https://cafe.naver.com/pcarpenter/841286', datetime: '2025-09-01 17:00' },
        { type: '1차', link: 'https://cafe.naver.com/pcarpenter/841287', datetime: '2025-09-02 10:00' }
      ]
    }
  ]);

  const [memos, setMemos] = useState([
    {
      id: 1,
      quoteId: 2,
      datetime: '2025-09-01 16:50',
      author: '관리자1',
      content: '고객이 욕실 타일 색상 변경 요청'
    },
    {
      id: 2,
      quoteId: 3,
      datetime: '2025-09-01 18:25',
      author: '관리자2',
      content: '공사 일정 조율 필요'
    }
  ]);
  
  const [postFormData, setPostFormData] = useState({
    link: '',
    title: '',
    content: ''
  });

  const [quoteRequestsData, setQuoteRequestsData] = useState([
    {
      id: 1,
      receiptDate: '2025-09-01 14:30',
      designation: '서울54호',
      designationType: '업체지정',
      nickname: '홍길동',
      naverId: 'hong123',
      name: '홍길동',
      phone: '010-1234-5678',
      postLink: '',
      area: '고양시 중산동 하늘마을 5단지',
      scheduledDate: '2025-09-15',
      workContent: '욕실 리모델링',
      assignedCompany: '',
      recentStatus: '대기중',
      reRequestCount: 0,
      quoteCount: 0,
      memoCount: 0
    },
    {
      id: 2,
      receiptDate: '2025-09-01 16:45',
      designation: '382회 공동구매 신청',
      designationType: '공동구매',
      nickname: '김철수',
      naverId: 'kim456',
      name: '김철수',
      phone: '010-9876-5432',
      postLink: 'https://cafe.naver.com/pcarpenter/841284',
      area: '광주광역시 서구 동천동 센트럴파크아파트',
      scheduledDate: '2025-09-20',
      workContent: '주방 리모델링',
      assignedCompany: '업체미비',
      recentStatus: '업체미비',
      reRequestCount: 1,
      quoteCount: 0,
      memoCount: 1
    },
    {
      id: 3,
      receiptDate: '2025-09-01 18:20',
      designation: '서울 12호, 서울 17호',
      designationType: '지정없음',
      nickname: '박영희',
      naverId: 'park789',
      name: '박영희',
      phone: '010-5555-6666',
      postLink: 'https://cafe.naver.com/pcarpenter/841292',
      area: '시흥시 배곧동 중흥s클래스',
      scheduledDate: '2025-09-25',
      workContent: '전체 리모델링',
      assignedCompany: '서울22',
      recentStatus: '반려',
      reRequestCount: 2,
      quoteCount: 2,
      memoCount: 0
    }
  ]);

  const companies = [
    { 
      id: 1, 
      name: '서울9',
      location: '강남',
      grade: 1,
      twoDay: '2/1',
      evaluationPeriod: '8/5',
      evaluationMax: 10,
      percentage: 65,
      fixedCost: 0,
      licenses: '전기공사업, 실내건축공사업',
      region: '실제적용',
      features: '24시간 AS 가능, 자체 타일 보유',
      isDesignated: false
    },
    { 
      id: 2, 
      name: '경기32',
      location: '수원',
      grade: 2,
      twoDay: '1/0',
      evaluationPeriod: '5/3',
      evaluationMax: 8,
      percentage: 50,
      fixedCost: -2,
      licenses: '실내건축공사업',
      region: '업체요청',
      features: '친환경 자재 전문',
      isDesignated: false
    },
    { 
      id: 3, 
      name: '인천18',
      location: '부평',
      grade: 3,
      twoDay: '0/0',
      evaluationPeriod: '3/2',
      evaluationMax: 6,
      percentage: 42,
      fixedCost: -1,
      licenses: '실내건축공사업, 전문소방시설공사업',
      region: '실제적용',
      features: '상가 전문, 야간작업 가능',
      isDesignated: false
    },
    { 
      id: 4, 
      name: '서울54',
      location: '강남',
      grade: 1,
      twoDay: '3/2',
      evaluationPeriod: '10/7',
      evaluationMax: 12,
      percentage: 75,
      fixedCost: 0,
      licenses: '종합건설업',
      region: '실제적용',
      features: '고급 자재 전문, VIP 전담팀',
      isDesignated: true
    }
  ];

  const groupPurchases = [
    {
      id: 1,
      round: '382회',
      company: '서울9 강남',
      unavailableDates: ['2025-09-10', '2025-09-11', '2025-09-12', '2025-09-13', '2025-09-14', '2025-09-15'],
      availableAreas: ['서울', '경기'],
      name: '욕실특가',
      link: 'https://cafe.naver.com/pcarpenter/837663'
    },
    {
      id: 2,
      round: '383회',
      company: '인천18 부평',
      unavailableDates: ['2025-09-20', '2025-09-21', '2025-09-22', '2025-09-23', '2025-09-24', '2025-09-25'],
      availableAreas: ['인천', '경기서부'],
      name: '주방리모델링',
      link: 'https://cafe.naver.com/pcarpenter/837664'
    }
  ];

  const regions = [
    '강남구', '서초구', '송파구', '강서구', '마포구', '영등포구',
    '수원시', '성남시', '고양시', '용인시', '부천시', '안양시',
    '인천 남동구', '인천 부평구', '인천 서구'
  ];

  const constructionTypes = [
    '아파트올수리',
    '아파트부분수리',
    '상가올수리',
    '상가부분수리',
    '주택올수리',
    '주택부분수리',
    '신축',
    '증축'
  ];

  const additionalServices = [
    { id: 1, name: '이사1호', type: '업체요청' },
    { id: 2, name: '시스템에어컨5호', type: '' },
    { id: 3, name: '입주청소2호', type: '업체요청' },
    { id: 4, name: '벽걸이TV설치3호', type: '업체요청' },
    { id: 5, name: '붙박이장4호', type: '' }
  ];

  const fieldLabels = {
    designation: '지정',
    nickname: '별명',
    naverId: '네이버ID',
    name: '이름',
    phone: '전화번호',
    area: '공사지역',
    scheduledDate: '공사예정일',
    workContent: '공사내용'
  };

  const openEditModal = (quoteId, fieldName, currentValue) => {
    setEditField({
      fieldName,
      fieldLabel: fieldLabels[fieldName],
      currentValue,
      newValue: currentValue,
      quoteId
    });
    setShowEditModal(true);
  };

  const openQuoteModal = (quoteId) => {
    setSelectedQuoteForModal(quoteId);
    setShowQuoteModal(true);
  };

  const openMemoModal = (quoteId) => {
    setSelectedQuoteForModal(quoteId);
    setShowMemoModal(true);
  };

  const openStatusModal = (quoteId) => {
    const quote = quoteRequestsData.find(q => q.id === quoteId);
    setSelectedQuoteForModal(quoteId);
    setStatusFormData({
      status: quote.recentStatus,
      template: '',
      recipient: '업체+고객',
      messageContent: ''
    });
    setShowStatusModal(true);
  };

  const handleStatusChange = (newStatus) => {
    const quote = quoteRequestsData.find(q => q.id === selectedQuoteForModal);
    const template = messageTemplates[newStatus];
    let messageContent = '';
    
    if (template && quote) {
      messageContent = template
        .replace('{name}', quote.name)
        .replace('{workContent}', quote.workContent);
    }
    
    setStatusFormData({
      ...statusFormData,
      status: newStatus,
      template: newStatus,
      messageContent
    });
  };

  const updateStatus = (sendMessage) => {
    const currentQuote = quoteRequestsData.find(q => q.id === selectedQuoteForModal);
    const datetime = new Date().toISOString().slice(0, 16).replace('T', ' ');
    
    // 상태 변경 이력 추가
    if (currentQuote && currentQuote.recentStatus !== statusFormData.status) {
      setStatusHistory(prev => [
        {
          id: prev.length + 1,
          quoteId: selectedQuoteForModal,
          datetime,
          author: '관리자1',
          oldStatus: currentQuote.recentStatus,
          newStatus: statusFormData.status,
          messageSent: sendMessage
        },
        ...prev
      ]);
    }
    
    setQuoteRequestsData(prev =>
      prev.map(item =>
        item.id === selectedQuoteForModal
          ? { ...item, recentStatus: statusFormData.status }
          : item
      )
    );
    
    if (sendMessage) {
      console.log('문자 발송:', statusFormData);
    }
    
    setShowStatusModal(false);
  };

  const saveFieldEdit = () => {
    const now = new Date();
    const datetime = now.toISOString().slice(0, 16).replace('T', ' ');
    
    if (editField.currentValue !== editField.newValue) {
      setChangeHistory([
        {
          id: changeHistory.length + 1,
          quoteId: editField.quoteId,
          fieldName: editField.fieldName,
          datetime,
          author: '관리자1',
          oldValue: editField.currentValue,
          newValue: editField.newValue
        },
        ...changeHistory
      ]);
    }
    
    setQuoteRequestsData(prev =>
      prev.map(item =>
        item.id === editField.quoteId
          ? { ...item, [editField.fieldName]: editField.newValue }
          : item
      )
    );
    
    setShowEditModal(false);
  };

  const getQuoteCount = (quoteId) => {
    const quote = quoteLinks.find(q => q.quoteId === quoteId);
    if (!quote) return 0;
    return quote.drafts.length;
  };

  const getMemoCount = (quoteId) => {
    return memos.filter(m => m.quoteId === quoteId).length;
  };

  const copyQuoteRequest = (item) => {
    const newItem = {
      ...item,
      id: Math.max(...quoteRequestsData.map(q => q.id)) + 1,
      receiptDate: new Date().toISOString().slice(0, 16).replace('T', ' '),
      postLink: '',
      assignedCompany: '',
      quoteCount: 0,
      memoCount: 0
    };
    setQuoteRequestsData([...quoteRequestsData, newItem]);
  };

  const extractPostNumber = (url) => {
    const match = url.match(/\/(\d{6})$/);
    return match ? match[1] : '';
  };

  const toggleRowExpansion = (id) => {
    setExpandedRow(expandedRow === id ? null : id);
  };

  const openPostModal = (quoteId) => {
    setSelectedQuoteId(quoteId);
    const quote = quoteRequestsData.find(q => q.id === quoteId);
    if (quote) {
      setPostFormData({
        link: quote.postLink || '',
        title: quote.workContent + ' 견적 의뢰',
        content: `안녕하세요.\n\n${quote.area}에서 ${quote.workContent} 작업을 예정하고 있습니다.\n\n공사예정일: ${quote.scheduledDate}\n${quote.designation ? '특별요청: ' + quote.designation : ''}\n\n견적 부탁드립니다.\n감사합니다.`
      });
    }
    setShowPostModal(true);
  };

  const savePostData = () => {
    if (selectedQuoteId) {
      setQuoteRequestsData(prev => 
        prev.map(item => 
          item.id === selectedQuoteId 
            ? { ...item, postLink: postFormData.link }
            : item
        )
      );
    }
    setShowPostModal(false);
    setSelectedQuoteId(null);
  };

  // Modal Components
  const EditModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg w-[500px]">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold">{editField.fieldLabel} 수정</h3>
          <button 
            onClick={() => setShowEditModal(false)}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">현재 값</label>
          <div className="p-2 bg-gray-100 rounded">{editField.currentValue}</div>
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">새로운 값</label>
          {editField.fieldName === 'workContent' || editField.fieldName === 'area' ? (
            <textarea
              value={editField.newValue}
              onChange={(e) => setEditField({...editField, newValue: e.target.value})}
              className="w-full p-2 border rounded h-24"
            />
          ) : editField.fieldName === 'scheduledDate' ? (
            <input
              type="date"
              value={editField.newValue}
              onChange={(e) => setEditField({...editField, newValue: e.target.value})}
              className="w-full p-2 border rounded"
            />
          ) : (
            <input
              type="text"
              value={editField.newValue}
              onChange={(e) => setEditField({...editField, newValue: e.target.value})}
              className="w-full p-2 border rounded"
            />
          )}
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">변경 이력</label>
          <div className="max-h-40 overflow-y-auto border rounded p-2">
            {changeHistory
              .filter(h => h.quoteId === editField.quoteId && h.fieldName === editField.fieldName)
              .map(history => (
                <div key={history.id} className="text-sm mb-2 pb-2 border-b last:border-0">
                  <div className="text-gray-600">{history.datetime} - {history.author}</div>
                  <div>변경값: {history.newValue}</div>
                  <div>변경전값: {history.oldValue}</div>
                </div>
              ))}
            {changeHistory.filter(h => h.quoteId === editField.quoteId && h.fieldName === editField.fieldName).length === 0 && (
              <div className="text-sm text-gray-500">변경 이력이 없습니다.</div>
            )}
          </div>
        </div>
        
        <div className="flex justify-end space-x-2">
          <button 
            onClick={() => setShowEditModal(false)}
            className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
          >
            취소
          </button>
          <button 
            onClick={saveFieldEdit}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            저장
          </button>
        </div>
      </div>
    </div>
  );

  const StatusModal = () => {
    const quote = quoteRequestsData.find(q => q.id === selectedQuoteForModal);
    const quoteStatusHistory = statusHistory.filter(h => h.quoteId === selectedQuoteForModal);
    const currentStatus = quote?.recentStatus || '대기중';
    const hasAssignedCompany = quote?.assignedCompany && quote.assignedCompany !== '';
    
    // 현재 상태에서 변경 가능한 상태들
    let availableStatuses = statusTransitions[currentStatus] || [];
    
    // 연락처오류에서 할당으로 변경 시 업체가 선택되어 있어야 함
    if (currentStatus === '연락처오류' && !hasAssignedCompany) {
      availableStatuses = availableStatuses.filter(s => s !== '할당');
    }
    
    const [selectedInquiryTemplate, setSelectedInquiryTemplate] = useState('');
    const isCustomerInquiry = statusFormData.status === '고객문의';
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white p-6 rounded-lg w-[600px] max-h-[90vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-bold">할당상태 변경</h3>
            <button 
              onClick={() => setShowStatusModal(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="mb-4 p-3 bg-blue-50 rounded">
            <div className="text-sm">
              <span className="font-medium">현재 상태:</span>
              <span className={`ml-2 px-2 py-1 rounded text-xs ${
                currentStatus === '대기중' ? 'bg-gray-100 text-gray-700' :
                currentStatus === '할당' ? 'bg-blue-100 text-blue-700' :
                currentStatus === '반려' ? 'bg-red-100 text-red-700' :
                currentStatus === '취소' ? 'bg-gray-100 text-gray-700' :
                currentStatus === '제외' ? 'bg-gray-100 text-gray-700' :
                currentStatus === '업체미비' ? 'bg-yellow-100 text-yellow-700' :
                currentStatus === '중복접수' ? 'bg-purple-100 text-purple-700' :
                currentStatus === '연락처오류' ? 'bg-orange-100 text-orange-700' :
                currentStatus === '가능문의' ? 'bg-blue-100 text-blue-700' :
                currentStatus === '불가능답변(X)' ? 'bg-red-100 text-red-700' :
                currentStatus === '고객문의' ? 'bg-green-100 text-green-700' :
                currentStatus === '계약' ? 'bg-green-100 text-green-700' :
                'bg-gray-100 text-gray-700'
              }`}>
                {currentStatus}
              </span>
              {quote?.assignedCompany && (
                <>
                  <span className="ml-4 font-medium">할당업체:</span>
                  <span className="ml-2 text-blue-600">{quote.assignedCompany}</span>
                </>
              )}
            </div>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">1. 상태 선택</label>
              <select
                value={statusFormData.status}
                onChange={(e) => {
                  handleStatusChange(e.target.value);
                  setSelectedInquiryTemplate('');
                }}
                className="w-full p-2 border rounded"
              >
                <option value={currentStatus}>{currentStatus}</option>
                {availableStatuses.map(status => (
                  <option key={status} value={status}>{status}</option>
                ))}
              </select>
              {availableStatuses.length === 0 && (
                <div className="mt-2 text-sm text-red-600">
                  현재 상태에서 변경 가능한 상태가 없습니다.
                </div>
              )}
            </div>

            {isCustomerInquiry && (
              <div>
                <label className="block text-sm font-medium mb-2">고객문의 템플릿 선택</label>
                <select
                  value={selectedInquiryTemplate}
                  onChange={(e) => {
                    setSelectedInquiryTemplate(e.target.value);
                    const template = customerInquiryTemplates[e.target.value];
                    if (template) {
                      setStatusFormData({
                        ...statusFormData,
                        messageContent: `안녕하세요. ${quote?.name}님.\n\n${template}\n\n확인 부탁드립니다.`
                      });
                    }
                  }}
                  className="w-full p-2 border rounded"
                >
                  <option value="">템플릿을 선택하세요</option>
                  {Object.keys(customerInquiryTemplates).map(key => (
                    <option key={key} value={key}>{key}</option>
                  ))}
                </select>
                {selectedInquiryTemplate && (
                  <div className="mt-2 p-2 bg-gray-100 rounded text-sm">
                    {customerInquiryTemplates[selectedInquiryTemplate]}
                  </div>
                )}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-2">2. 템플릿 자동선택</label>
              <div className="p-2 bg-gray-100 rounded text-sm">
                {statusFormData.template || '템플릿 없음'}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">3. 수신자 선택</label>
              <select
                value={statusFormData.recipient}
                onChange={(e) => setStatusFormData({...statusFormData, recipient: e.target.value})}
                className="w-full p-2 border rounded"
              >
                <option value="업체+고객">업체+고객</option>
                <option value="업체">업체</option>
                <option value="고객">고객</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">4. 할당 문자 내용</label>
              <textarea
                value={statusFormData.messageContent}
                onChange={(e) => setStatusFormData({...statusFormData, messageContent: e.target.value})}
                className="w-full p-2 border rounded h-32"
                placeholder="문자 내용을 입력하세요..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">상태 변경 이력</label>
              <div className="max-h-40 overflow-y-auto border rounded p-2">
                {quoteStatusHistory.length > 0 ? (
                  quoteStatusHistory.map(history => (
                    <div key={history.id} className="text-sm mb-2 pb-2 border-b last:border-0">
                      <div className="text-gray-600">
                        {history.datetime} - {history.author}
                        {history.messageSent && (
                          <span className="ml-2 text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">
                            문자발송
                          </span>
                        )}
                      </div>
                      <div>
                        <span className={`px-2 py-1 rounded text-xs ${
                          history.oldStatus === '대기중' ? 'bg-gray-100 text-gray-700' :
                          history.oldStatus === '할당' ? 'bg-blue-100 text-blue-700' :
                          history.oldStatus === '반려' ? 'bg-red-100 text-red-700' :
                          history.oldStatus === '취소' ? 'bg-gray-100 text-gray-700' :
                          history.oldStatus === '제외' ? 'bg-gray-100 text-gray-700' :
                          history.oldStatus === '업체미비' ? 'bg-yellow-100 text-yellow-700' :
                          history.oldStatus === '중복접수' ? 'bg-purple-100 text-purple-700' :
                          history.oldStatus === '연락처오류' ? 'bg-orange-100 text-orange-700' :
                          history.oldStatus === '가능문의' ? 'bg-blue-100 text-blue-700' :
                          history.oldStatus === '불가능답변(X)' ? 'bg-red-100 text-red-700' :
                          history.oldStatus === '고객문의' ? 'bg-green-100 text-green-700' :
                          history.oldStatus === '계약' ? 'bg-green-100 text-green-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {history.oldStatus}
                        </span>
                        <span className="mx-2">→</span>
                        <span className={`px-2 py-1 rounded text-xs ${
                          history.newStatus === '대기중' ? 'bg-gray-100 text-gray-700' :
                          history.newStatus === '할당' ? 'bg-blue-100 text-blue-700' :
                          history.newStatus === '반려' ? 'bg-red-100 text-red-700' :
                          history.newStatus === '취소' ? 'bg-gray-100 text-gray-700' :
                          history.newStatus === '제외' ? 'bg-gray-100 text-gray-700' :
                          history.newStatus === '업체미비' ? 'bg-yellow-100 text-yellow-700' :
                          history.newStatus === '중복접수' ? 'bg-purple-100 text-purple-700' :
                          history.newStatus === '연락처오류' ? 'bg-orange-100 text-orange-700' :
                          history.newStatus === '가능문의' ? 'bg-blue-100 text-blue-700' :
                          history.newStatus === '불가능답변(X)' ? 'bg-red-100 text-red-700' :
                          history.newStatus === '고객문의' ? 'bg-green-100 text-green-700' :
                          history.newStatus === '계약' ? 'bg-green-100 text-green-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {history.newStatus}
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-sm text-gray-500">상태 변경 이력이 없습니다.</div>
                )}
              </div>
            </div>

            <div className="flex justify-end space-x-2">
              <button 
                onClick={() => setShowStatusModal(false)}
                className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
              >
                취소
              </button>
              <button 
                onClick={() => updateStatus(false)}
                disabled={availableStatuses.length === 0}
                className={`px-4 py-2 rounded ${
                  availableStatuses.length > 0
                    ? 'bg-yellow-500 text-white hover:bg-yellow-600'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                문자 안보내고 상태변경
              </button>
              <button 
                onClick={() => updateStatus(true)}
                disabled={availableStatuses.length === 0}
                className={`px-4 py-2 rounded ${
                  availableStatuses.length > 0
                    ? 'bg-blue-500 text-white hover:bg-blue-600'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                문자 보내고 상태변경
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const PostModal = () => {
    const [activeTab, setActiveTab] = useState('link');
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white p-6 rounded-lg w-[600px] max-h-[80vh] overflow-y-auto">
          <h3 className="text-lg font-bold mb-4">네이버 카페 게시글 관리</h3>
          
          <div className="flex space-x-2 mb-4 border-b">
            <button
              onClick={() => setActiveTab('link')}
              className={`px-4 py-2 ${activeTab === 'link' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'}`}
            >
              1. 의뢰글 링크
            </button>
            <button
              onClick={() => setActiveTab('post')}
              className={`px-4 py-2 ${activeTab === 'post' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'}`}
            >
              2. 게시글대신의뢰
            </button>
          </div>
          
          {activeTab === 'link' ? (
            <>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">네이버 카페 링크</label>
                  <input 
                    type="url" 
                    value={postFormData.link}
                    onChange={(e) => setPostFormData({...postFormData, link: e.target.value})}
                    className="w-full p-2 border rounded"
                    placeholder="https://cafe.naver.com/pcarpenter/841280"
                  />
                </div>
              </div>
              
              <div className="flex justify-end space-x-2 mt-6">
                <button 
                  onClick={() => {
                    setShowPostModal(false);
                    setActiveTab('link');
                  }}
                  className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
                >
                  취소
                </button>
                <button 
                  onClick={() => {
                    savePostData();
                    setActiveTab('link');
                  }}
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  저장
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">제목</label>
                  <input 
                    type="text" 
                    value={postFormData.title}
                    onChange={(e) => setPostFormData({...postFormData, title: e.target.value})}
                    className="w-full p-2 border rounded"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">내용</label>
                  <textarea 
                    value={postFormData.content}
                    onChange={(e) => setPostFormData({...postFormData, content: e.target.value})}
                    className="w-full p-2 border rounded h-40"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-2 mt-6">
                <button 
                  onClick={() => {
                    setShowPostModal(false);
                    setActiveTab('link');
                  }}
                  className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
                >
                  취소
                </button>
                <button 
                  onClick={() => {
                    setPostFormData({...postFormData, link: 'https://cafe.naver.com/pcarpenter/843361'});
                    if (selectedQuoteId) {
                      setQuoteRequestsData(prev => 
                        prev.map(item => 
                          item.id === selectedQuoteId 
                            ? { ...item, postLink: 'https://cafe.naver.com/pcarpenter/843361' }
                            : item
                        )
                      );
                    }
                    setShowPostModal(false);
                    setSelectedQuoteId(null);
                    setActiveTab('link');
                  }}
                  className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                >
                  게시글게시
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    );
  };

  const MessageModal = () => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg w-96">
        <h3 className="text-lg font-bold mb-4">문자 메시지 발송</h3>
        
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">템플릿 선택</label>
          <select 
            value={messageTemplate} 
            onChange={(e) => setMessageTemplate(e.target.value)}
            className="w-full p-2 border rounded"
          >
            <option value="템플릿1">견적 요청 안내</option>
            <option value="템플릿2">업체 배정 완료</option>
            <option value="템플릿3">견적서 제출 안내</option>
          </select>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">수신자 선택</label>
          <select 
            value={messageRecipient} 
            onChange={(e) => setMessageRecipient(e.target.value)}
            className="w-full p-2 border rounded"
          >
            <option value="업체+고객">업체 + 고객</option>
            <option value="업체">업체만</option>
            <option value="고객">고객만</option>
          </select>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">메시지 내용</label>
          <textarea 
            className="w-full p-2 border rounded h-24"
            placeholder="메시지 내용을 입력하세요..."
          />
        </div>

        <div className="flex justify-end space-x-2">
          <button 
            onClick={() => setShowMessageModal(false)}
            className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
          >
            취소
          </button>
          <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
            발송
          </button>
        </div>
      </div>
    </div>
  );

  const QuoteModal = () => {
    const existingQuoteLink = quoteLinks.find(q => q.quoteId === selectedQuoteForModal);
    const [draftLink, setDraftLink] = useState('');
    
    const getNextDraftType = () => {
      if (!existingQuoteLink || existingQuoteLink.drafts.length === 0) {
        return '초안';
      }
      const draftCount = existingQuoteLink.drafts.filter(d => d.type.includes('차')).length;
      return `${draftCount + 1}차`;
    };

    const addDraftLink = () => {
      if (draftLink) {
        const datetime = new Date().toISOString().slice(0, 16).replace('T', ' ');
        const draftType = getNextDraftType();
        const existing = quoteLinks.find(q => q.quoteId === selectedQuoteForModal);
        
        if (existing) {
          setQuoteLinks(prev =>
            prev.map(item =>
              item.quoteId === selectedQuoteForModal
                ? { 
                    ...item, 
                    drafts: [...item.drafts, { type: draftType, link: draftLink, datetime }]
                  }
                : item
            )
          );
        } else {
          setQuoteLinks(prev => [...prev, {
            id: prev.length + 1,
            quoteId: selectedQuoteForModal,
            openQuoteLink: '',
            drafts: [{ type: '초안', link: draftLink, datetime }]
          }]);
        }
        setDraftLink('');
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white p-6 rounded-lg w-[600px] max-h-[80vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-bold">견적서 관리</h3>
            <button 
              onClick={() => setShowQuoteModal(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="mb-6">
            <h4 className="font-medium mb-2">견적서 링크 추가</h4>
            <div className="flex space-x-2 mb-3">
              <div className="px-3 py-2 bg-gray-100 rounded text-sm font-medium">
                {getNextDraftType()}
              </div>
              <input
                type="url"
                value={draftLink}
                onChange={(e) => setDraftLink(e.target.value)}
                className="flex-1 p-2 border rounded"
                placeholder="견적서 링크 입력"
              />
              <button
                onClick={addDraftLink}
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
              >
                추가
              </button>
            </div>
          </div>

          <div className="mb-4">
            <h4 className="font-medium mb-2">견적서 이력</h4>
            <div className="border rounded p-3 max-h-60 overflow-y-auto">
              {existingQuoteLink?.drafts?.length > 0 ? (
                existingQuoteLink.drafts.map((draft, idx) => (
                  <div key={idx} className="text-sm mb-2 pb-2 border-b last:border-0">
                    <div className="text-gray-600">{draft.datetime}</div>
                    <div>
                      <span className="font-medium">{draft.type}:</span>{' '}
                      <a href={draft.link} className="text-blue-500 hover:underline" target="_blank" rel="noopener noreferrer">
                        {draft.link.split('/').pop()}
                      </a>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-sm text-gray-500">등록된 견적서가 없습니다.</div>
              )}
            </div>
          </div>

          <div className="flex justify-end">
            <button 
              onClick={() => setShowQuoteModal(false)}
              className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
            >
              닫기
            </button>
          </div>
        </div>
      </div>
    );
  };

  const MemoModal = () => {
    const [newMemo, setNewMemo] = useState('');
    const quoteMemos = memos.filter(m => m.quoteId === selectedQuoteForModal);
    
    const addMemo = () => {
      if (newMemo.trim()) {
        const datetime = new Date().toISOString().slice(0, 16).replace('T', ' ');
        setMemos(prev => [...prev, {
          id: prev.length + 1,
          quoteId: selectedQuoteForModal,
          datetime,
          author: '관리자1',
          content: newMemo
        }]);
        setNewMemo('');
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white p-6 rounded-lg w-[600px] max-h-[80vh] overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-bold">메모 관리</h3>
            <button 
              onClick={() => setShowMemoModal(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="mb-6">
            <h4 className="font-medium mb-2">메모 입력</h4>
            <textarea
              value={newMemo}
              onChange={(e) => setNewMemo(e.target.value)}
              className="w-full p-2 border rounded h-24 mb-2"
              placeholder="메모를 입력하세요..."
            />
            <button
              onClick={addMemo}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              메모 추가
            </button>
          </div>

          <div className="mb-4">
            <h4 className="font-medium mb-2">메모 이력</h4>
            <div className="border rounded p-3 max-h-60 overflow-y-auto">
              {quoteMemos.length > 0 ? (
                quoteMemos.map(memo => (
                  <div key={memo.id} className="text-sm mb-3 pb-3 border-b last:border-0">
                    <div className="text-gray-600 font-medium">
                      {memo.datetime} - {memo.author}
                    </div>
                    <div className="mt-1">{memo.content}</div>
                  </div>
                ))
              ) : (
                <div className="text-sm text-gray-500">등록된 메모가 없습니다.</div>
              )}
            </div>
          </div>

          <div className="flex justify-end">
            <button 
              onClick={() => setShowMemoModal(false)}
              className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
            >
              닫기
            </button>
          </div>
        </div>
      </div>
    );
  };

  const CompanyAssignmentPanel = ({ quoteId }) => {
    const quoteData = quoteRequestsData.find(q => q.id === quoteId);
    const [localSelectedCompanies, setLocalSelectedCompanies] = useState([]);
    const [selectedRegion, setSelectedRegion] = useState('');
    const [selectedConstructionType, setSelectedConstructionType] = useState('');
    const [localDesignationType, setLocalDesignationType] = useState(quoteData?.designationType || '지정없음');
    const [selectedGroupPurchase, setSelectedGroupPurchase] = useState(null);
    
    // 지정업체 찾기
    const designatedCompany = localDesignationType === '업체지정' 
      ? companies.find(c => quoteData?.designation?.includes(c.name) || quoteData?.designation?.includes(`${c.name}호`))
      : null;
    
    // 공동구매 정보 찾기 및 가능/불가능 판단
    const groupPurchase = localDesignationType === '공동구매' && selectedGroupPurchase
      ? groupPurchases.find(gp => gp.id === selectedGroupPurchase)
      : null;
    
    const checkGroupPurchaseAvailability = () => {
      if (!groupPurchase || !quoteData) return { dateAvailable: true, areaAvailable: true };
      
      // 날짜 체크
      const scheduledDate = new Date(quoteData.scheduledDate);
      const dateAvailable = !groupPurchase.unavailableDates.some(date => {
        const unavailableDate = new Date(date);
        return scheduledDate.toDateString() === unavailableDate.toDateString();
      });
      
      // 지역 체크
      const customerArea = quoteData.area;
      const areaAvailable = groupPurchase.availableAreas.some(area => 
        customerArea.includes(area) || area === '서울' && customerArea.includes('서울') ||
        area === '경기' && (customerArea.includes('경기') || customerArea.includes('고양') || customerArea.includes('성남')) ||
        area === '인천' && customerArea.includes('인천')
      );
      
      return { dateAvailable, areaAvailable };
    };
    
    const { dateAvailable, areaAvailable } = checkGroupPurchaseAvailability();
    
    // 업체 목록 정렬
    const sortedCompanies = [...companies].sort((a, b) => {
      if (designatedCompany && a.id === designatedCompany.id) return -1;
      if (designatedCompany && b.id === designatedCompany.id) return 1;
      if (groupPurchase && `${a.name} ${a.location}` === groupPurchase.company) return -1;
      if (groupPurchase && `${b.name} ${b.location}` === groupPurchase.company) return 1;
      return 0;
    });
    
    // 이미 할당된 업체들 확인 (같은 의뢰게시글의 모든 할당)
    const allAssignedCompanies = quoteRequestsData
      .filter(q => q.postLink === quoteData.postLink && q.assignedCompany)
      .map(q => q.assignedCompany);
    
    const handleCompanyAllocation = () => {
      if (localSelectedCompanies.length === 0 && selectedServices.length === 0) {
        alert('할당할 업체 또는 부가서비스를 선택해주세요.');
        return;
      }
      
      let rowsToAdd = [];
      let firstItemAssigned = false;
      
      // 선택된 메인 업체들 처리
      localSelectedCompanies.forEach((companyId) => {
        const company = companies.find(c => c.id === companyId);
        const companyName = `${company.name} ${company.location}`;
        
        if (!allAssignedCompanies.includes(companyName)) {
          if (!firstItemAssigned && !quoteData.assignedCompany) {
            // 첫 번째 업체이고 현재 행에 할당된 업체가 없으면 현재 행 업데이트
            setQuoteRequestsData(prev =>
              prev.map(item =>
                item.id === quoteId
                  ? { ...item, assignedCompany: companyName, recentStatus: '대기중' }
                  : item
              )
            );
            firstItemAssigned = true;
          } else {
            // 추가 업체는 새 행 생성
            const newId = Math.max(...quoteRequestsData.map(q => q.id)) + rowsToAdd.length + 1;
            rowsToAdd.push({
              ...quoteData,
              id: newId,
              assignedCompany: companyName,
              recentStatus: '대기중',
              receiptDate: new Date().toISOString().slice(0, 16).replace('T', ' ')
            });
          }
        }
      });
      
      // 선택된 부가서비스들 처리
      selectedServices.forEach((serviceId) => {
        const service = additionalServices.find(s => s.id === serviceId);
        const serviceName = service.name;
        
        if (!firstItemAssigned && !quoteData.assignedCompany) {
          // 첫 번째 서비스이고 메인 업체가 없으면 현재 행 업데이트
          setQuoteRequestsData(prev =>
            prev.map(item =>
              item.id === quoteId
                ? { ...item, assignedCompany: serviceName, recentStatus: '대기중' }
                : item
            )
          );
          firstItemAssigned = true;
        } else {
          // 추가 부가서비스는 새 행 생성
          const newId = Math.max(...quoteRequestsData.map(q => q.id)) + rowsToAdd.length + 1;
          rowsToAdd.push({
            ...quoteData,
            id: newId,
            assignedCompany: serviceName,
            recentStatus: '대기중',
            receiptDate: new Date().toISOString().slice(0, 16).replace('T', ' ')
          });
        }
      });
      
      // 새 행들 추가
      if (rowsToAdd.length > 0) {
        setQuoteRequestsData(prev => [...prev, ...rowsToAdd]);
      }
      
      // 성공 메시지
      const totalAssigned = localSelectedCompanies.length + selectedServices.length;
      alert(`${totalAssigned}개 업체/서비스가 할당되었습니다.`);
      
      setLocalSelectedCompanies([]);
      setSelectedServices([]);
      setExpandedRow(null);
    };
    
    return (
      <tr>
        <td colSpan="17" className="border-0 p-0">
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 m-2">
            <h3 className="font-bold text-lg mb-4">업체할당 정보</h3>
            
            {/* 지역구 및 공사구분 선택 */}
            <div className="mb-4 p-4 bg-white rounded border">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">지역구 선택</label>
                  <select 
                    value={selectedRegion}
                    onChange={(e) => setSelectedRegion(e.target.value)}
                    className="w-full p-2 border rounded"
                  >
                    <option value="">지역구를 선택하세요</option>
                    {regions.map(region => (
                      <option key={region} value={region}>{region}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">공사구분 선택</label>
                  <select 
                    value={selectedConstructionType}
                    onChange={(e) => setSelectedConstructionType(e.target.value)}
                    className="w-full p-2 border rounded"
                  >
                    <option value="">공사구분을 선택하세요</option>
                    {constructionTypes.map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
            
            {/* 견적의뢰 정보 */}
            <div className="mb-4 p-4 bg-white rounded border">
              <h4 className="font-semibold mb-3">견적의뢰 정보</h4>
              <div className="text-sm space-y-2">
                <div>
                  <span className="font-medium text-gray-600">공사내용:</span>
                  <span className="ml-2">{quoteData?.workContent}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-600">공사지역:</span>
                  <span className="ml-2">{quoteData?.area}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-600">공사예정일:</span>
                  <span className="ml-2">{quoteData?.scheduledDate}</span>
                </div>
                {allAssignedCompanies.length > 0 && (
                  <div>
                    <span className="font-medium text-gray-600">기할당업체:</span>
                    <span className="ml-2 text-blue-600 font-medium">{allAssignedCompanies.join(', ')}</span>
                  </div>
                )}
              </div>
            </div>
            
            {/* 지정 타입 선택 */}
            <div className="mb-4 p-4 bg-white rounded border">
              <h4 className="font-semibold mb-3">지정 타입</h4>
              <div className="flex space-x-4">
                <label className="flex items-center">
                  <input 
                    type="radio" 
                    name="designationType" 
                    value="지정없음"
                    checked={localDesignationType === '지정없음'}
                    onChange={(e) => {
                      setLocalDesignationType(e.target.value);
                      setSelectedGroupPurchase(null);
                    }}
                    className="mr-2"
                  />
                  <span className={localDesignationType === '지정없음' ? 'font-semibold' : ''}>지정없음</span>
                </label>
                <label className="flex items-center">
                  <input 
                    type="radio" 
                    name="designationType" 
                    value="업체지정"
                    checked={localDesignationType === '업체지정'}
                    onChange={(e) => {
                      setLocalDesignationType(e.target.value);
                      setSelectedGroupPurchase(null);
                    }}
                    className="mr-2"
                  />
                  <span className={localDesignationType === '업체지정' ? 'font-semibold text-blue-600' : ''}>
                    업체지정 {localDesignationType === '업체지정' && quoteData?.designation && `(${quoteData.designation})`}
                  </span>
                </label>
                <label className="flex items-center">
                  <input 
                    type="radio" 
                    name="designationType" 
                    value="공동구매"
                    checked={localDesignationType === '공동구매'}
                    onChange={(e) => setLocalDesignationType(e.target.value)}
                    className="mr-2"
                  />
                  <span className={localDesignationType === '공동구매' ? 'font-semibold text-green-600' : ''}>
                    공동구매
                  </span>
                </label>
                {localDesignationType === '공동구매' && (
                  <select 
                    value={selectedGroupPurchase || ''}
                    onChange={(e) => setSelectedGroupPurchase(Number(e.target.value))}
                    className="ml-4 p-1 border rounded text-sm"
                  >
                    <option value="">공동구매 선택</option>
                    {groupPurchases.map(gp => (
                      <option key={gp.id} value={gp.id}>{gp.round} - {gp.name}</option>
                    ))}
                  </select>
                )}
              </div>
            </div>
            
            {/* 공동구매 정보 */}
            {localDesignationType === '공동구매' && groupPurchase && (
              <div className="mb-4 p-4 bg-green-50 rounded border border-green-300">
                <h4 className="font-semibold mb-3 text-green-700">공동구매 정보</h4>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-green-100">
                      <th className="border border-green-300 p-2">회차</th>
                      <th className="border border-green-300 p-2">공사가능지역</th>
                      <th className="border border-green-300 p-2">공사불가능일정</th>
                      <th className="border border-green-300 p-2">업체명</th>
                      <th className="border border-green-300 p-2">공동구매이름</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="border border-green-300 p-2 text-center">{groupPurchase.round}</td>
                      <td className={`border border-green-300 p-2 text-center ${!areaAvailable ? 'bg-red-100' : 'bg-green-100'}`}>
                        <div className="font-medium mb-1">
                          {groupPurchase.availableAreas.join(', ')}
                        </div>
                        <div className={`text-xs font-bold ${!areaAvailable ? 'text-red-700' : 'text-green-700'}`}>
                          고객: {quoteData?.area} → {!areaAvailable ? '❌ 불가능' : '✅ 가능'}
                        </div>
                      </td>
                      <td className={`border border-green-300 p-2 text-center ${!dateAvailable ? 'bg-red-100' : 'bg-green-100'}`}>
                        <div className="font-medium mb-1">
                          {groupPurchase.unavailableDates.slice(0, 3).map(date => 
                            new Date(date).toLocaleDateString('ko-KR', { month: '2-digit', day: '2-digit' })
                          ).join(', ')}
                          {groupPurchase.unavailableDates.length > 3 && '...'}
                        </div>
                        <div className={`text-xs font-bold ${!dateAvailable ? 'text-red-700' : 'text-green-700'}`}>
                          고객: {quoteData?.scheduledDate} → {!dateAvailable ? '❌ 불가능' : '✅ 가능'}
                        </div>
                      </td>
                      <td className="border border-green-300 p-2 font-medium text-center">{groupPurchase.company}</td>
                      <td className="border border-green-300 p-2 text-center">
                        <a 
                          href={groupPurchase.link} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline font-medium"
                        >
                          {groupPurchase.name}
                        </a>
                      </td>
                    </tr>
                  </tbody>
                </table>
                {(!dateAvailable || !areaAvailable) && (
                  <div className="mt-3 p-3 bg-red-100 border border-red-300 rounded">
                    <p className="text-red-700 font-medium text-sm">
                      ⚠️ 주의: 고객의 {!dateAvailable && !areaAvailable ? '공사일정과 지역이 모두' : !dateAvailable ? '공사일정이' : '공사지역이'} 
                      {' '}이 공동구매 조건과 맞지 않습니다.
                    </p>
                  </div>
                )}
              </div>
            )}
            
            {/* 할당 가능 업체 */}
            <div className="mt-6">
              <h4 className="font-semibold mb-3">할당 가능 업체 (복수 선택 가능)</h4>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse border border-gray-300 text-xs">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="border p-2">선택</th>
                      <th className="border p-2">업체명</th>
                      <th className="border p-2">평가등급</th>
                      <th className="border p-2">할당수</th>
                      <th className="border p-2">업체면허</th>
                      <th className="border p-2">지역구분</th>
                      <th className="border p-2">특장점</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedCompanies.map(company => {
                      const companyFullName = `${company.name} ${company.location}`;
                      const isAlreadyAssigned = allAssignedCompanies.includes(companyFullName);
                      const isDesignated = designatedCompany && company.id === designatedCompany.id;
                      const isGroupPurchaseCompany = groupPurchase && companyFullName === groupPurchase.company;
                      
                      return (
                        <tr 
                          key={company.id} 
                          className={`hover:bg-gray-50 
                            ${isAlreadyAssigned ? 'bg-gray-100' : ''} 
                            ${isDesignated ? 'bg-blue-50 border-2 border-blue-400' : ''}
                            ${isGroupPurchaseCompany ? 'bg-green-50 border-2 border-green-400' : ''}`}
                        >
                          <td className="border p-2 text-center">
                            <input 
                              type="checkbox"
                              disabled={isAlreadyAssigned}
                              checked={localSelectedCompanies.includes(company.id)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setLocalSelectedCompanies([...localSelectedCompanies, company.id]);
                                } else {
                                  setLocalSelectedCompanies(localSelectedCompanies.filter(id => id !== company.id));
                                }
                              }}
                            />
                          </td>
                          <td className={`border p-2 font-medium ${isAlreadyAssigned ? 'text-gray-500' : ''}`}>
                            {companyFullName}
                            {isAlreadyAssigned && <span className="ml-2 text-xs text-gray-500">(기할당)</span>}
                            {isDesignated && <span className="ml-2 text-xs bg-blue-500 text-white px-2 py-1 rounded">지정업체</span>}
                            {isGroupPurchaseCompany && <span className="ml-2 text-xs bg-green-500 text-white px-2 py-1 rounded">공동구매</span>}
                          </td>
                          <td className="border p-2 text-center">
                            <span className={`px-2 py-1 rounded font-bold ${
                              company.grade === 1 ? 'bg-green-100 text-green-700' :
                              company.grade === 2 ? 'bg-blue-100 text-blue-700' :
                              company.grade === 3 ? 'bg-yellow-100 text-yellow-700' :
                              'bg-gray-100 text-gray-700'
                            } ${isAlreadyAssigned ? 'opacity-50' : ''}`}>
                              {company.grade}등급
                            </span>
                          </td>
                          <td className={`border p-2 ${isAlreadyAssigned ? 'text-gray-500' : ''}`}>
                            <div className="space-y-1">
                              <div>2일: {company.twoDay}</div>
                              <div>평가: {company.evaluationPeriod}</div>
                              <div>최대: {company.evaluationMax}</div>
                              <div className={`font-medium ${
                                company.percentage >= 80 ? 'text-red-600' : 
                                company.percentage >= 60 ? 'text-yellow-600' : 
                                'text-green-600'
                              }`}>
                                {company.percentage}%
                                {company.fixedCost < 0 && (
                                  <span className="text-red-600"> ({company.fixedCost})</span>
                                )}
                              </div>
                            </div>
                          </td>
                          <td className={`border p-2 ${isAlreadyAssigned ? 'text-gray-500' : ''}`}>
                            <div className="text-xs">{company.licenses}</div>
                          </td>
                          <td className="border p-2">
                            <span className={`px-2 py-1 rounded text-xs ${
                              company.region === '실제적용' 
                                ? 'bg-green-100 text-green-700' 
                                : 'bg-gray-100 text-gray-700'
                            } ${isAlreadyAssigned ? 'opacity-50' : ''}`}>
                              {company.region}
                            </span>
                          </td>
                          <td className={`border p-2 text-xs ${isAlreadyAssigned ? 'text-gray-500' : ''}`}>
                            {company.features}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* 부가서비스업체 */}
            <div className="mt-6">
              <h4 className="font-semibold mb-3">할당 가능 부가서비스업체 (복수 선택 가능)</h4>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse border border-gray-300 text-sm">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="border p-2">선택</th>
                      <th className="border p-2">업체명</th>
                      <th className="border p-2">적용구분</th>
                    </tr>
                  </thead>
                  <tbody>
                    {additionalServices.map(service => (
                      <tr key={service.id} className="hover:bg-gray-50">
                        <td className="border p-2 text-center">
                          <input 
                            type="checkbox"
                            checked={selectedServices.includes(service.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedServices([...selectedServices, service.id]);
                              } else {
                                setSelectedServices(selectedServices.filter(id => id !== service.id));
                              }
                            }}
                          />
                        </td>
                        <td className="border p-2 font-medium">{service.name}</td>
                        <td className="border p-2 text-gray-600">
                          {service.type}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="mt-4 flex justify-end space-x-2">
              <button 
                onClick={handleCompanyAllocation}
                disabled={localSelectedCompanies.length === 0 && selectedServices.length === 0}
                className={`px-4 py-2 rounded ${
                  (localSelectedCompanies.length > 0 || selectedServices.length > 0)
                    ? 'bg-green-500 text-white hover:bg-green-600' 
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                선택업체 할당 ({localSelectedCompanies.length + selectedServices.length}개)
              </button>
              <button 
                onClick={() => {
                  setExpandedRow(null);
                  setLocalSelectedCompanies([]);
                  setSelectedServices([]);
                }}
                className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
              >
                닫기
              </button>
            </div>
          </div>
        </td>
      </tr>
    );
  };

  const QuoteListPage = () => (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">견적의뢰 관리</h1>
        <div className="flex space-x-2">
          {selectedRows.length > 0 && (
            <button 
              onClick={handleDeleteSelected}
              className="bg-red-500 text-white px-4 py-2 rounded flex items-center hover:bg-red-600"
            >
              선택 삭제 ({selectedRows.length})
            </button>
          )}
          <button 
            onClick={() => window.open('https://docs.google.com/forms/d/e/1FAIpQLSfOnhe1eBTRM5bb-r_XA6epsUkPctmqexzcwJk-MC5KlC3F4g/viewform', '_blank')}
            className="bg-blue-500 text-white px-4 py-2 rounded flex items-center hover:bg-blue-600"
          >
            <Plus className="w-4 h-4 mr-2" />
            추가
          </button>
        </div>
      </div>

      <div className="mb-4 flex space-x-2">
        <input 
          type="text" 
          placeholder="검색어를 입력하세요..."
          className="flex-1 p-2 border rounded"
        />
        <button className="bg-gray-500 text-white px-4 py-2 rounded flex items-center hover:bg-gray-600">
          <Search className="w-4 h-4 mr-2" />
          검색
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse border border-gray-300">
          <thead>
            <tr className="bg-gray-100">
              <th className="border p-2 w-10">
                <input 
                  type="checkbox"
                  onChange={handleSelectAll}
                  checked={selectedRows.length === quoteRequestsData.length && quoteRequestsData.length > 0}
                />
              </th>
              <th className="border p-2">접수일시</th>
              <th className="border p-2 w-40">지정</th>
              <th className="border p-2">별명</th>
              <th className="border p-2">네이버ID</th>
              <th className="border p-2">이름</th>
              <th className="border p-2">전화번호</th>
              <th className="border p-2">의뢰게시글</th>
              <th className="border p-2 w-32">공사지역</th>
              <th className="border p-2">공사예정일</th>
              <th className="border p-2">공사내용</th>
              <th className="border p-2">할당업체명</th>
              <th className="border p-2">최근할당상태</th>
              <th className="border p-2">재의뢰</th>
              <th className="border p-2">견적</th>
              <th className="border p-2">메모</th>
              <th className="border p-2">액션</th>
            </tr>
          </thead>
          <tbody>
            {quoteRequestsData
              .sort((a, b) => new Date(b.receiptDate) - new Date(a.receiptDate))
              .map(item => (
              <React.Fragment key={item.id}>
                <tr className={`hover:bg-gray-50 ${selectedRows.includes(item.id) ? 'bg-blue-50' : ''}`}>
                  <td className="border p-2 text-center">
                    <input 
                      type="checkbox"
                      checked={selectedRows.includes(item.id)}
                      onChange={() => handleSelectRow(item.id)}
                    />
                  </td>
                  <td className="border p-2 text-sm">{item.receiptDate}</td>
                  <td 
                    className="border p-2 text-xs max-w-40 cursor-pointer hover:bg-yellow-50"
                    onDoubleClick={() => openEditModal(item.id, 'designation', item.designation)}
                  >
                    <div className="break-words">{item.designation}</div>
                  </td>
                  <td 
                    className="border p-2 cursor-pointer hover:bg-yellow-50"
                    onDoubleClick={() => openEditModal(item.id, 'nickname', item.nickname)}
                  >
                    {item.nickname}
                  </td>
                  <td 
                    className="border p-2 cursor-pointer hover:bg-yellow-50"
                    onDoubleClick={() => openEditModal(item.id, 'naverId', item.naverId)}
                  >
                    {item.naverId}
                  </td>
                  <td 
                    className="border p-2 cursor-pointer hover:bg-yellow-50"
                    onDoubleClick={() => openEditModal(item.id, 'name', item.name)}
                  >
                    {item.name}
                  </td>
                  <td 
                    className="border p-2 cursor-pointer hover:bg-yellow-50"
                    onDoubleClick={() => openEditModal(item.id, 'phone', item.phone)}
                  >
                    {item.phone}
                  </td>
                  <td 
                    className="border p-2 cursor-pointer hover:bg-blue-100"
                    onClick={() => openPostModal(item.id)}
                  >
                    {item.postLink ? (
                      <span className="text-blue-500 hover:underline">
                        {extractPostNumber(item.postLink)}
                      </span>
                    ) : (
                      <span className="bg-orange-500 text-white px-2 py-1 rounded text-xs hover:bg-orange-600">
                        대기중
                      </span>
                    )}
                  </td>
                  <td 
                    className="border p-2 text-sm cursor-pointer hover:bg-yellow-50"
                    onDoubleClick={() => openEditModal(item.id, 'area', item.area)}
                  >
                    {item.area}
                  </td>
                  <td 
                    className="border p-2 cursor-pointer hover:bg-yellow-50"
                    onDoubleClick={() => openEditModal(item.id, 'scheduledDate', item.scheduledDate)}
                  >
                    {item.scheduledDate}
                  </td>
                  <td 
                    className="border p-2 cursor-pointer hover:bg-yellow-50"
                    onDoubleClick={() => openEditModal(item.id, 'workContent', item.workContent)}
                  >
                    {item.workContent}
                  </td>
                  <td 
                    className="border p-2 cursor-pointer hover:bg-blue-100"
                    onClick={() => toggleRowExpansion(item.id)}
                  >
                    {item.assignedCompany ? (
                      <span className="text-blue-600 underline">{item.assignedCompany}</span>
                    ) : (
                      <button className="bg-orange-500 text-white px-2 py-1 rounded text-xs hover:bg-orange-600">
                        대기중
                      </button>
                    )}
                  </td>
                  <td 
                    className="border p-2 cursor-pointer hover:bg-blue-100"
                    onClick={() => openStatusModal(item.id)}
                  >
                    <span className={`px-2 py-1 rounded text-xs ${
                      item.recentStatus === '대기중' ? 'bg-gray-100 text-gray-700' :
                      item.recentStatus === '문의중' ? 'bg-blue-100 text-blue-700' :
                      item.recentStatus === '견적완료' ? 'bg-green-100 text-green-700' :
                      item.recentStatus === '계약완료' ? 'bg-purple-100 text-purple-700' :
                      item.recentStatus === '공사중' ? 'bg-yellow-100 text-yellow-700' :
                      item.recentStatus === '공사완료' ? 'bg-indigo-100 text-indigo-700' :
                      item.recentStatus === '반려' ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {item.recentStatus}
                    </span>
                  </td>
                  <td className="border p-2">
                    <button className="text-blue-500 hover:underline">
                      {item.reRequestCount}
                    </button>
                  </td>
                  <td className="border p-2">
                    <button 
                      className="text-blue-500 hover:underline"
                      onClick={() => openQuoteModal(item.id)}
                    >
                      {getQuoteCount(item.id)}
                    </button>
                  </td>
                  <td className="border p-2">
                    <button 
                      className="text-blue-500 hover:underline"
                      onClick={() => openMemoModal(item.id)}
                    >
                      {getMemoCount(item.id)}
                    </button>
                  </td>
                  <td className="border p-2">
                    <div className="flex space-x-1">
                      <button 
                        onClick={() => copyQuoteRequest(item)}
                        className="bg-gray-500 text-white px-2 py-1 rounded text-xs hover:bg-gray-600"
                      >
                        <Copy className="w-3 h-3" />
                      </button>
                    </div>
                  </td>
                </tr>
                {expandedRow === item.id && <CompanyAssignmentPanel quoteId={item.id} />}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const QuoteAddPage = () => (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center mb-6">
        <button 
          onClick={() => setCurrentPage('list')}
          className="mr-4 text-blue-500 hover:underline"
        >
          ← 목록으로
        </button>
        <h1 className="text-2xl font-bold">견적의뢰 추가</h1>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">접수일시</label>
            <input type="datetime-local" className="w-full p-2 border rounded" />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              원하시는 <span className="font-bold">[공동구매]</span> 또는 <span className="font-bold">[열린업체]</span>가 있으시면 적어주세요
            </label>
            <textarea className="w-full p-2 border rounded h-20" placeholder="공동구매 또는 열린업체 정보를 입력하세요..."></textarea>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">별명</label>
            <input type="text" className="w-full p-2 border rounded" />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">네이버ID</label>
            <input type="text" className="w-full p-2 border rounded" />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">이름</label>
            <input type="text" className="w-full p-2 border rounded" />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">전화번호</label>
            <input type="tel" className="w-full p-2 border rounded" />
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">공사지역</label>
            <input type="text" className="w-full p-2 border rounded mb-2" />
            <div className="grid grid-cols-2 gap-2">
              <select className="p-2 border rounded">
                <option>광역지역 선택</option>
                <option>서울특별시</option>
                <option>경기도</option>
                <option>인천광역시</option>
              </select>
              <select className="p-2 border rounded">
                <option>시군구지역 선택</option>
                <option>강남구</option>
                <option>서초구</option>
                <option>송파구</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">공사예정일</label>
            <input type="date" className="w-full p-2 border rounded" />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">공사내용</label>
            <textarea className="w-full p-2 border rounded h-20"></textarea>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">견적의뢰 게시글</label>
            <input type="url" className="w-full p-2 border rounded mb-2" placeholder="견적의뢰 게시글 링크를 입력하세요" />
            <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
              <FileText className="w-4 h-4 inline mr-2" />
              견적의뢰 게시글 작성
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">작업자 (담당자)</label>
            <select className="w-full p-2 border rounded">
              <option>담당자를 선택하세요</option>
              <option>관리자1</option>
              <option>관리자2</option>
            </select>
          </div>
        </div>
      </div>

      <div className="mt-6 flex justify-end space-x-2">
        <button 
          onClick={() => setCurrentPage('list')}
          className="px-6 py-2 bg-gray-300 rounded hover:bg-gray-400"
        >
          취소
        </button>
        <button className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
          저장
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-xl font-bold text-gray-900">견적의뢰 관리 시스템</h1>
          </div>
        </div>
      </nav>

      {currentPage === 'list' && <QuoteListPage />}
      {currentPage === 'add' && <QuoteAddPage />}

      {showPostModal && <PostModal />}
      {showMessageModal && <MessageModal />}
      {showEditModal && <EditModal />}
      {showQuoteModal && <QuoteModal />}
      {showMemoModal && <MemoModal />}
      {showStatusModal && <StatusModal />}
    </div>
  );
};

export default QuoteManagementSystem;