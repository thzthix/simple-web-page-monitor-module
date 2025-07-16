#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
교보 계열사 13개 사이트 전체 스크래핑
"""

import os
import requests
from datetime import datetime

# 13개 사이트 URL 리스트
KYOBO_URLS = [
    ("교보문고", "통합PC", "https://mmbr.kyobobook.co.kr/login"),
    ("교보문고", "eBook", "https://mmbr.kyobobook.co.kr/login?continue=https://ebook.kyobobook.co.kr/"),
    ("교보문고", "sam정액구독", "https://mmbr.kyobobook.co.kr/login?continue=https://sam.kyobobook.co.kr/"),
    ("교보문고", "핫트랙스몰", "https://mmbr.kyobobook.co.kr/login?continue=https://hottracks.kyobobook.co.kr/"),
    ("교보문고", "스토리플랫폼", "https://mmbr.kyobobook.co.kr/login?continue=https://storynew.kyobobook.co.kr/"),
    ("교보문고", "핫트랙스관리자", "https://admin.hottracks.co.kr/admin/login/form"),
    ("교보생명", "통합로그인", "https://www.kyobo.com/dgt/web/dtm/lc/tu/login"),
    ("교보생명", "금융인증서", "https://www.kyobo.com/dgt/web/dtm/lc/tu/kftcLogin"),
    ("교보생명", "카카오인증서", "https://www.kyobo.com/dgt/web/dtm/lc/tu/kakaoLogin"),
    ("교보생명", "토스인증서", "https://www.kyobo.com/dgt/web/dtm/lc/tu/tossLogin"),
    ("교보생명", "사내SmartON", "https://sso.kyobo.com:5443/3rdParty/certLoginFormPage.jsp"),
    ("교보라이프플래닛", "통합PC", "https://www.lifeplanet.co.kr/lpds2/common/ua/UA01001S.dev"),
    ("교보증권", "고객포털PC", "https://www.iprovest.com/weblogic/LOginServlet")
]

def create_folders():
    """날짜별 폴더 구조 생성"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    base_dir = f"kyobo_scraping_{date_str}"
    
    # 기본 폴더 생성
    os.makedirs(base_dir, exist_ok=True)
    
    # 관계사별 폴더 생성
    companies = ["교보문고", "교보생명", "교보라이프플래닛", "교보증권"]
    for company in companies:
        company_dir = os.path.join(base_dir, company)
        os.makedirs(company_dir, exist_ok=True)
    
    return base_dir

def fetch_html(url):
    """HTML 가져오기"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ 오류: {e}")
        return None

def scrape_all():
    """전체 스크래핑 실행"""
    print("🚀 교보 계열사 13개 사이트 스크래핑 시작")
    print("="*50)
    
    base_dir = create_folders()
    timestamp = datetime.now().strftime("%H%M%S")
    
    success = 0
    total = len(KYOBO_URLS)
    
    for i, (company, service, url) in enumerate(KYOBO_URLS, 1):
        print(f"[{i}/{total}] {company} - {service}")
        print(f"  URL: {url}")
        
        # HTML 가져오기
        html = fetch_html(url)
        
        if html:
            # 파일 저장
            filename = f"{service}_{timestamp}.html"
            filepath = os.path.join(base_dir, company, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"  ✅ 저장: {filepath} ({len(html):,} 문자)")
            success += 1
        else:
            print(f"  ❌ 실패")
        
        print()
    
    print("📋 완료 요약")
    print("="*50)
    print(f"✅ 성공: {success}/{total}")
    print(f"📁 저장 위치: {base_dir}")
    
    # 폴더별 파일 개수
    for company in ["교보문고", "교보생명", "교보라이프플래닛", "교보증권"]:
        company_dir = os.path.join(base_dir, company)
        if os.path.exists(company_dir):
            files = [f for f in os.listdir(company_dir) if f.endswith('.html')]
            print(f"  {company}: {len(files)}개 파일")

if __name__ == "__main__":
    scrape_all()