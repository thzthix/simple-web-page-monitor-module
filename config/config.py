# config.py

# 모니터링 대상 URL 리스트
TARGET_URLS = [
    "https://mmbr.kyobobook.co.kr/login",
    "https://www.kyobo.com/dgt/web/dtm/lc/tu/login"
]

# 기본 URL (기존 호환성)
TARGET_URL = TARGET_URLS[0]

# 로그 파일 경로
LOG_FILE = "monitor.log"

# 데이터베이스 파일 경로
DATABASE_PATH = "snapshots_monitor.db"  # 새 이름으로 변경

# CSV 요약 보고서 파일 경로
CSV_REPORT_SIMPLE = "monitoring_report_simple.csv" 