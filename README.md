# 간이 웹페이지 변경 모니터

교보문고 엠앤비알(M&BR) 로그인 페이지의 변조를 감지하는 모니터링 시스템입니다.

## 🚀 주요 기능

### 1. 내용 기반 변경 감지
- **동적 요소 필터링**: CSS 해시, 타임스탬프 등 무의미한 변경 무시
- **실제 내용 변경 감지**: HTML 구조와 텍스트 내용의 실제 변경만 감지
- **악의적 스크립트 감지**: 악의적인 JavaScript 코드 삽입 탐지

### 2. 구체적 변경사항 분석
- 스크립트 태그 추가/수정
- 외부 링크 추가
- 폼 구조 변경
- 의심스러운 JavaScript 코드 (`eval`, `document.write` 등)

### 3. 데이터 저장
- SQLite 데이터베이스에 스냅샷 저장
- CSV 보고서 생성
- 상세한 로그 기록

## 📁 파일 구조

```
simple-web-page-monitor-module/
├── monitor.py              # 메인 모니터링 로직
├── simple_compare.py       # HTML 비교 및 악의적 변경 감지
├── fetcher.py             # 웹페이지 가져오기
├── database.py            # 데이터베이스 관리
├── csv_report.py          # CSV 보고서 생성
├── logger.py              # 로깅 설정
├── config.py              # 운영용 설정 파일
├── config_prod.py         # 프로덕션 설정 백업
├── config_test.py         # 테스트용 설정 파일
├── simple_test.py         # ⭐ 변조 감지 테스트 스크립트
└── README.md              # 이 파일
```

## 🛠️ 설치 및 실행

### 1. 의존성 설치
```bash
pip install requests beautifulsoup4
```

### 2. 기본 모니터링 실행
```bash
python monitor.py
```

### 3. 변조 감지 테스트 실행 (필수)
```bash
# 변조 감지 시스템 테스트
python simple_test.py
```

**⚠️ 중요: 시스템을 테스트하려면 반드시 위 테스트 스크립트를 실행해야 합니다!**

## 🧪 변조 감지 테스트

### ⭐ simple_test.py 실행
```bash
# 변조 감지 시스템 테스트
python simple_test.py
```

`simple_test.py`는 변조 감지 시스템을 쉽게 테스트할 수 있는 스크립트입니다:

**🔍 동작 과정:**
1. 교보문고 로그인 페이지 원본 다운로드
2. 3가지 변조 버전 자동 생성 (URL 변조, 악성 스크립트, 텍스트 변조)
3. 로컬 HTTP 서버 자동 시작
4. 변조 감지 로직 테스트 및 결과 출력
5. 상세한 로그 파일 생성 (`simple_test.log`)

**📊 핵심 코드 설명:**
```python
# 해시 계산으로 변경 감지
original_hash = hashlib.sha256(original_html.encode('utf-8')).hexdigest()
modified_hash = hashlib.sha256(modified_html.encode('utf-8')).hexdigest()

# 변조 감지 로직 실행
changed = is_html_changed(original_html, modified_html)

# 결과 로깅
log_message = f"[변조유형] 원본해시: {original_hash[:16]}..., 변조해시: {modified_hash[:16]}..., 감지결과: {changed}"
```

### 📁 테스트 실행 시 생성되는 파일들:
- `kyobo_login_original.html`: 원본 교보문고 로그인 페이지
- `kyobo_login_url_modified.html`: URL 변조 버전
- `kyobo_login_script_modified.html`: 악성 스크립트 추가 버전  
- `kyobo_login_text_modified.html`: 텍스트 변조 버전
- `simple_test.log`: 상세한 테스트 로그

### 테스트 시나리오
1. **URL 변조**: 교보문고 URL을 악의적 사이트로 변경
2. **악성 스크립트**: 키로거 등 악성 JavaScript 코드 삽입
3. **텍스트 변조**: "교보문고" → "가짜문고" 등 텍스트 변경

## 📊 결과 확인

### 운영용 파일들
- `monitor.log`: 상세한 모니터링 로그
- `snapshots_monitor.db`: SQLite 데이터베이스
- `monitoring_report_simple.csv`: 요약 보고서

### 테스트용 파일들
- `simple_test.log`: 테스트 실행 로그
- `kyobo_login_*.html`: 테스트용 HTML 파일들

### 데이터베이스
- 스냅샷 테이블: 타임스탬프, URL, 해시, HTML 내용, 변경 여부

### CSV 보고서
- 컬럼: 날짜, 시간, URL, 변경감지, 변경내용, HTML크기, 해시값

## 🔧 설정

### config.py (운영용)
```python
TARGET_URL = "https://mmbr.kyobobook.co.kr/login"  # 모니터링 대상
LOG_FILE = "monitor.log"                            # 로그 파일
DATABASE_PATH = "snapshots_monitor.db"              # 데이터베이스 파일
CSV_REPORT_SIMPLE = "monitoring_report_simple.csv"  # CSV 보고서
```

### config_test.py (테스트용)
```python
TARGET_URL = "http://localhost:8000/original.html"  # 테스트 대상
LOG_FILE = "test_monitor.log"                       # 테스트 로그 파일
DATABASE_PATH = "test_snapshots_monitor.db"         # 테스트 데이터베이스
CSV_REPORT_SIMPLE = "test_monitoring_report_simple.csv"  # 테스트 CSV
```

## 🚨 변경 감지 로직

### 1. 내용 기반 비교
- 외부 CSS 링크 제거 (내부 스타일은 유지)
- 일부 meta 태그 제거 (viewport, generator)
- 동적 data 속성 제거 (보안 관련은 유지)
- 공백 정리 (의미있는 공백은 유지)

### 2. 악의적 변경 감지
- 스크립트 태그 추가/수정
- 외부 링크 추가
- 폼 구조 변경
- 의심스러운 JavaScript 패턴:
  - `eval()`
  - `document.write`
  - `innerHTML =`
  - `<iframe>`
  - `javascript:`
  - `onload=`, `onclick=`

## 📈 성능 및 안정성

### 네트워크 안정성
- 30초 타임아웃 설정
- User-Agent 헤더 설정
- 10MB HTML 크기 제한

### 에러 처리
- 네트워크 오류 처리
- HTML 파싱 오류 처리
- 데이터베이스 오류 처리

## 🔍 모니터링 결과 예시

```
2024-01-15 10:30:15 - INFO - [내용 기반 모드] 실제 HTML 내용과 악의적 스크립트를 모두 감지합니다.
2024-01-15 10:30:16 - WARNING - [내용 기반 모드] 내용 변경: 스크립트 추가, 의심스러운 내용
2024-01-15 10:30:16 - INFO - 모니터링 완료
```

## ⚠️ 주의사항

1. **BeautifulSoup 의존성**: `beautifulsoup4` 패키지가 필요합니다
2. **테스트 환경**: 로컬 테스트 시 포트 8000이 사용됩니다
3. **데이터 백업**: 중요한 데이터는 별도로 백업하세요
4. **네트워크**: 안정적인 인터넷 연결이 필요합니다
5. **테스트 파일 분리**: 테스트용 파일들은 운영용과 완전히 분리됩니다

## 🚨 알려진 제한사항

### 동적 CSS 해시 문제
현재 시스템은 **단순 SHA256 해시 비교**를 사용하므로 다음과 같은 무의미한 변경도 감지합니다:

- **동적 CSS 파일 해시**: `styles-abc123.css` → `styles-def456.css`
- **타임스탬프 변경**: 페이지 로드 시간, 세션 시간 등
- **세션 토큰**: CSRF 토큰, 세션 ID 등 동적 값
- **광고 스크립트**: Google Analytics, 광고 태그 등

### ✅ 현재 구현 상태
```python
# simple_compare.py - 현재 구현 (동적 필터링 포함)
def is_html_exactly_equal_filtered(html1: str, html2: str) -> bool:
    """동적 요소를 필터링한 후 HTML 비교"""
    normalized_html1 = normalize_dynamic_content(html1)
    normalized_html2 = normalize_dynamic_content(html2)
    return normalized_html1 == normalized_html2

def normalize_dynamic_content(html: str) -> str:
    """동적 요소 정규화"""
    # CSS/JS 타임스탬프 제거 (?t=숫자)
    html = re.sub(r'\?t=\d+', '', html)
    # JavaScript 세션 토큰 정규화
    html = re.sub(r'(NfVTe|sXDdA|qPSFs|Tywgp)":"[^"]*"', r'\1":"NORMALIZED"', html)
    # 로그 타임스탬프 정규화
    html = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', 'YYYY-MM-DD HH:MM:SS', html)
    return html
```

### 📊 개선된 모니터링 결과
```
2025-01-14 - INFO - 변경 없음 (동적 요소만 변경됨)  # 이전: 매번 변경 감지
2025-01-14 - WARNING - 악의적 변조 감지!           # 실제 위험한 변경만 감지
```

## 🆘 문제 해결

### BeautifulSoup 설치 오류
```bash
pip install beautifulsoup4 lxml
```

### 포트 충돌
```bash
# 다른 포트 사용
python -m http.server 8080
```

### 데이터베이스 오류
```bash
# 운영용 데이터베이스 파일 삭제 후 재생성
rm snapshots_monitor.db
python monitor.py
```

### 테스트 실패 시
```bash
# 테스트 파일들 정리 후 재시도
rm -rf test_pages test_*.db test_*.log test_*.csv
python test_detection_logic.py
```

### 테스트 파일 정리
```bash
# 테스트용 파일들만 삭제
rm -f test_*.db test_*.log test_*.csv
rm -rf test_pages
```
