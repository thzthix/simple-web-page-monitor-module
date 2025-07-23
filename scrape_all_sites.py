#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 가져오기 유틸리티 (Playwright 사용)
"""

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def fetch_html_async(url, browser_type="chromium", headless=True):
    """Playwright Stealth를 사용하여 탐지 우회 및 HTML 가져오기 (비동기)"""
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    extra_headers = {
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    try:
        async with async_playwright() as p:
            browser_launcher = getattr(p, browser_type)
            browser = await browser_launcher.launch(headless=headless)
            context = await browser.new_context(
                user_agent=user_agent,
                extra_http_headers=extra_headers
            )
            page = await context.new_page()
            
            # Stealth 기능 적용 - bot 탐지 우회
            stealth = Stealth()
            await stealth.apply_stealth_async(page)
            
            await page.goto(url, wait_until="networkidle")
            html_content = await page.content()
            await browser.close()
            return html_content
    except Exception as e:
        print(f"오류: {e}")
        return None