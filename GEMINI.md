# GEMINI.MD: AI 협업 가이드

이 문서는 본 프로젝트와 상호작용하는 AI 모델을 위한 핵심 컨텍스트를 제공합니다. 이 가이드라인을 준수하면 일관성을 보장하고 코드 품질을 유지할 수 있습니다.

## 1. 프로젝트 개요 및 목적

* **주요 목표:** 복잡한 웹사이트를 탐색하는 사용자에게 개인화된 단계별 가이드를 제공하여 사용자 경험(UX)을 개선하고 이탈률을 줄이는 것을 목표로 합니다. 이 시스템은 성공적인 사용자 경로를 분석하여 신규 또는 어려움을 겪는 사용자에게 인터랙티브 가이드를 제공합니다.
* **비즈니스 도메인:** 사용자 경험 향상, 웹 분석, 행동 분석.

## 2. 핵심 기술 및 스택

* **언어:** JavaScript, Python
* **프레임워크 및 런타임:** 백엔드는 Node.js (Express 포함) 또는 Python (Flask 포함), 확장 프로그램 UI는 React 또는 Vue.js를 사용합니다.
* **데이터베이스:** MongoDB (유연한 이벤트 로깅용), PostgreSQL (분석 결과 등 정형 데이터용).
* **주요 라이브러리/의존성:** Pandas 및 Scikit-learn (데이터 분석용), JS Event Listeners (클라이언트 측 데이터 수집용).
* **패키지 매니저:** npm (모든 JavaScript 기반 구성요소용), pip (Python 분석 모듈용).

## 3. 아키텍처 패턴

* **전체 아키텍처:** 세 가지 주요 구성요소로 이루어진 클라이언트-서버 아키텍처:
    1.  **브라우저 확장 프로그램 (클라이언트):** 사용자 행동 데이터를 수집하고 가이드를 렌더링합니다.
    2.  **백엔드 서버:** 사용자 이벤트 로그를 수신하고 저장하는 API 서버입니다.
    3.  **데이터 분석 모듈:** 사용자 클러스터링 및 경로 분석을 위한 배치 처리 모듈입니다.
* **디렉토리 구조 철학:** 여러 구성요소를 관리하기 위해 모노레포 구조를 추론합니다:
    *   `/extension`: 브라우저 확장 프로그램 소스 코드 (React/Vue, content scripts, background scripts)를 포함합니다.
    *   `/server`: 백엔드 API 서버 코드 (Node.js/Express 또는 Python/Flask)를 포함합니다.
    *   `/analysis`: 데이터 분석 및 머신러닝을 위한 Python 스크립트를 포함합니다.
    *   `/docs`: PRD, SRS와 같은 프로젝트 문서를 포함합니다.

## 4. 코딩 컨벤션 및 스타일 가이드

* **포매팅:** 코드 스타일은 자동으로 강제됩니다. JavaScript/TypeScript에는 Prettier, Python에는 Black을 사용합니다. 주요 규칙으로는 2칸 들여쓰기와 최대 120자의 줄 길이가 있습니다.
* **이름 규칙:**
    *   `변수`, `함수`: JS는 `camelCase`, Python은 `snake_case`.
    *   `클래스`, `컴포넌트`: 모두 `PascalCase`.
    *   `파일`: `kebab-case` (예: `user-profile.js`).
* **API 디자인:** RESTful 원칙을 따릅니다. API 엔드포인트는 버전이 명시됩니다 (예: `/api/v1/...`). 표준 HTTP 동사를 사용합니다. 요청/응답 본문에는 JSON을 사용합니다.
* **오류 처리:** 모든 비동기 작업 (API 호출, DB 쿼리)은 `try...catch` 블록으로 감싸거나 프로미스 `.catch()` 핸들러를 사용해야 합니다.

## 5. 주요 파일 및 진입점

* **메인 진입점:**
    *   확장 프로그램: `extension/src/background.js` (이벤트 처리) 및 `extension/src/index.js` (UI 렌더링).
    *   서버: `server/index.js` 또는 `server/app.py`.
* **설정:**
    *   확장 프로그램: `extension/manifest.json` (권한 및 설정에 중요, SRS에 명시된 Manifest V3 규격 준수).
    *   서버 측: `/server` 및 `/analysis` 디렉토리의 `.env` 파일 (데이터베이스 자격증명 및 기타 비밀 정보용).
* **CI/CD 파이프라인:** 아직 정의되지 않았습니다. 테스트 및 린팅을 자동화하기 위해 워크플로우 파일 (예: `.github/workflows/main.yml`)을 생성해야 합니다.

## 6. 개발 및 테스트 워크플로우

* **로컬 개발 환경:** 각 구성요소 (`/extension`, `/server`, `/analysis`)는 자체 `package.json` 또는 `requirements.txt`를 가집니다. 각 디렉토리에서 `npm install` 또는 `pip install -r requirements.txt`를 실행하여 각 부분을 설정합니다.
* **테스트:** 모든 새로운 기능에는 단위 테스트가 동반되어야 합니다. `npm test` 또는 `pytest`를 통해 테스트를 실행합니다. `develop`에 병합하기 전에 크로스 브라우저 기능 (Chrome, Firefox)을 수동으로 확인해야 합니다.

## 7. AI 협업을 위한 특별 지침

* **기여 가이드라인:** 모든 개발은 `develop`에서 분기된 `feature/<feature-name>` 브랜치에서 수행해야 합니다. `develop`으로의 병합은 최소 한 번의 코드 리뷰가 포함된 Pull Request를 통해 이루어져야 합니다.
* **보안:** 보안에 유의하세요. 모든 데이터 전송은 HTTPS를 사용해야 합니다. 개인 식별 정보(PII)는 서버로 전송되기 *전에* 클라이언트 측에서 필터링하거나 익명화해야 합니다. 비밀 정보를 하드코딩하지 말고 `.env` 파일을 사용하세요.
* **의존성:** 새 의존성을 추가하려면 `npm install <package>` 또는 `pip install <package>`를 사용하고 해당 설정 파일 (`package.json` 또는 `requirements.txt`)을 업데이트하세요. Pull Request에서 새 의존성의 필요성을 정당화해야 합니다.