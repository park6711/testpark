// Google Apps Script - 고객만족도(Satisfy) 전용
// 고객불만과 동일한 스타일로 수정

function onFormSubmit(e) {
  try {
    console.log("고객만족도 onFormSubmit 시작");

    var sheet = SpreadsheetApp.getActiveSheet();
    var lastRow = sheet.getLastRow();

    if (lastRow < 2) {
      console.log("데이터가 없습니다");
      return;
    }

    // 마지막 행 데이터 가져오기
    var rowData = sheet.getRange(lastRow, 1, 1, sheet.getLastColumn()).getValues()[0];
    console.log("읽은 데이터:", rowData);

    // 고객만족도 데이터 매핑
    // 구글 시트 컬럼 순서에 맞게 조정 필요
    var payload = {
      sTimeStamp: String(rowData[0] || ""),
      sCompanyName: String(rowData[1] || ""),
      sPhone: String(rowData[2] || ""),
      sConMoney: String(rowData[3] || ""),
      sArea: String(rowData[4] || ""),
      sS1: String(rowData[5] || "보통"),
      sS2: String(rowData[6] || "보통"),
      sS3: String(rowData[7] || "보통"),
      sS4: String(rowData[8] || "보통"),
      sS5: String(rowData[9] || "보통"),
      sS6: String(rowData[10] || "보통"),
      sS7: String(rowData[11] || "보통"),
      sS8: String(rowData[12] || "보통"),
      sS9: String(rowData[13] || "보통"),
      sS10: String(rowData[14] || "보통"),
      sS11: String(rowData[15] || "")
    };

    console.log("전송할 데이터:", JSON.stringify(payload));

    // HTTP 옵션
    var options = {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload),
      headers: {
        "Authorization": "Bearer testpark-google-sheets-webhook-2024",
        "Content-Type": "application/json"
      },
      muteHttpExceptions: true
    };

    // Webhook URL - 고객만족도 전용 엔드포인트
    var url = "https://testpark-webhook.loca.lt/evaluation/webhook/google-sheets/";

    // 요청 전송
    var response = UrlFetchApp.fetch(url, options);
    var responseCode = response.getResponseCode();
    var responseText = response.getContentText();

    console.log("응답 코드:", responseCode);
    console.log("응답 내용:", responseText);

    if (responseCode == 200) {
      console.log("✅ 고객만족도 데이터 전송 성공!");
    } else {
      console.error("❌ 고객만족도 데이터 전송 실패:", responseCode, responseText);
    }

  } catch (error) {
    console.error("오류 발생:", error.toString());
    console.error("스택:", error.stack);
  }
}

// 수동 테스트 함수
function testSatisfyWebhook() {
  console.log("고객만족도 수동 테스트 시작");

  var testPayload = {
    sTimeStamp: new Date().toLocaleString("ko-KR"),
    sCompanyName: "테스트업체",
    sPhone: "010-1234-5678",
    sConMoney: "1,000,000원",
    sArea: "서울시 강남구",
    sS1: "매우 만족",
    sS2: "만족",
    sS3: "보통",
    sS4: "만족",
    sS5: "매우 만족",
    sS6: "만족",
    sS7: "보통",
    sS8: "만족",
    sS9: "매우 만족",
    sS10: "만족",
    sS11: "테스트 추가의견입니다"
  };

  var options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(testPayload),
    headers: {
      "Authorization": "Bearer testpark-google-sheets-webhook-2024",
      "Content-Type": "application/json"
    },
    muteHttpExceptions: true
  };

  try {
    var url = "https://testpark-webhook.loca.lt/evaluation/webhook/google-sheets/";
    var response = UrlFetchApp.fetch(url, options);

    console.log("응답 코드:", response.getResponseCode());
    console.log("응답 내용:", response.getContentText());

    if (response.getResponseCode() == 200) {
      console.log("✅ 테스트 성공!");
    } else {
      console.log("❌ 테스트 실패");
    }
  } catch (error) {
    console.error("테스트 오류:", error.toString());
  }
}

// 트리거 설정
function setupSatisfyTrigger() {
  // 기존 트리거 제거
  var triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(trigger) {
    if (trigger.getHandlerFunction() == "onFormSubmit") {
      ScriptApp.deleteTrigger(trigger);
      console.log("기존 트리거 삭제됨");
    }
  });

  // 새 트리거 생성
  ScriptApp.newTrigger("onFormSubmit")
    .forSpreadsheet(SpreadsheetApp.getActiveSpreadsheet())
    .onFormSubmit()
    .create();

  console.log("✅ 고객만족도 트리거 설정 완료!");
}

// 시트 데이터 확인
function checkSatisfySheetData() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var lastRow = sheet.getLastRow();

  console.log("현재 행 수:", lastRow);

  if (lastRow >= 2) {
    var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    console.log("헤더:", headers);

    var lastRowData = sheet.getRange(lastRow, 1, 1, sheet.getLastColumn()).getValues()[0];
    console.log("마지막 행 데이터:");
    for (var i = 0; i < lastRowData.length; i++) {
      console.log("  컬럼 " + (i+1) + ": " + lastRowData[i]);
    }
  }
}