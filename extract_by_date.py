#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DB에서 모든 스냅샷을 날짜별 폴더로 분류하여 HTML 파일로 저장하는 스크립트
"""

import sqlite3
import os
from config import DATABASE_PATH
from datetime import datetime

def extract_snapshots_by_date():
    """DB에서 모든 스냅샷을 가져와서 날짜별 폴더로 분류하여 HTML 파일로 저장"""
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        
        # 모든 스냅샷 가져오기
        cursor.execute("""
            SELECT id, timestamp, html_content 
            FROM snapshots 
            ORDER BY timestamp ASC
        """)
        results = cursor.fetchall()
        
        if not results:
            print("DB에 저장된 스냅샷이 없습니다.")
            return
        
        print(f"총 {len(results)}개의 스냅샷을 찾았습니다.")
        
        # 날짜별로 그룹화
        date_groups = {}
        for snapshot_id, timestamp, html_content in results:
            # 날짜 추출 (YYYY-MM-DD 형식)
            date_str = timestamp.split('T')[0]
            
            if date_str not in date_groups:
                date_groups[date_str] = []
            
            date_groups[date_str].append((snapshot_id, timestamp, html_content))
        
        # 날짜별 폴더 생성 및 파일 저장
        for date_str, snapshots in date_groups.items():
            # 폴더 생성
            folder_name = f"snapshots_{date_str}"
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
                print(f"폴더 생성: {folder_name}")
            
            # 해당 날짜의 스냅샷들을 파일로 저장
            for i, (snapshot_id, timestamp, html_content) in enumerate(snapshots):
                # 시간 부분 추출 (HH-MM-SS 형식)
                time_part = timestamp.split('T')[1].replace(':', '-').split('.')[0]
                filename = f"{folder_name}/snapshot_{i+1:02d}_{time_part}_id{snapshot_id}.html"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                print(f"저장됨: {filename}")
        
        print(f"\n날짜별 분류 완료:")
        for date_str, snapshots in date_groups.items():
            print(f"  {date_str}: {len(snapshots)}개 스냅샷")

if __name__ == "__main__":
    extract_snapshots_by_date()