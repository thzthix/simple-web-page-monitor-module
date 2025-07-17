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
    동적 요소를 필터링한 후 HTML 동일성 확인
    실제 콘텐츠만 비교하고 타임스탬프, 세션 토큰 등은 무시
    """
    normalized1 = normalize_dynamic_content(html1)
    normalized2 = normalize_dynamic_content(html2)
    
    return normalized1 == normalized2

def normalize_dynamic_content(html: str) -> str:
    """
    HTML에서 동적 요소들을 정규화하여 실제 콘텐츠 변경만 감지할 수 있도록 함
    
    제거/정규화하는 요소들:
    - CSS/JS 파일의 타임스탬프/버전 파라미터 (?t=숫자, ?v=날짜, ?r=날짜, ?dt=날짜)
    - JavaScript 세션/보안 토큰 (ErW76 객체 등)
    - JavaScript 변수 내 날짜/시간 값
    - JavaScript 변수 내 IP 주소
    - JavaScript 변수 내 API 키/플러그인 키
    - 브라우저 생성 HTML 메타데이터
    - 로그 타임스탬프
    - 암호화 관련 동적 값
    """
    normalized = html
    
    # 1. CSS/JS 파일의 타임스탬프/버전 파라미터 제거 (?t=숫자, ?v=날짜, ?r=날짜, ?dt=날짜)
    normalized = re.sub(r'\?[tvrdt]=\d{4}\.\d{2}\.\d{2}(?:\.\d+)?', '?v=TIMESTAMP', normalized) # ?v=YYYY.MM.DD.NN, ?r=YYYY.MM.DD, ?dt=YYYYMMDD
    normalized = re.sub(r'\?[tvrdt]=\d+', '?t=TIMESTAMP', normalized) # ?t=숫자
    
    # 2. JavaScript 세션 토큰 정규화 (TNK_SR)
    normalized = re.sub(r'(var\s+TNK_SR\s*=\s*["])[a-f0-9]{32}(["])', r'\1TNK_SR_TOKEN\2', normalized, flags=re.MULTILINE) # TNK_SR

    # 3. fncAesEnc 함수 내의 암호화된 데이터 정규화
    normalized = re.sub(r'(fncAesEnc\(["])[a-zA-Z0-9+/=]{20,}(["]\))', r'\1ENCRYPTED_DATA\2', normalized)

    # 4. URL 파라미터 내의 InitechEamNoCacheNonce 값 정규화 (URL 인코딩된 Base64)
    normalized = re.sub(r'(InitechEamNoCacheNonce=)[a-zA-Z0-9%+/=]+', r'\1INITECH_NONCE_TOKEN', normalized)

    # 5. gitple-loader-frame의 title 속성 정규화 (동적으로 변하는 한글 타이틀 처리)
    normalized = re.sub(r'(iframe id=\"gitple-loader-frame\" .*? title=\")[^\"]*(\")', r'\1GITPLE_TITLE\2', normalized)

    # 6. body 태그의 style 속성 제거 (display: none; 등 동적으로 추가되는 스타일)
    normalized = re.sub(r'<body([^>]*?) style=\"[^\"]*\"([^>]*?)>', r'<body\1\2>', normalized)

    # 7. body 태그의 class 속성 내 동적 클래스 제거 (is-header 등)
    normalized = re.sub(r'(body[^>]*?class=\"[^\"]*?)(is-header|is-floatbots|cetis-full)(\"[^>]*?>)', r'\1\3', normalized)

    # 8. input 태그의 value 속성 내 동적 날짜/시간 값 정규화 (dateCheck)
    normalized = re.sub(r'(value=\")\d{14}(\")', r'\1DATETIME_VALUE\2', normalized) # YYYYMMDDHHMMSS (dateCheck)

    # 9. JavaScript 변수 내 날짜/시간 값 정규화 (plainText)
    normalized = re.sub(r'(var\s+plainText=loginId\+\")\d{14}(\")', r'\1DATETIME_VALUE\2', normalized)

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
