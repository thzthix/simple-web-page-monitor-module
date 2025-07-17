#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
텍스트 직접 비교 vs 해시 비교 테스트
두 방식이 동일한 결과를 보이는지 확인
"""

import hashlib
import time

def is_html_changed_direct(html1: str, html2: str) -> bool:
    """텍스트 직접 비교"""
    return html1 != html2

def is_html_changed_hash(html1: str, html2: str) -> bool:
    """해시 비교"""
    hash1 = hashlib.sha256(html1.encode('utf-8')).hexdigest()
    hash2 = hashlib.sha256(html2.encode('utf-8')).hexdigest()
    return hash1 != hash2

def test_comparison_methods():
    """두 비교 방식 테스트"""
    print("🧪 텍스트 직접 비교 vs 해시 비교 테스트")
    print("=" * 50)
    
    # 테스트 케이스들
    test_cases = [
        ("<html><body>Hello</body></html>", "<html><body>Hello</body></html>", "동일한 HTML"),
        ("<html><body>Hello</body></html>", "<html><body>World</body></html>", "다른 텍스트"),
        ("<html><body>Hello</body></html>", "<html><body>Hello</body></html> ", "공백 차이"),
        ("<html><body>Hello</body></html>", "<html><body>Hello</body></html>", "완전 동일"),
    ]
    
    results = []
    
    for html1, html2, description in test_cases:
        print(f"\n📋 {description}")
        print("-" * 30)
        
        # 직접 비교
        direct_result = is_html_changed_direct(html1, html2)
        
        # 해시 비교
        hash_result = is_html_changed_hash(html1, html2)
        
        # 해시값 출력
        hash1 = hashlib.sha256(html1.encode('utf-8')).hexdigest()
        hash2 = hashlib.sha256(html2.encode('utf-8')).hexdigest()
        
        print(f"  직접 비교 결과: {'다름' if direct_result else '동일'}")
        print(f"  해시 비교 결과: {'다름' if hash_result else '동일'}")
        print(f"  원본 해시: {hash1[:16]}...")
        print(f"  비교 해시: {hash2[:16]}...")
        
        # 결과 일치 확인
        if direct_result == hash_result:
            print("  ✅ 결과 일치")
            status = "성공"
        else:
            print("  ❌ 결과 불일치")
            status = "실패"
        
        results.append({
            'description': description,
            'direct_result': direct_result,
            'hash_result': hash_result,
            'status': status
        })
    
    # 성능 테스트
    print(f"\n📊 성능 테스트")
    print("-" * 30)
    
    # 큰 HTML 문자열 생성
    large_html1 = "<html><body>" + "Hello World " * 10000 + "</body></html>"
    large_html2 = "<html><body>" + "Hello World " * 10000 + "</body></html>"
    
    # 직접 비교 시간 측정
    start_time = time.time()
    for _ in range(100):
        is_html_changed_direct(large_html1, large_html2)
    direct_time = time.time() - start_time
    
    # 해시 비교 시간 측정
    start_time = time.time()
    for _ in range(100):
        is_html_changed_hash(large_html1, large_html2)
    hash_time = time.time() - start_time
    
    print(f"  직접 비교 시간: {direct_time:.4f}초")
    print(f"  해시 비교 시간: {hash_time:.4f}초")
    print(f"  성능 차이: {direct_time/hash_time:.1f}배")
    
    # 결과 요약
    print(f"\n📈 테스트 결과 요약")
    print("=" * 50)
    
    success_count = sum(1 for r in results if r['status'] == "성공")
    print(f"결과 일치: {success_count}/{len(results)}")
    
    if success_count == len(results):
        print("🎉 모든 테스트에서 두 방식이 동일한 결과를 보입니다!")
    else:
        print("⚠️  일부 테스트에서 결과가 다릅니다.")

if __name__ == "__main__":
    test_comparison_methods() 