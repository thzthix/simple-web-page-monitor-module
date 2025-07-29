#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 가져오기 유틸리티 (Playwright 사용)
"""

import asyncio
import random
from playwright.async_api import async_playwright
from playwright_stealth import Stealth # Stealth 클래스를 직접 사용한다고 가정

async def fetch_html_async(url, browser_type="chromium", headless=True):
    """
    Playwright Stealth를 사용하여 탐지 우회 및 HTML 가져오기 (비동기)
    CSR 페이지의 경우 정적 HTML과 동적 HTML을 모두 반환합니다.
    """
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    extra_headers = {
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    initial_html = None
    rendered_html = None

    try:
        async with async_playwright() as p:
            browser_launcher = getattr(p, browser_type)
            browser = await browser_launcher.launch(headless=headless)
            
            # 브라우저 컨텍스트 설정 강화: 로케일, 타임존, 뷰포트
            context = await browser.new_context(
                user_agent=user_agent,
                extra_http_headers=extra_headers,
                locale="ko-KR",  # 한국어 로케일 설정
                timezone_id="Asia/Seoul", # 한국 표준시 설정
                viewport={"width": 1920, "height": 1080}, # 일반적인 데스크톱 해상도
            )
            page = await context.new_page()
            
            # Stealth 기능 적용 - bot 탐지 우회
            stealth = Stealth()
            await stealth.apply_stealth_async(page)
            
            # 1. 페이지로 이동하고 초기 HTML(정적) 가져오기
            # timeout을 넉넉하게 설정하여 Eversafe 등의 지연에 대비
            response = await page.goto(url, wait_until="commit", timeout=90000) # commit: 응답 헤더를 받았을 때
            if response:
                initial_html = await response.text() # 초기 응답의 텍스트 (정적 HTML)
            
            # 2. CSR 렌더링 완료를 위한 대기 (networkidle) 후 추가 지연
            # networkidle로 완전히 로드될 때까지 기다림
            await page.wait_for_load_state("networkidle", timeout=90000) 
            # CSR 동작 및 봇 탐지 회피를 위한 추가 무작위 지연
            await asyncio.sleep(random.uniform(3, 8)) 
            
            # 3. 렌더링 완료된 HTML (동적) 가져오기
            rendered_html = await page.content()
            
            return {
                "initial_html": initial_html,
                "rendered_html": rendered_html
            }
            
    except Exception as e:
        print(f"오류 발생: {e}")
        # 오류 발생 시에도 어떤 HTML이든 가져온 것이 있다면 반환
        return {
            "initial_html": initial_html,
            "rendered_html": rendered_html
        }
    finally:
        if 'browser' in locals() and browser:
            await browser.close()