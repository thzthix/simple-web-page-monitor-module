import requests

def fetch_page(url):
    """
    주어진 URL에서 HTML 페이지를 가져옵니다.
    실패 시 None 반환.
    """
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"페이지 가져오기 실패: {e}")
        return None 