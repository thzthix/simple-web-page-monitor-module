#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모든 교보 계열사 사이트 모니터링 및 결과 데이터베이스 저장
"""

import hashlib
import logging
import sys
from datetime import datetime
import os

from database import setup_database
from logger import setup_logging
from config.urls import KYOBO_URLS
from scrape_all_sites import fetch_html
from saver import create_folders, save_html_to_file, save_snapshot

# 표준 출력 인코딩 설정 (Windows 환경에서 한글 깨짐 방지)
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def monitor_all_sites():
    """
    모든 교보 계열사 사이트를 모니터링하고 결과를 데이터베이스에 저장
    """
    logger = setup_logging()
    setup_database()

    logger.info("교보 계열사 사이트 모니터링 시작")
    logger.info("="*50)
    
    base_dir = create_folders() # scrape_all_sites에서 폴더 생성 함수 재사용
    timestamp = datetime.now().strftime("%H%M%S")
    
    success_count = 0
    total = len(KYOBO_URLS)
    
    for i, (company, service, url) in enumerate(KYOBO_URLS, 1):
        logger.info(f"[{i}/{total}] {company} - {service}")
        logger.info(f"  URL: {url}")
        
        html = None
        change_detected = False
        change_details = ""
        content_hash = ""
        html_size = 0

        try:
            # HTML 가져오기
            html = fetch_html(url)
            
            if html:
                # 파일 저장
                filepath = save_html_to_file(base_dir, company, service, timestamp, html)
                
                logger.info(f"  저장: {filepath} ({len(html):,} 문자)")
                success_count += 1
                
                content_hash = hashlib.sha256(html.encode('utf-8')).hexdigest()
                html_size = len(html)
                change_detected = True # 첫 스크래핑이므로 변경으로 간주
                change_details = "최초 스크래핑 성공"
                logger.info(f"  ✅ 성공")
            else:
                change_details = "페이지 가져오기 실패"
                logger.error(f"  ❌ 실패: {change_details}")
        except Exception as e:
            change_details = f"스크래핑 중 오류 발생: {e}"
            logger.error(f"  ❌ 실패: {change_details}")
        finally:
            # 데이터베이스에 결과 저장
            save_snapshot(url, content_hash, html if html else "", html_size, change_detected, change_details)
        
        logger.info("") # 빈 줄 추가
    
    logger.info("완료 요약")
    logger.info("="*50)
    logger.info(f"성공: {success_count}/{total}")
    logger.info(f"저장 위치: {base_dir}")

if __name__ == "__main__":
    monitor_all_sites()
