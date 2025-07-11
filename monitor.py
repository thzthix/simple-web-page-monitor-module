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
from simple_compare import is_html_changed
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
    latest_snapshot = get_latest_snapshot(TARGET_URL)
    if not latest_snapshot:
        logger.info("[단순 모드] 첫 번째 스냅샷을 생성합니다.")
        return True, '첫 번째 스냅샷'

    previous_html = latest_snapshot.get('html_content', None)
    assert previous_html is not None, "DB에 스냅샷이 있는데 html_content가 None인 경우는 비정상입니다."
    change_detected = is_html_changed(previous_html, html_content)
    if change_detected:
        logger.warning("[단순 모드] 전체 HTML 해시가 변경되었습니다.")
        change_details = '전체 HTML 해시 변경'
    else:
        logger.info("[단순 모드] 변경 없음 (해시 동일)")
        change_details = '변경사항 없음'
    return change_detected, change_details

def save_results(html_content, change_detected, change_details):
    content_hash = hashlib.sha256(html_content.encode('utf-8')).hexdigest()
    timestamp = save_snapshot(TARGET_URL, content_hash, html_content, change_detected, change_details)
    return timestamp, content_hash

def monitor_once():
    print("[DEBUG] monitor_once 시작")
    logger = setup_logging()
    print("[DEBUG] setup_logging() 완료")
    logger.info("[단순 모드] 전체 HTML 해시만 비교합니다.")
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
