#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
단순 HTML 변경 비교 모듈
두 HTML 문자열이 해시(SHA256) 기준으로 동일한지(변경 여부만) 판단합니다.
동적 요소(타임스탬프, 세션 토큰 등)를 필터링하여 실제 콘텐츠 변경만 감지합니다.
"""

import hashlib
import re
from bs4 import BeautifulSoup, Tag

def is_html_changed(html1: str, html2: str) -> bool:
    """
    두 HTML 문자열의 SHA256 해시가 동일한지 비교 (True면 변경됨, False면 동일)
    """
    hash1 = hashlib.sha256(html1.encode('utf-8')).hexdigest()
    hash2 = hashlib.sha256(html2.encode('utf-8')).hexdigest()
    return hash1 != hash2

def is_html_exactly_equal(html1: str, html2: str) -> bool:
    """
    두 HTML 문자열이 완전히 동일한지 비교 (True면 동일, False면 다름)
    """
    return html1 == html2

def normalize_dynamic_content(html: str) -> str:
    """
    HTML에서 동적 요소들을 정규화하여 실제 콘텐츠 변경만 감지할 수 있도록 함
    
    제거/정규화하는 요소들:
    - CSS/JS 파일의 타임스탬프 파라미터 (?t=숫자)
    - JavaScript 세션/보안 토큰 (ErW76 객체 등)
    - 브라우저 생성 HTML 메타데이터
    - 로그 타임스탬프
    """
    normalized = html
    
    # 1. CSS/JS 파일의 타임스탬프 파라미터 제거 (?t=숫자)
    normalized = re.sub(r'\?t=\d+', '?t=TIMESTAMP', normalized)
    
    # 2. JavaScript 세션 토큰 정규화 (ErW76 객체의 NfVTe 속성)
    # "NfVTe":"긴인코딩문자열" -> "NfVTe":"SESSION_TOKEN"
    normalized = re.sub(r'"NfVTe":"[^"]*"', '"NfVTe":"SESSION_TOKEN"', normalized)
    
    # 3. 기타 세션 관련 토큰들 정규화
    normalized = re.sub(r'"sXDdA":"[^"]*"', '"sXDdA":"SECURITY_TOKEN"', normalized)
    normalized = re.sub(r'"qPSFs":"[^"]*"', '"qPSFs":"SECURITY_TOKEN"', normalized)
    normalized = re.sub(r'"Tywgp":"[^"]*"', '"Tywgp":"SECURITY_TOKEN"', normalized)
    
    # 4. 로그 타임스탬프 정규화 (YYYY-MM-DD HH:MM:SS,mmm)
    normalized = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}', 'YYYY-MM-DD HH:MM:SS,mmm', normalized)
    
    # 5. 브라우저가 생성하는 파일 경로 차이 정규화
    normalized = re.sub(r'교보문고\d*_files', '교보문고_files', normalized)
    
    # 6. kjkOT 보안 객체 전체 필터링 (멀티라인 대응)
    normalized = re.sub(r'var kjkOT = \{.*?\};', 'var kjkOT = {SECURITY_TOKENS};', normalized, flags=re.DOTALL)
    
    return normalized

def is_html_changed_filtered(html1: str, html2: str) -> bool:
    """
    동적 요소를 필터링한 후 HTML 변경 여부 확인
    실제 콘텐츠 변경만 감지하고 타임스탬프, 세션 토큰 등은 무시
    """
    normalized1 = normalize_dynamic_content(html1)
    normalized2 = normalize_dynamic_content(html2)
    
    hash1 = hashlib.sha256(normalized1.encode('utf-8')).hexdigest()
    hash2 = hashlib.sha256(normalized2.encode('utf-8')).hexdigest()
    
    return hash1 != hash2

def is_html_exactly_equal_filtered(html1: str, html2: str) -> bool:
    """
    동적 요소를 필터링한 후 HTML 동일성 확인
    실제 콘텐츠만 비교하고 타임스탬프, 세션 토큰 등은 무시
    """
    normalized1 = normalize_dynamic_content(html1)
    normalized2 = normalize_dynamic_content(html2)
    
    return normalized1 == normalized2 