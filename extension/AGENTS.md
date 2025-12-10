# Agent 요약: Extension

## 1. 책임 (Responsibility)
이 에이전트는 "Follow Me!" 시스템의 클라이언트 측 데이터 수집기 및 사용자 인터페이스 역할을 하는 Chrome 브라우저 확장 프로그램입니다. 사용자 상호작용을 기록하고, 분석을 위해 백엔드로 전송하며, 분석 결과를 기반으로 웹 페이지에 내비게이션 가이드를 표시합니다.

## 2. 입력 / 출력 (Inputs / Outputs)
### 입력
- **사용자 행동**: 클릭, 양식 입력, 스크롤, 페이지 이동.
- **서버 API (GET `/api/v1/guide`)**: 현재 URL에 대한 JSON 기반 가이드 데이터를 수신합니다.
- **브라우저 저장소 (`chrome.storage.local`)**: 사용자 동의 상태, 세션 ID, 가이드 활성화 설정을 읽습니다.

### 출력
- **서버 API (POST `/api/v1/log_batch`)**: 수집된 사용자 상호작용 로그 배치를 JSON 배열로 전송합니다.
- **DOM 조작**: 가이드를 위한 시각적 오버레이(하이라이트 상자 및 툴팁)를 생성하기 위해 HTML 및 CSS를 주입합니다.
- **브라우저 저장소 (`chrome.storage.local`)**:
  - **쓰기**: 전송 전 로그 데이터를 버퍼링하고, 팝업에서 설정한 사용자 설정을 저장합니다.

## 3. 내부 구조 (Internal Structure)
- **`manifest.json`**: 권한(storage, scripting, alarms), API에 대한 호스트 권한, 스크립트 진입점을 정의하는 핵심 구성 파일입니다.
- **`background.js` (서비스 워커)**:
  - 로그 데이터에 대한 영구 버퍼를 관리합니다.
  - `chrome.alarms`를 사용하여 버퍼링된 데이터를 주기적으로 백엔드 API로 전송합니다.
  - 설치 시 고유한 세션 ID를 생성합니다.
- **`content.js`**:
  - 모든 웹 페이지에 주입됩니다.
  - 사용자 이벤트(클릭, 입력, 스크롤) 및 페이지 전환을 캡처합니다.
  - 로깅 전 민감한 데이터를 삭제하기 위해 PII 마스킹을 구현합니다.
  - 서버에서 가이드를 가져와 `GuideManager` UI를 렌더링합니다.
- **`popup.html` / `popup.js` / `popup.css`**: 가이드 표시를 활성화 또는 비활성화하는 토글을 포함하여 브라우저 액션 팝업을 위한 UI를 제공합니다.
- **`consent.html` / `consent.js`**: 데이터 수집에 대한 사용자 동의를 요청하는 일회성 페이지입니다.

## 4. 의존성 (Dependencies)
### 내부 모듈
- `content.js`는 `chrome.runtime` API를 사용하여 `background.js`로 메시지를 보냅니다.
- `popup.js`는 `chrome.storage.local`에 기록하여 `content.js`의 동작을 수정합니다.

### 외부 모듈
- **백엔드 서버**: 현재 `http://127.0.0.1:5000`으로 하드코딩된 서버의 `/api/v1/log_batch` 및 `/api/v1/guide` 엔드포인트에 의존합니다.

## 5. 검사 결과 (Inspection Findings)
- **기능적 결함**: 백엔드 서버가 다운되면 버퍼링된 로그가 지워지지 않아 반복적인 전송 실패가 발생합니다. 백오프(backoff)가 있는 재시도 로직이 없습니다.
- **설계 결함**:
  - SPA 내비게이션이 비효율적인 `setInterval`을 통해 감지됩니다. 최신 Navigation API를 사용하는 것이 더 나은 선택입니다.
  - `GuideManager`가 DOM을 직접 조작하여 일부 웹 애플리케이션(예: React 앱)과 충돌할 수 있습니다.
- **유지보수 리스크**:
  - 백엔드 서버 URL이 `background.js`와 `content.js` 모두에 하드코딩되어 있어 다른 환경에 맞게 변경하기 어렵습니다.
- **프로토타입 흔적**:
  - PII 마스킹이 간단한 정규식에 기반하며 포괄적이지 않습니다.
  - 코드 전반에 `console.log` 문이 존재합니다.
  - 알람 주기가 개발용으로 1분으로 설정되어 있습니다.
- **추천 리팩터링**:
  - 하드코딩된 API URL을 중앙 구성 위치로 이동합니다.
  - `setInterval` URL 확인을 Navigation API 또는 `popstate` 및 `hashchange` 이벤트를 수신하여 대체합니다.
  - 스타일 충돌을 피하기 위해 가이드 UI의 모든 DOM 조작을 Shadow DOM 내에 캡슐화합니다.

## 6. 테스트 용이성 (Testability)
- **수동 테스트**: 브라우저에 확장 프로그램을 로드하고 웹사이트를 방문하면서 백엔드 서버를 로컬에서 실행해야 합니다.
- **자동화 테스트**:
  - 스크립트 내 로직은 Jest와 같은 프레임워크와 모의 Chrome API 라이브러리(`jest-chrome` 등)를 결합하여 단위 테스트할 수 있습니다.
  - 엔드투엔드 테스트는 Puppeteer나 Selenium과 같은 브라우저 자동화 프레임워크로 달성할 수 있습니다.