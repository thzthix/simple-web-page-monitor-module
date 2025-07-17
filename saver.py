#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스크래핑 결과 저장 모듈
HTML 파일 저장 및 데이터베이스 스냅샷 저장을 담당합니다.
"""

import os
import sqlite3
from datetime import datetime
from config.config import DATABASE_PATH

def create_folders():
    """날짜별 폴더 구조 생성"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    # 저장 경로를 C:\Users\KICO\scrapes 로 변경
    base_dir = os.path.join(r"C:\Users\KICO\scrapes", f"kyobo_scraping_{date_str}")
    
    # 기본 폴더 생성
    os.makedirs(base_dir, exist_ok=True)
    
    # 관계사별 폴더 생성
    companies = ["교보문고", "교보생명", "교보라이프플래닛", "교보증권"]
    for company in companies:
        company_dir = os.path.join(base_dir, company)
        os.makedirs(company_dir, exist_ok=True)
    
    return base_dir

def save_html_to_file(base_dir, company, service, timestamp, html_content):
    """스크래핑한 HTML을 파일로 저장"""
    filename = f"{service}_{timestamp}.html"
    filepath = os.path.join(base_dir, company, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filepath

def save_snapshot(url, content_hash, html_content, html_size=0, change_detected=False, change_details=None):
    """Saves a new snapshot to the database."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO snapshots (timestamp, url, content_hash, html_content, html_size, change_detected, change_details) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (timestamp, url, content_hash, html_content, html_size, change_detected, change_details)
        )
        conn.commit()
        return timestamp
