#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간이 웹페이지 변경 모니터 (단순 해시 비교)
전체 HTML이 바뀌었는지 아닌지만 감지합니다.
"""

import hashlib
import logging
from datetime import datetime
from database import setup_database, get_latest_snapshot, save_snapshot
from simple_compare import is_html_exactly_equal, is_html_exactly_equal_filtered
from fetcher import fetch_page
from logger import setup_logging
from csv_report import save_to_csv_simple
from config import TARGET_URL, LOG_FILE

# --- MAIN ---
def fetch_target_html(logger):
    html_content = fetch_page(TARGET_URL)
    if not html_content:
        logger.error("페이지를 가져올 수 없어 모니터링을 중단합니다.")
    return html_content

def detect_change(html_content, logger):
    """
    HTML 변경 감지 (동적 요소 필터링 적용)
    타임스탬프, 세션 토큰 등은 무시하고 실제 콘텐츠 변경만 감지
    """
    latest_snapshot = get_latest_snapshot(TARGET_URL)
    if not latest_snapshot:
        logger.info("첫 번째 스냅샷을 생성합니다.")
        return True, '첫 번째 스냅샷'

    previous_html = latest_snapshot.get('html_content', None)
    assert previous_html is not None, "DB에 스냅샷이 있는데 html_content가 None인 경우는 비정상입니다."
    
    # 동적 요소 필터링 후 비교
    change_detected = not is_html_exactly_equal_filtered(previous_html, html_content)
    if change_detected:
        logger.warning("실제 콘텐츠가 변경되었습니다.")
        change_details = '실제 콘텐츠 변경 (동적 요소 제외)'
    else:
        logger.info("변경 없음 (동적 요소만 변경됨)")
        change_details = '동적 요소만 변경됨 (실제 콘텐츠 동일)'
    
    return change_detected, change_details

def save_results(html_content, change_detected, change_details):
    content_hash = hashlib.sha256(html_content.encode('utf-8')).hexdigest()
    html_size = len(html_content) if html_content else 0
    timestamp = save_snapshot(TARGET_URL, content_hash, html_content, html_size, change_detected, change_details)
    return timestamp, content_hash

def monitor_once():
    print("[DEBUG] monitor_once 시작")
    logger = setup_logging()
    print("[DEBUG] setup_logging() 완료")
    logger.info("동적 요소 필터링 후 HTML 콘텐츠를 비교합니다.")
    setup_database()
    html_content = fetch_target_html(logger)
    if not html_content:
        print("[DEBUG] html_content 없음, 종료")
        return
    change_detected, change_details = detect_change(html_content, logger)
    timestamp, content_hash = save_results(html_content, change_detected, change_details)
    save_to_csv_simple(timestamp, TARGET_URL, change_detected, change_details, html_content, content_hash)
    logger.info("모니터링 완료")
    print("[DEBUG] monitor_once 끝")

if __name__ == "__main__":
    monitor_once()
