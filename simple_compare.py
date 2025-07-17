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
    # `(?:
.
\d+)?` 부분의 괄호 오류 수정
    normalized = re.sub(r'\?[tvrdt]=\d{4}\.\d{2}\.\d{2}(?:\.\d+)?', '?v=TIMESTAMP', normalized) # ?v=YYYY.MM.DD.NN, ?r=YYYY.MM.DD, ?dt=YYYYMMDD
    normalized = re.sub(r'\?[tvrdt]=\d+', '?t=TIMESTAMP', normalized) # ?t=숫자
    
    # 2. JavaScript 세션 토큰 정규화 (ErW76 객체의 NfVTe 속성)
    # normalized = re.sub(r'"NfVTe":"[^"]*"', '"NfVTe":"SESSION_TOKEN"', normalized)
    
    # 3. 기타 세션 관련 토큰들 정규화
    # normalized = re.sub(r'"sXDdA":"[^"]*"', '"sXDdA":"SECURITY_TOKEN"', normalized)
    # normalized = re.sub(r'"qPSFs":"[^"]*"', '"qPSFs":"SECURITY_TOKEN"', normalized)
    # normalized = re.sub(r'"Tywgp":"[^"]*"', '"Tywgp":"SECURITY_TOKEN"', normalized)
    
    # 4. 로그 타임스탬프 정규화 (YYYY-MM-DD HH:MM:SS,mmm)
    # normalized = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}', 'YYYY-MM-DD HH:MM:SS,mmm', normalized)
    
    # 5. 브라우저가 생성하는 파일 경로 차이 정규화
    # normalized = re.sub(r'교보문고\d*_files', '교보문고_files', normalized)
    
    # 6. kjkOT 보안 객체 전체 필터링 (멀티라인 대응)
    # normalized = re.sub(r'var kjkOT = \{.*?\};', 'var kjkOT = {SECURITY_TOKENS};', normalized, flags=re.DOTALL)

    # 7. JavaScript 변수 내 날짜/시간 값 정규화 (예: var talkStdYmd = '20250716';)
    # `(?:
\d{6})?` 부분의 괄호 오류 수정
    normalized = re.sub(r'(var\s+\w+\s*=\s*[""])\d{8}(?:\d{6})?([""])', r'\1DATE_VALUE\2', normalized) # YYYYMMDD or YYYYMMDDHHMMSS
    normalized = re.sub(r'(var\s+\w+\s*=\s*[""])\d{4}\.\d{2}\.\d{2}([""])', r'\1DATE_VALUE\2', normalized) # YYYY.MM.DD
    normalized = re.sub(r'(value=[""])\d{14}([""])', r'\1DATETIME_VALUE\2', normalized) # YYYYMMDDHHMMSS (dateCheck)

    # 8. JavaScript 변수 내 IP 주소 정규화 (예: var remoteAddr = "211.106.8.234";)
    # normalized = re.sub(r'(var\s+\w+\s*=\s*[""])\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}([""])', r'\1IP_ADDRESS\2', normalized)

    # 9. JavaScript 변수 내 API 키/플러그인 키 정규화 (예: "pluginKey": "UUID", "apiKey": "API_KEY")
    # normalized = re.sub(r'("pluginKey"\s*:\s*[""])[a-f0-9-]{36}([""])', r'\1PLUGIN_KEY\2', normalized)
    # normalized = re.sub(r'("apiKey"\s*:\s*[""])[a-f0-9]{64}([""])', r'\1API_KEY\2', normalized)
    normalized = re.sub(r'(var\s+TNK_SR\s*=\s*[""])[a-f0-9]{32}([""])', r'\1TNK_SR_TOKEN\2', normalized) # TNK_SR
    # normalized = re.sub(r'(_inihubClientId\s*=\s*[""])[a-f0-9-]{36}([""])', r'\1INIHUB_CLIENT_ID\2', normalized) # _inihubClientId
    # normalized = re.sub(r'(_kakaoKey\s*=\s*[""])[a-f0-9]{32}([""])', r'\1KAKAO_KEY\2', normalized) # _kakaoKey
    # normalized = re.sub(r'(adbrix_appkey\s*=\s*[""])[a-zA-Z0-9]{20}([""])', r'\1ADBRIX_APPKEY\2', normalized) # adbrix_appkey
    # normalized = re.sub(r'(adbrix_webSecretkey\s*=\s*[""])[a-zA-Z0-9]{20}([""])', r'\1ADBRIX_WEBSECRETKEY\2', normalized) # adbrix_webSecretkey
    # normalized = re.sub(r'(let\s+nth_sid\s*=\s*[""])\d+([""])', r'\1NTH_SID\2', normalized) # nth_sid

    # 10. 암호화 관련 동적 값 정규화
    # normalized = re.sub(r'(CryptoJS\.\enc\.\Latin1\.parse\(\s*[""])[a-f0-9]{16,32}([""]\s*\))', r'\1ENCRYPTION_KEY\2', normalized) # CryptoJS key/iv
    normalized = re.sub(r'(fncAesEnc\(["])[a-zA-Z0-9+/=]{20,}([""]\))', r'\1ENCRYPTED_DATA\2', normalized) # fncAesEnc
    # normalized = re.sub(r'(new\s+Date\(\)\.getTime\(\))', r'DYNAMIC_TIMESTAMP_CALL', normalized) # new Date().getTime()
    # normalized = re.sub(r'(ran_gen\(\))', r'RANDOM_GENERATOR_CALL', normalized) # ran_gen()

    # 11. gitple-loader-frame의 title 속성 변경 (한글 깨짐 방지)
    normalized = re.sub(r'title=""', 'title="Channel chat"', normalized)
    
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