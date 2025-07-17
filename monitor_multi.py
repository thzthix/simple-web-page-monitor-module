#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
다중 URL 웹페이지 변경 모니터
여러 URL을 동시에 모니터링하고, 결과를 날짜/관계사별 폴더에 저장합니다.
"""

import hashlib
import logging
import os
import sys
from datetime import datetime
from database import setup_database, get_latest_snapshot, save_snapshot
from simple_compare import is_html_changed_filtered
from fetcher import fetch_page
from logger import setup_logging
from csv_report import save_to_csv_simple
from kyobo_sites_config import get_all_urls, safe_filename

# 표준 출력 인코딩 설정
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 스크립트 파일의 절대 경로를 기준으로 snapshots 폴더 경로 설정
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SNAPSHOTS_DIR = os.path.join(SCRIPT_DIR, 'snapshots')



def monitor_site(company, service, url, logger):
    """
    단일 사이트 모니터링
    """
    logger.info(f"모니터링 시작: {company} - {service} ({url})")
    
    html_content = fetch_page(url)
    change_detected = False
    change_details = ""
    content_hash = ""
    html_size = 0

    if html_content:
        # 2. HTML 파일로 저장

        # 3. 변경 감지 (필터링 로직 사용)
        latest_snapshot = get_latest_snapshot(url)
        if latest_snapshot:
            previous_html = latest_snapshot.get('html_content', '')
            if not is_html_changed_filtered(previous_html, html_content):
                change_detected = False
                change_details = "변경 없음 (필터링 후)"
            else:
                change_detected = True
                change_details = "콘텐츠 변경됨 (필터링 후)"
        else:
            change_detected = True
            change_details = "첫 번째 스냅샷"

        # 4. 데이터베이스에 결과 저장
        content_hash = hashlib.sha256(html_content.encode('utf-8')).hexdigest()
        html_size = len(html_content)
        save_snapshot(url, content_hash, html_content, html_size, change_detected, change_details)
    else:
        # 페이지 가져오기 실패 시
        change_detected = True # 실패도 일종의 변경으로 간주
        change_details = "페이지 가져오기 실패"
        # html_content, content_hash, html_size는 기본값 또는 None으로 유지

    # 5. CSV 요약 보고서 저장 (성공/실패 여부와 관계없이 항상 호출)
    timestamp = datetime.now().isoformat()
    save_to_csv_simple(timestamp, url, change_detected, change_details, html_content, content_hash)
    
    logger.info(f"모니터링 완료: {company} - {service}")

def monitor_all_sites():
    """
    모든 교보 계열사 사이트를 모니터링
    """
    logger = setup_logging()
    setup_database()
    
    sites = get_all_urls()
    logger.info(f"총 {len(sites)}개 사이트 모니터링을 시작합니다.")
    
    for company, service, url in sites:
        try:
            monitor_site(company, service, url, logger)
        except Exception as e:
            logger.error(f"URL 모니터링 중 오류 발생 {url}: {e}")
            print(f"[ERROR] {url}: {e}")
        
    logger.info("모든 사이트 모니터링이 완료되었습니다.")

if __name__ == "__main__":
    monitor_all_sites()