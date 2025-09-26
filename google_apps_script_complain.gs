// Google Apps Script - 고객불만(Complain) 전용
// 고객불만 구글 시트에서 사용

function onFormSubmit(e) {
  try {
    console.log("고객불만 onFormSubmit 시작");

    var sheet = SpreadsheetApp.getActiveSheet();
    var lastRow = sheet.getLastRow();

    if (lastRow < 2) {
      console.log("데이터가 없습니다");
      return;
    }

    // 마지막 행 데이터 가져오기
    var rowData = sheet.getRange(lastRow, 1, 1, sheet.getLastColumn()).getValues()[0];
    console.log("읽은 데이터:", rowData);

    // 고객불만 데이터 매핑
    // 구글 시트 컬럼 순서에 맞게 조정 필요
    var payload = {
      sTimeStamp: String(rowData[0] || ""),
      sCompanyName: String(rowData[1] || ""),
      sPass: String(rowData[2] || ""),
      sComplain: String(rowData[3] || ""),
      sComplainPost: String(rowData[4] || ""),
      sPost: String(rowData[5] || ""),
      sSMSBool: String(rowData[6] || ""),
      sSMSMent: String(rowData[7] || ""),
      sFile: String(rowData[8] || ""),
      sCheck: String(rowData[9] || ""),
      sWorker: String(rowData[10] || ""),
      fComplain: String(rowData[11] || "0")
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

    // Webhook URL - 고객불만 전용 엔드포인트
    var url = "https://testpark-webhook.loca.lt/evaluation/webhook/google-sheets-complain/";

    // 요청 전송
    var response = UrlFetchApp.fetch(url, options);
    var responseCode = response.getResponseCode();
    var responseText = response.getContentText();

    console.log("응답 코드:", responseCode);
    console.log("응답 내용:", responseText);

    if (responseCode == 200) {
      console.log("✅ 고객불만 데이터 전송 성공!");
    } else {
      console.error("❌ 고객불만 데이터 전송 실패:", responseCode, responseText);
    }

  } catch (error) {
    console.error("오류 발생:", error.toString());
    console.error("스택:", error.stack);
  }
}

// 수동 테스트 함수
function testComplainWebhook() {
  console.log("고객불만 수동 테스트 시작");

  var testPayload = {
    sTimeStamp: new Date().toLocaleString("ko-KR"),
    sCompanyName: "테스트업체",
    sPass: "전화",
    sComplain: "시공 불만족 테스트",
    sComplainPost: "https://example.com/post",
    sPost: "테스트 의뢰글",
    sSMSBool: "발송",
    sSMSMent: "고객님께 SMS를 발송했습니다",
    sFile: "file.pdf",
    sCheck: "확인",
    sWorker: "박세욱",
    fComplain: "5.0"
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
    var url = "https://testpark-webhook.loca.lt/evaluation/webhook/google-sheets-complain/";
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
function setupComplainTrigger() {
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

  console.log("✅ 고객불만 트리거 설정 완료!");
}

// 시트 데이터 확인
function checkComplainSheetData() {
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