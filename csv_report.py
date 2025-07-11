import csv
import os
from datetime import datetime
from config import CSV_REPORT_SIMPLE

def save_to_csv_simple(timestamp, url, change_detected, change_details, html_content, content_hash):
    COLUMNS = ['날짜', '시간', 'URL', '변경감지', '변경내용', 'HTML크기(문자)', '해시값(앞10자리)']
    if not os.path.exists(CSV_REPORT_SIMPLE):
        with open(CSV_REPORT_SIMPLE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(COLUMNS)
    dt = datetime.fromisoformat(timestamp)
    date_str = dt.strftime('%Y-%m-%d')
    time_str = dt.strftime('%H:%M:%S')
    with open(CSV_REPORT_SIMPLE, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            date_str,
            time_str,
            url,
            '변경감지' if change_detected else '변경없음',
            change_details if change_details else 'N/A',
            len(html_content),
            content_hash[:10]
        ])
    print(f"CSV 요약 보고서(단순) 업데이트 완료: {CSV_REPORT_SIMPLE}") 