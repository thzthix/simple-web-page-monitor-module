#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
교보 계열사 사이트 설정
"""

KYOBO_SITES = {
    "교보문고": {
        "통합(PC)": "https://mmbr.kyobobook.co.kr/login",
        "eBook": "https://mmbr.kyobobook.co.kr/login?continue=https://ebook.kyobobook.co.kr/",
        "sam 정액구독": "https://mmbr.kyobobook.co.kr/login?continue=https://sam.kyobobook.co.kr/",
        "핫트랙스몰": "https://mmbr.kyobobook.co.kr/login?continue=https://hottracks.kyobobook.co.kr/",
        "스토리 플랫폼": "https://mmbr.kyobobook.co.kr/login?continue=https://storynew.kyobobook.co.kr/",
        "핫트랙스 관리자 포털": "https://admin.hottracks.co.kr/admin/login/form"
    },
    "교보생명": {
        "통합 로그인 선택 화면": "https://www.kyobo.com/dgt/web/dtm/lc/tu/login",
        "금융인증서": "https://www.kyobo.com/dgt/web/dtm/lc/tu/kftcLogin",
        "카카오 인증서": "https://www.kyobo.com/dgt/web/dtm/lc/tu/kakaoLogin",
        "토스 인증서": "https://www.kyobo.com/dgt/web/dtm/lc/tu/tossLogin",
        "기업고객(코퍼레이트)": "https://www.kyobo.com/dgt/web/dtm/lc/tu/login",  # 동일 URL
        "사내 Smart-ON": "https://sso.kyobo.com:5443/3rdParty/certLoginFormPage.jsp"
    },
    "교보라이프플래닛": {
        "통합(PC)": "https://www.lifeplanet.co.kr/lpds2/common/ua/UA01001S.dev"
    },
    "교보증권": {
        "고객 포털(PC)": "https://www.iprovest.com/weblogic/LOginServlet"
    }
}

# URL을 플랫 리스트로 변환
def get_all_urls():
    """모든 URL을 (회사명, 서비스명, URL) 튜플의 리스트로 반환"""
    urls = []
    for company, services in KYOBO_SITES.items():
        for service, url in services.items():
            urls.append((company, service, url))
    return urls

# 파일명 안전화 함수
def safe_filename(text):
    """파일명에 안전한 문자열로 변환"""
    import re
    # 특수문자를 언더스코어로 변경
    safe = re.sub(r'[^\w\s-]', '_', text)
    # 공백을 언더스코어로 변경
    safe = re.sub(r'\s+', '_', safe)
    # 연속된 언더스코어를 하나로 변경
    safe = re.sub(r'_+', '_', safe)
    # 앞뒤 언더스코어 제거
    return safe.strip('_')

if __name__ == "__main__":
    # 테스트
    urls = get_all_urls()
    print(f"총 {len(urls)}개 URL:")
    for company, service, url in urls:
        print(f"  {company} - {service}: {url}")
        print(f"    파일명: {safe_filename(company)}_{safe_filename(service)}")
    
    # 중복 URL 확인
    url_list = [url for _, _, url in urls]
    unique_urls = set(url_list)
    if len(url_list) != len(unique_urls):
        print(f"\n⚠️ 중복 URL 발견: {len(url_list) - len(unique_urls)}개")
        from collections import Counter
        duplicates = [url for url, count in Counter(url_list).items() if count > 1]
        for dup in duplicates:
            print(f"  중복: {dup}")