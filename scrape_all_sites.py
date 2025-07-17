#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 가져오기 유틸리티 (Playwright 사용)
"""

from playwright.sync_api import sync_playwright

def fetch_html(url):
    """Playwright를 사용하여 HTML 가져오기"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True) # 헤드리스 모드
            page = browser.new_page()
            page.goto(url)
            html_content = page.content()
            browser.close()
            return html_content
    except Exception as e:
        print(f"오류: {e}")
        return None