#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DB에서 마지막 3개의 스냅샷을 추출하여 HTML 파일로 저장하는 스크립트
"""

import sqlite3
from config import DATABASE_PATH

def extract_last_three_snapshots():
    """DB에서 마지막 3개의 스냅샷을 가져와서 HTML 파일로 저장"""
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, html_content 
            FROM snapshots 
            ORDER BY timestamp DESC 
            LIMIT 3
        """)
        results = cursor.fetchall()
        
        if not results:
            print("DB에 저장된 스냅샷이 없습니다.")
            return
        
        print(f"총 {len(results)}개의 스냅샷을 찾았습니다.")
        
        for i, (snapshot_id, timestamp, html_content) in enumerate(results):
            filename = f"snapshot_{i+1}_latest.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"저장됨: {filename} (ID: {snapshot_id}, 시간: {timestamp})")

if __name__ == "__main__":
    extract_last_three_snapshots()