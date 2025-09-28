// Google Apps Script 코드
// 구글 시트의 확장 프로그램 > Apps Script에 복사해서 사용하세요

function onFormSubmit(e) {
  // 활성 시트 가져오기
  var sheet = SpreadsheetApp.getActiveSheet();
  var lastRow = sheet.getLastRow();

  // 마지막 행의 데이터 가져오기
  var rowData = sheet.getRange(lastRow, 1, 1, sheet.getLastColumn()).getValues()[0];

  // 데이터 매핑 (구글 폼 순서에 맞게 조정 필요)
  var payload = {
    "sTimeStamp": rowData[0] || "",
    "sCompanyName": rowData[1] || "",
    "sPhone": rowData[2] || "",
    "sConMoney": rowData[3] || "",
    "sArea": rowData[4] || "",
    "sS1": rowData[5] || "보통",
    "sS2": rowData[6] || "보통",
    "sS3": rowData[7] || "보통",
    "sS4": rowData[8] || "보통",
    "sS5": rowData[9] || "보통",
    "sS6": rowData[10] || "보통",
    "sS7": rowData[11] || "보통",
    "sS8": rowData[12] || "보통",
    "sS9": rowData[13] || "보통",
    "sS10": rowData[14] || "보통",
    "sS11": rowData[15] || ""
  };

  // HTTP 요청 옵션 설정
  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "headers": {
      "Authorization": "Bearer testpark-google-sheets-webhook-2024"
    },
    "muteHttpExceptions": true // 오류 발생시에도 응답 받기
  };

  try {
    // Webhook URL (localtunnel 사용)
    var response = UrlFetchApp.fetch(
      "https://testpark-webhook.loca.lt/evaluation/webhook/google-sheets/",
      options
    );

    // 응답 확인
    var responseCode = response.getResponseCode();
    var responseText = response.getContentText();

    console.log("Response Code: " + responseCode);
    console.log("Response: " + responseText);

    // 성공 여부 로그
    if (responseCode == 200) {
      console.log("데이터 전송 성공!");
    } else {
      console.log("데이터 전송 실패: " + responseCode);
    }

  } catch (error) {
    console.error("에러 발생:", error.toString());
  }
}

// 테스트 함수
function testWebhook() {
  // 테스트 데이터
  var testData = {
    "sTimeStamp": "2024. 12. 26. 오후 3:30:45",
    "sCompanyName": "테스트 업체",
    "sPhone": "010-1234-5678",
    "sConMoney": "1000000",
    "sArea": "서울시 강남구",
    "sS1": "매우 만족",
    "sS2": "만족",
    "sS3": "보통",
    "sS4": "만족",
    "sS5": "매우 만족",
    "sS6": "만족",
    "sS7": "보통",
    "sS8": "만족",
    "sS9": "매우 만족",
    "sS10": "만족",
    "sS11": "테스트 추가 의견입니다."
  };

  var options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(testData),
    "headers": {
      "Authorization": "Bearer testpark-google-sheets-webhook-2024"
    },
    "muteHttpExceptions": true
  };

  try {
    var response = UrlFetchApp.fetch(
      "https://testpark-webhook.loca.lt/evaluation/webhook/google-sheets/",
      options
    );

    console.log("테스트 응답:", response.getContentText());

  } catch (error) {
    console.error("테스트 실패:", error.toString());
  }
}

// 트리거 설정 함수
function setupTrigger() {
  // 기존 트리거 삭제
  var triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(trigger) {
    if (trigger.getHandlerFunction() == "onFormSubmit") {
      ScriptApp.deleteTrigger(trigger);
    }
  });

  // 새 트리거 생성 (폼 제출시)
  ScriptApp.newTrigger("onFormSubmit")
    .forSpreadsheet(SpreadsheetApp.getActiveSpreadsheet())
    .onFormSubmit()
    .create();

  console.log("트리거 설정 완료!");
}