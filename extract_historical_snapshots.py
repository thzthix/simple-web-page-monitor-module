#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DB에서 맨 처음, 어제, 오늘 최신 스냅샷을 추출하여 HTML 파일로 저장하는 스크립트
"""

import sqlite3
from config import DATABASE_PATH
from datetime import datetime, timedelta

def extract_historical_snapshots():
    """DB에서 맨 처음, 어제, 오늘 최신 스냅샷을 가져와서 HTML 파일로 저장"""
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        
        # 전체 스냅샷 수 확인
        cursor.execute("SELECT COUNT(*) FROM snapshots")
        total_count = cursor.fetchone()[0]
        print(f"DB에 총 {total_count}개의 스냅샷이 있습니다.")
        
        if total_count == 0:
            print("DB에 저장된 스냅샷이 없습니다.")
            return
        
        # 1. 맨 처음 스냅샷 (가장 오래된 것)
        cursor.execute("""
            SELECT id, timestamp, html_content 
            FROM snapshots 
            ORDER BY timestamp ASC 
            LIMIT 1
        """)
        first_snapshot = cursor.fetchone()
        
        # 2. 오늘 최신 스냅샷 (가장 최근 것)
        cursor.execute("""
            SELECT id, timestamp, html_content 
            FROM snapshots 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        latest_snapshot = cursor.fetchone()
        
        # 3. 어제 스냅샷 중 하나 (어제 날짜 범위에서 가장 최근)
        cursor.execute("""
            SELECT id, timestamp, html_content 
            FROM snapshots 
            WHERE DATE(timestamp) = '2025-07-15'
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        yesterday_snapshot = cursor.fetchone()
        
        # 어제 스냅샷이 없으면 가장 최근에서 두 번째 스냅샷 사용
        if not yesterday_snapshot:
            print("어제 스냅샷이 없어서 최근 두 번째 스냅샷을 사용합니다.")
            cursor.execute("""
                SELECT id, timestamp, html_content 
                FROM snapshots 
                ORDER BY timestamp DESC 
                LIMIT 1 OFFSET 1
            """)
            yesterday_snapshot = cursor.fetchone()
        
        # HTML 파일로 저장
        snapshots = [
            (first_snapshot, "snapshot_first.html", "맨 처음"),
            (yesterday_snapshot, "snapshot_yesterday.html", "어제"),
            (latest_snapshot, "snapshot_latest.html", "오늘 최신")
        ]
        
        for snapshot_data, filename, description in snapshots:
            if snapshot_data:
                snapshot_id, timestamp, html_content = snapshot_data
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"저장됨: {filename} ({description}) - ID: {snapshot_id}, 시간: {timestamp}")
            else:
                print(f"경고: {description} 스냅샷을 찾을 수 없습니다.")

if __name__ == "__main__":
    extract_historical_snapshots()