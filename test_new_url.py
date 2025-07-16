#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
새 URL 직접 스크래핑 테스트
"""

import requests
from fetcher import fetch_page

def test_new_url_direct():
    """새 URL을 직접 테스트"""
    url = "https://www.kyobo.com/dgt/web/dtm/lc/tu/login"
    
    print(f"🔍 URL 테스트: {url}")
    print("=" * 60)
    
    # 1. fetch_page 함수 사용
    print("1️⃣ fetch_page 함수 결과:")
    result1 = fetch_page(url)
    if result1:
        print(f"   길이: {len(result1)} 문자")
        print(f"   내용: {result1[:200]}...")
        
        # 파일로 저장
        with open("new_url_fetch_page.html", "w", encoding="utf-8") as f:
            f.write(result1)
        print("   저장: new_url_fetch_page.html")
    else:
        print("   결과: None (실패)")
    
    print()
    
    # 2. requests 직접 사용
    print("2️⃣ requests 직접 호출 결과:")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   상태코드: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   길이: {len(response.text)} 문자")
        print(f"   내용: {response.text[:200]}...")
        
        # 파일로 저장
        with open("new_url_requests.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("   저장: new_url_requests.html")
        
        # 응답 헤더 확인
        print("\n📋 응답 헤더:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
            
    except Exception as e:
        print(f"   오류: {e}")

if __name__ == "__main__":
    test_new_url_direct()