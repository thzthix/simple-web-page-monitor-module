#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스크랩된 HTML 파일들을 비교하는 스크립트
각 페이지별로 최근 두 개의 스냅샷을 비교하여 차이점을 정리합니다.
"""

import os
import re
from datetime import datetime
from collections import defaultdict

from compare_snapshots import read_html_file, find_differences

# 스크랩된 HTML 파일이 저장된 기본 디렉토리
BASE_SCRAPES_DIR = r"C:\Users\KICO\scrapes"

def get_latest_scrape_dir():
    """가장 최근에 생성된 스크랩 디렉토리를 찾아서 반환"""
    all_scrape_dirs = [d for d in os.listdir(BASE_SCRAPES_DIR) if os.path.isdir(os.path.join(BASE_SCRAPES_DIR, d)) and d.startswith("kyobo_scraping_")]
    all_scrape_dirs.sort(key=lambda x: datetime.strptime(x, "kyobo_scraping_%Y-%m-%d"), reverse=True)
    if all_scrape_dirs:
        return os.path.join(BASE_SCRAPES_DIR, all_scrape_dirs[0])
    return None

def compare_latest_two_snapshots():
    """각 페이지별로 최근 두 개의 스냅샷을 비교하여 차이점을 출력"""
    latest_scrape_dir = get_latest_scrape_dir()
    if not latest_scrape_dir:
        print(f"오류: 스크랩 디렉토리를 찾을 수 없습니다. {BASE_SCRAPES_DIR} 경로를 확인하세요.")
        return

    print(f"최근 스크랩 디렉토리: {latest_scrape_dir}")
    print("--------------------------------------------------")

    # 관계사별로 파일들을 그룹화
    company_files = defaultdict(lambda: defaultdict(list))
    for company_name in os.listdir(latest_scrape_dir):
        company_path = os.path.join(latest_scrape_dir, company_name)
        if os.path.isdir(company_path):
            for filename in os.listdir(company_path):
                if filename.endswith(".html"):
                    # 파일명에서 서비스명과 타임스탬프 추출
                    match = re.match(r'(.+)_(\d{6})\.html', filename)
                    if match:
                        service_name = match.group(1)
                        timestamp = match.group(2)
                        company_files[company_name][service_name].append((timestamp, os.path.join(company_path, filename)))
    
    # 각 서비스별로 최근 두 개의 스냅샷 비교
    for company, services in company_files.items():
        print(f"\n### 관계사: {company} ###")
        for service, snapshots in services.items():
            # 타임스탬프 기준으로 정렬 (최신순)
            snapshots.sort(key=lambda x: x[0], reverse=True)
            
            if len(snapshots) >= 2:
                latest_timestamp, latest_file = snapshots[0]
                second_latest_timestamp, second_latest_file = snapshots[1]

                print(f"\n--- 서비스: {service} ---")
                print(f"  최신 스냅샷: {os.path.basename(latest_file)}")
                print(f"  2번째 스냅샷: {os.path.basename(second_latest_file)}")

                html1 = read_html_file(latest_file)
                html2 = read_html_file(second_latest_file)

                if html1 is not None and html2 is not None:
                    diff_result = find_differences(html1, html2, f"{service} (최신)", f"{service} (2번째)")
                    print(diff_result)
                else:
                    print("  오류: HTML 파일을 읽을 수 없습니다.")
            else:
                print(f"\n--- 서비스: {service} ---")
                print("  비교할 스냅샷이 2개 미만입니다.")

if __name__ == "__main__":
    compare_latest_two_snapshots()