import requests

def fetch_page(url):
    """
    주어진 URL에서 HTML 페이지를 가져옵니다.
    실패 시 None 반환.
    """
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
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # HTML 크기 제한 (10MB)
        if len(response.content) > 10 * 1024 * 1024:
            print("HTML이 너무 큽니다 (10MB 초과)")
            return None
            
        return response.text
    except Exception as e:
        print(f"페이지 가져오기 실패: {e}")
        return None 