from playwright.sync_api import sync_playwright
import logging
import time

def fetch_page(url):
    """
    주어진 URL에서 HTML 페이지를 가져옵니다.
    실패 시 None 반환.
    """
    # 실제 브라우저와 유사한 헤더 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.kyobobook.co.kr/' # Referer 헤더 추가
    }

    try:
        with sync_playwright() as p:
            # headless 모드로 실행 (필요시 headless=False로 변경하여 디버깅)
            browser = p.chromium.launch(headless=True)
            
            # 새로운 브라우저 컨텍스트 생성 및 User-Agent 설정
            context = browser.new_context(user_agent=headers['User-Agent'], extra_http_headers=headers)
            
            page = context.new_page()
            
            # 페이지 이동 및 네트워크 활동이 없을 때까지 대기
            page.goto(url, wait_until="networkidle") 
            
            # 추가적인 대기 시간 (JavaScript 렌더링 등을 위해)
            time.sleep(3)
            
            html_content = page.content()
            browser.close()

            # HTML 크기 제한 (10MB)
            if len(html_content) > 10 * 1024 * 1024:
                logging.warning(f"HTML이 너무 큽니다 (10MB 초과): {url}")
                return None
            
            return html_content
    except Exception as e:
        logging.error(f"페이지 가져오기 실패: {url}, 오류: {e}")
        return None
