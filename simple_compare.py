#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
단순 HTML 변경 비교 모듈
두 HTML 문자열이 해시(SHA256) 기준으로 동일한지(변경 여부만) 판단합니다.
"""

import hashlib

def is_html_changed(html1: str, html2: str) -> bool:
    """
    두 HTML 문자열의 SHA256 해시가 동일한지 비교 (True면 변경됨, False면 동일)
    """
    hash1 = hashlib.sha256(html1.encode('utf-8')).hexdigest()
    hash2 = hashlib.sha256(html2.encode('utf-8')).hexdigest()
    return hash1 != hash2 