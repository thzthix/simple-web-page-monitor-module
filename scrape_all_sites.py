#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 가져오기 유틸리티
"""

import requests

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
        print(f"오류: {e}")
        return None