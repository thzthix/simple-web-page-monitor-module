#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
새 URL의 스냅샷을 추출하여 분석하는 스크립트
"""

import sqlite3
from config import DATABASE_PATH

def extract_new_url_snapshot():
    """새 URL의 최신 스냅샷을 추출"""
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        
        # 새 URL의 최신 스냅샷 가져오기
        cursor.execute("""
            SELECT id, timestamp, html_content 
            FROM snapshots 
            WHERE url = 'https://www.kyobo.com/dgt/web/dtm/lc/tu/login'
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        result = cursor.fetchone()
        
        if result:
            snapshot_id, timestamp, html_content = result
            
            # HTML 파일로 저장
            filename = f"kyobo_new_login_{snapshot_id}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"저장됨: {filename}")
            print(f"ID: {snapshot_id}, 시간: {timestamp}")
            print(f"HTML 크기: {len(html_content)} 문자")
            
            # 보안 객체 찾기
            import re
            var_pattern = r'var\s+([a-zA-Z0-9]+)\s*=\s*\{'
            matches = re.findall(var_pattern, html_content)
            if matches:
                print(f"발견된 JavaScript 변수들: {matches}")
            else:
                print("JavaScript 변수를 찾을 수 없습니다.")
                
            return filename
        else:
            print("새 URL의 스냅샷을 찾을 수 없습니다.")
            return None

if __name__ == "__main__":
    extract_new_url_snapshot()