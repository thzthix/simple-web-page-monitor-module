# Web Page Change Monitor

## 1. 프로젝트 개요

이 프로젝트는 지정된 웹 페이지(로그인 페이지 등)의 HTML 소스 코드 변화를 주기적으로 감지하기 위한 간단한 파이썬 모듈입니다.

매일 스크립트를 실행하여 대상 페이지의 스냅샷을 생성하고, 이전 스냅샷과 비교하여 변경된 내용을 사용자에게 알려줍니다. 이를 통해 페이지의 위변조나 예기치 않은 변경을 신속하게 파악할 수 있습니다.

- **모니터링 대상 URL:** `https://mmbr.kyobobook.co.kr/login`

## 2. 핵심 기능 및 사용 기술

이 모듈은 단순한 텍스트 비교를 넘어, 보다 안정적이고 정확한 변경 감지를 위해 다음 기술들을 사용합니다.

- **데이터 저장:**
  - **SQLite:** 모든 스냅샷 기록을 단일 `snapshots.db` 파일에 저장하여 관리합니다. 각 기록은 타임스탬프, URL, HTML 해시, 원본 HTML, 그리고 추출된 핵심 요소를 포함합니다.
- **변경 감지 방식:**
  - **해시 비교:** 스크래핑한 HTML 콘텐츠의 `SHA256` 해시값을 계산하여 이전 해시값과 비교함으로써 전체 내용의 변경 여부를 빠르게 판단합니다.
  - **구체적 요소 분석:** `BeautifulSoup4`를 사용하여 페이지의 다양한 DOM 요소를 분석하고 비교합니다. 이를 통해 어떤 부분이 변경되었는지 구체적으로 파악할 수 있습니다.
- **주요 라이브러리:**
  - `requests`: 웹 페이지의 HTML을 가져옵니다.
  - `BeautifulSoup4`: HTML을 파싱하고 데이터를 추출합니다.
  - `sqlite3`, `hashlib`, `json`, `datetime`: 데이터베이스 연동, 해시 계산, 데이터 직렬화, 시간 기록 등 파이썬 기본 라이브러리를 활용합니다.

## 3. 변경사항 감지 요소

### 🔍 분석하는 HTML 요소들
모니터링 시스템은 다음 요소들의 변경을 구체적으로 감지합니다:

| 요소 | 설명 | 감지 내용 |
|------|------|-----------|
| **스크립트** | JavaScript 파일 | 추가/제거된 스크립트 파일 |
| **링크** | CSS, 리소스 파일 | 추가/제거된 CSS, 리소스 파일 |
| **이미지** | 이미지 파일 | 추가/제거된 이미지 |
| **페이지 제목** | `<title>` 태그 | 페이지 제목 변경 |
| **메타 태그** | SEO 메타데이터 | 메타 태그 변경 |
| **버튼** | 버튼 요소 | 버튼 추가/제거/수정 |
| **입력 필드** | 폼 입력 요소 | 입력 필드 변경 |
| **페이지 구조** | DIV 요소 | 레이아웃 구조 변경 |
| **폼** | 폼 요소 | 폼 구조 변경 |
| **기타 요소** | 기타 HTML 요소 | 위 요소들 외의 변경 |

### 📊 변경사항 기록 예시
```
변경 내용: 스크립트 변경; 링크(CSS/리소스) 변경; 페이지 제목 변경; 메타 태그 변경; 페이지 구조(DIV) 변경
```

## 4. 데이터베이스 저장 형태

### 📊 테이블 구조
스냅샷 데이터는 `snapshots` 테이블에 다음과 같은 구조로 저장됩니다:

```sql
CREATE TABLE snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 자동 증가 ID
    timestamp TEXT NOT NULL,               -- 스냅샷 생성 시간 (ISO 형식)
    url TEXT NOT NULL,                     -- 모니터링 대상 URL
    content_hash TEXT NOT NULL,            -- HTML 내용의 SHA256 해시값
    html_content TEXT NOT NULL,            -- 전체 HTML 내용 (원본)
    key_elements TEXT NOT NULL,            -- 추출된 핵심 요소들 (JSON 형태)
    change_detected BOOLEAN DEFAULT FALSE, -- 변경 감지 여부
    change_details TEXT                    -- 변경 상세 내용
)
```

### 💾 저장되는 데이터 예시
```json
{
  "timestamp": "2025-07-11T14:06:41.314879",
  "url": "https://mmbr.kyobobook.co.kr/login",
  "content_hash": "468caaf989b8ccbd3f2c...",
  "html_content": "<!DOCTYPE html><html>...</html>",  // 전체 HTML (약 46KB)
  "key_elements": {
    "forms": [],  // 폼 요소들
    "scripts": [  // 스크립트 태그들의 src 속성들
      "/assets/js/init.js",
      "/assets/js/vars.js",
      "https://contents.kyobobook.co.kr/resources/fo/js/common-vars.js?t=25710133734"
    ],
    "links": [    // 링크 태그들의 href 속성들
      // CSS 파일들, 기타 리소스들
    ],
    "images": [], // 이미지 파일들
    "titles": [], // 페이지 제목들
    "metas": [],  // 메타 태그들
    "buttons": [], // 버튼 요소들
    "inputs": [],  // 입력 필드들
    "divs_with_id": [] // ID가 있는 DIV 요소들
  }
}
```

### 🔍 저장 방식의 장점
1. **전체 HTML 보존**: 원본 HTML을 그대로 저장하여 필요시 전체 내용 확인 가능
2. **해시 기반 빠른 비교**: SHA256 해시로 전체 내용 변경 여부를 빠르게 판단
3. **구체적 요소 분석**: 다양한 HTML 요소를 분석하여 정확한 변경 내용 파악
4. **시간 기록**: 각 스냅샷의 정확한 생성 시간 기록

## 5. CSV 요약 보고서

### 📋 CSV 파일 구조
모니터링 결과는 `monitoring_report.csv` 파일에 다음과 같은 형태로 저장됩니다:

| 컬럼명 | 설명 |
|--------|------|
| 날짜 | 스냅샷 생성 날짜 (YYYY-MM-DD) |
| 시간 | 스냅샷 생성 시간 (HH:MM:SS) |
| URL | 모니터링 대상 URL |
| 변경감지 | 변경감지 여부 (변경감지/변경없음) |
| 변경내용 | 구체적인 변경 내용 (예: "스크립트 변경; 페이지 제목 변경") |
| HTML크기(문자) | HTML 파일의 크기 |
| 해시값(앞10자리) | SHA256 해시의 앞 10자리 |
| 스크립트수 | 페이지의 스크립트 태그 개수 |
| 링크수 | 페이지의 링크 태그 개수 |
| 폼수 | 페이지의 폼 태그 개수 |

### 📊 CSV 보고서 생성 방법

#### 자동 생성
- 매번 모니터링 실행 시 자동으로 CSV 파일이 업데이트됩니다.

#### 수동 생성
```bash
# 기존 데이터베이스에서 CSV 보고서 생성
py -3.11 generate_report.py
```

### 📈 CSV 보고서 활용
- **Excel/Google Sheets**: CSV 파일을 열어서 데이터 분석
- **통계 분석**: 변경 감지율, 트렌드 분석 등
- **보고서 작성**: 정기적인 모니터링 보고서 작성

## 6. 설정 및 설치

모듈을 실행하기 위해 필요한 파이썬 라이브러리를 설치해야 합니다.

```bash
pip install requests beautifulsoup4
```

## 7. 사용 방법

### 분석 모드 선택 (간단/상세)

이 모듈은 두 가지 분석 모드를 지원하며, 각 모드별로 별도의 CSV 보고서가 생성됩니다:

- **단순 모드 (기본값)**: 전체 HTML의 해시값만 비교하여 변경 여부만 판단합니다. (가장 빠르고 간단)
  - 결과는 `monitoring_report_simple.csv`에 저장됩니다.
  - 컬럼: 날짜, 시간, URL, 변경감지, 변경내용, HTML크기, 해시값(앞10자리)
- **상세 모드**: HTML을 파싱하여 각종 요소별로 변경 내역을 상세하게 분석합니다.
  - 결과는 `monitoring_report_detailed.csv`에 저장됩니다.
  - 컬럼: 날짜, 시간, URL, 변경감지, 변경내용, HTML크기, 해시값(앞10자리), 스크립트수, 링크수, 폼수, 이미지수, 제목수, 메타태그수, 버튼수, 입력필드수, DIV수

#### 실행 예시

```bash
# 단순(해시) 비교 모드 (기본값)
py -3.11 monitor.py

# 상세 분석 모드
py -3.11 monitor.py --mode detailed

# 명시적으로 단순 모드 실행
py -3.11 monitor.py --mode simple
```

- **단순 모드**는 전체 HTML이 바뀌었는지 아닌지만 빠르게 감지하며, 최소 정보만 기록합니다.
- **상세 모드**는 어떤 요소가 바뀌었는지까지 구체적으로 알려주고, 모든 요소별 개수를 기록합니다.

### 수동 실행
1.  프로젝트 디렉토리(`web_page_monitor`)로 이동합니다.
2.  다음 명령어를 사용하여 파이썬 스크립트를 실행합니다.

    ```bash
    # Windows
    py -3.11 monitor.py

    # macOS / Linux
    python3 monitor.py
    ```

### 자동 실행 설정 (매일 1회)

#### 방법 1: Windows 작업 스케줄러 (추천)

1. **작업 스케줄러 열기**
   - `Win + R` → `taskschd.msc` 입력
   - 또는 검색에서 "작업 스케줄러" 검색

2. **새 작업 만들기**
   - 오른쪽 패널에서 "작업 만들기" 클릭
   - 이름: "웹페이지 모니터링"
   - "가장 높은 수준의 권한으로 실행" 체크

3. **트리거 설정**
   - "트리거" 탭 → "새로 만들기"
   - "매일" 선택
   - 시작 시간 설정 (예: 오전 9시)
   - "사용" 체크

4. **동작 설정**
   - "동작" 탭 → "새로 만들기"
   - 동작: "프로그램 시작"
   - 프로그램/스크립트: `C:\Users\KICO\web_page_monitor\run_monitor.bat`
   - 시작 위치: `C:\Users\KICO\web_page_monitor`

5. **조건 설정**
   - "조건" 탭에서 필요시 설정 조정
   - "네트워크 연결이 가능한 경우에만 작업 시작" 체크 권장

#### 방법 2: PowerShell 스크립트 (고급 사용자)

```powershell
# PowerShell을 관리자 권한으로 실행 후
.\schedule_monitor.ps1
```

-   **최초 실행 시:** `snapshots.db` 파일이 생성되고, 페이지의 첫 번째 스냅샷이 데이터베이스에 저장됩니다.
-   **두 번째 실행부터:** 현재 페이지 상태를 가장 최근에 저장된 스냅샷과 비교하고, 변경 사항이 있을 경우 상세 내역을 터미널에 출력합니다. 이후 현재 상태를 새로운 스냅샷으로 DB에 저장합니다.

## 8. 로그 및 알림

### 로그 파일
- 모든 실행 기록은 `monitor.log` 파일에 저장됩니다
- 콘솔과 파일에 동시에 로그가 기록됩니다

### 변경사항 알림
- 변경사항이 감지되면 상세한 로그와 함께 알림이 표시됩니다
- 구체적으로 어떤 요소가 변경되었는지 명확하게 표시됩니다
- 현재는 로그 기반 알림만 제공 (이메일, 슬랙 등 추가 가능)

## 9. 프로젝트 구조

### 📁 모듈화된 파일 구조
프로젝트는 기능별로 모듈화되어 있어 유지보수가 용이합니다:

```
web_page_monitor/
│
├── monitor.py              # 메인 스크립트 (모니터링 실행)
├── config.py               # 설정 파일 (URL, 경로, 알림 설정 등)
├── database.py             # 데이터베이스 관리 모듈
├── html_analyzer.py        # HTML 분석 모듈
├── csv_reporter.py         # CSV 보고서 모듈
├── generate_report.py      # CSV 보고서 생성 스크립트
├── run_monitor.bat         # Windows 배치 파일 (자동 실행용)
├── schedule_monitor.ps1    # PowerShell 스케줄링 스크립트
├── snapshots.db            # SQLite 데이터베이스 파일
├── monitoring_report.csv   # CSV 요약 보고서 파일
├── monitor.log             # 실행 로그 파일
├── .gitignore              # Git 무시 파일 목록
└── README.md               # 프로젝트 설명 파일
```

### 🔧 모듈별 기능

| 모듈 | 기능 | 설명 |
|------|------|------|
| **monitor.py** | 메인 실행 | 전체 모니터링 프로세스 조정 |
| **config.py** | 설정 관리 | URL, 경로, 알림 설정 등 중앙 관리 |
| **database.py** | 데이터베이스 관리 | SQLite DB 생성, 저장, 조회 |
| **html_analyzer.py** | HTML 분석 | 웹페이지 스크래핑, 요소 추출, 비교 |
| **csv_reporter.py** | CSV 보고서 | CSV 파일 생성 및 관리 |
| **generate_report.py** | 보고서 생성 | 기존 데이터에서 CSV 보고서 생성 |

### ⚙️ 설정 파일 (config.py)

모든 설정은 `config.py` 파일에서 중앙 관리됩니다:

```python
# 모니터링 대상 URL
TARGET_URL = "https://mmbr.kyobobook.co.kr/login"

# 파일 경로 설정
LOG_FILE = "monitor.log"
DATABASE_FILE = "snapshots.db"
CSV_REPORT_FILE = "monitoring_report.csv"

# 모니터링 요소 우선순위
MONITORING_PRIORITY = [
    ElementType.TITLES,      # 페이지 제목 변경
    ElementType.FORMS,       # 폼 구조 변경
    ElementType.INPUTS,      # 입력 필드 변경
    # ... 기타 요소들
]

# 알림 설정
ENABLE_EMAIL_NOTIFICATIONS = False
ENABLE_SLACK_NOTIFICATIONS = False
ENABLE_TELEGRAM_NOTIFICATIONS = False
```

## 10. TODO 및 향후 개선사항

### 🔄 동적 요소 제거 기능 (TODO)
현재는 모든 HTML 요소를 분석하지만, 향후 다음 동적 요소들을 제거하여 의미있는 변경만 감지하도록 개선할 예정입니다:

- **광고 스크립트 제거**: Google Analytics, Facebook Pixel 등
- **타임스탬프 제거**: 시간 관련 요소들
- **랜덤 토큰 제거**: 세션 토큰, CSRF 토큰 등
- **CSS 클래스 난독화 제거**: 빌드 시 생성되는 해시 클래스

### 📧 알림 기능 확장 (TODO)
- 이메일 알림 기능
- Slack 웹훅 알림
- Telegram 봇 알림

### 🔧 추가 개선사항
- 다중 URL 모니터링 지원
- 웹 대시보드 제공
- 변경사항 히스토리 시각화
- 성능 최적화
