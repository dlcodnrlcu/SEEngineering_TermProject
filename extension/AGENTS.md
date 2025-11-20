# Agent 요약: extension

## 1. 책임
`extension` 모듈은 웹 페이지에서 익명화된 사용자 상호작용 데이터(특히 클릭)를 수집하고, 이 수집에 대한 사용자 동의를 관리하며, 데이터를 로컬에 버퍼링하고, 주기적으로 구성된 백엔드 서버에 일괄 업로드하는 역할을 하는 크롬 확장 프로그램입니다.

## 2. 입력 / 출력
### 입력
- 웹 페이지에서의 사용자 `click` 이벤트.
- 동의 페이지와의 사용자 상호작용 ("동의" / "비동의").
- 확장 프로그램 설치 이벤트.
- 예약된 작업을 위한 크롬 알람 이벤트.
- 로그 업로드를 위한 백엔드 API 응답.
### 출력
- `background.js` 스크립트로 전송된 익명화된 클릭 이벤트 데이터.
- `chrome.storage.local`에 저장된 동의 상태.
- `chrome.storage.local`에 저장된 버퍼링된 로그 데이터.
- `http://127.0.0.1:5000/api/v1/log_batch`로 전송된 HTTP POST 요청 (로그 데이터 배치).
- 크롬 `console.log` 및 `console.error` 메시지.
- `consent.html` 페이지 열기.

## 3. 내부 구조
- 주요 클래스/함수 목록:
    - `background.js`:
        - `LOG_BUFFER_KEY`, `CONSENT_KEY`, `UPLOAD_ALARM_NAME` (상수)
        - `chrome.runtime.onInstalled.addListener` (이벤트 리스너)
        - `chrome.runtime.onMessage.addListener` (이벤트 리스너)
        - `chrome.alarms.onAlarm.addListener` (이벤트 리스너)
        - `sendBufferedLogs()` (함수)
    - `content.js`:
        - `CONSENT_KEY` (상수)
        - `document.body.addEventListener('click', ...)` (이벤트 리스너)
    - `consent.js`:
        - `document.getElementById('agree').addEventListener('click', ...)` (이벤트 리스너)
        - `document.getElementById('disagree').addEventListener('click', ...)` (이벤트 리스너)
    - `manifest.json`: 설정 파일.
    - `consent.html`, `popup.html`: 사용자 인터페이스 파일.
- 대표적 실행 흐름(sequence of operations):
    1.  **설치/동의:** 설치 시 `background.js`가 동의 여부를 확인합니다. 동의하지 않은 경우 `consent.html`이 열립니다. 사용자는 `consent.js`를 통해 `consent.html`과 상호작용하여 로컬 저장소에 `hasConsented`를 설정합니다.
    2.  **데이터 수집:** `content.js`는 모든 페이지에서 클릭을 수신합니다. `hasConsented`가 true이면 클릭 데이터를 캡처하여 `background.js`에 메시지로 보냅니다.
    3.  **데이터 버퍼링 및 업로드:** `background.js`는 클릭 데이터를 수신하고 `hasConsented`를 확인한 후 로컬 저장소에 버퍼링합니다. 알람이 주기적으로 `sendBufferedLogs()`를 트리거합니다. `sendBufferedLogs()`는 버퍼링된 데이터를 검색하고 `hasConsented`인 경우 `fetch`를 통해 백엔드로 보냅니다. 성공 시 버퍼가 지워집니다.

## 4. 의존성
- 내부 모듈:
    - `background.js`는 들어오는 메시지에 대해 `content.js`에 의존하고 동의 상태에 대해 `consent.js`/`consent.html`에 의존합니다.
    - `content.js`는 메시지 전달을 위해 `background.js`에 의존합니다.
    - `consent.js`는 DOM 요소에 대해 `consent.html`에 의존합니다.
- 외부 모듈:
    - 크롬 확장 API: `chrome.storage`, `chrome.runtime`, `chrome.tabs`, `chrome.alarms`.
    - 웹 API: HTTP 요청을 위한 `fetch`, `document.body.addEventListener`.

## 5. 검사 결과 (체크리스트 기반)
- 기능적 결함:
    - 백엔드 API `log_batch`가 데이터를 올바르게 처리한다고 가정할 때 핵심 기능에서 확인된 결함 없음.
- 설계적 결함:
    - `background.js`에 하드코딩된 백엔드 URL (`http://127.0.0.1:5000/api/v1/log_batch`). 이로 인해 다른 배포 환경에 대한 쉬운 구성이 방해됩니다.
    - `content.js`는 `event.target.textContent`를 캡처하는데, 이는 잘려도 PII 필터링/익명화에 대한 프롬프트의 강조를 감안할 때 캡처 전에 신중하게 익명화하거나 필터링하지 않으면 개인 식별 정보(PII)를 포함할 수 있습니다.
- 유지보수 리스크:
    - 확장 프로그램의 로직에 대한 단위 테스트가 없어 리팩토링이나 새로운 기능 개발이 위험합니다.
    - 실패한 업로드에 대한 `console.error` 이상의 제한된 오류 보고/복구.
- 프로토타입 흔적:
    - `consent.html` 및 `popup.html`의 기본 UI는 초기 구현임을 시사합니다.
    - 하드코딩된 백엔드 URL.
    - 클릭 이벤트만 캡처합니다. 다른 상호작용 유형(스크롤, 양식 입력, 페이지 변경)은 아직 구현되지 않았습니다.
- 추천 리팩터링:
    - 백엔드 API URL을 구성 가능한 설정(예: 엔터프라이즈 정책의 경우 `chrome.storage.managed` 또는 간단한 옵션 페이지)으로 외부화합니다.
    - 백엔드 통신 실패에 대한 보다 강력한 오류 처리 및 보고 메커니즘을 구현합니다.
    - `content.js`에서 `textContent` 캡처에 대한 PII 삭제/익명화를 강화하거나 수집되는 `textContent`에 대한 명확한 정책을 제공합니다.
    - 설치 후 사용자가 동의 상태 및 기타 설정을 관리할 수 있도록 옵션 페이지를 추가하는 것을 고려합니다.

## 6. 테스트 용이성
- 테스트 전략 또는 실행 방법:
    - `chrome.storage.local` 및 네트워크 요청을 검사하여 설치 흐름, 동의, 클릭 로깅 및 데이터 업로드에 대한 수동 테스트.
    - 자동화된 테스트의 경우 Puppeteer 또는 Selenium과 같은 프레임워크를 사용하여 사용자 상호작용을 시뮬레이션하고 확장 프로그램 동작을 확인할 수 있지만 상당한 설정이 필요합니다. 순수 자바스크립트 함수(추출된 경우)에 대한 단위 테스트는 구현하기가 더 쉽습니다.