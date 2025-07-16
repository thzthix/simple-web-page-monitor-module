#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
보안 객체의 키와 값을 더 정확히 분석하는 스크립트
"""

import os
import re
from collections import defaultdict

def extract_security_object_raw(html_content):
    """HTML에서 보안 객체를 원시 형태로 추출"""
    # var 객체명 = {내용} 패턴 찾기 (중괄호 매칭 개선)
    pattern = r'var\s+([a-zA-Z0-9]+)\s*=\s*(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})'
    matches = re.findall(pattern, html_content, re.DOTALL)
    
    if matches:
        # 가장 긴 객체를 보안 객체로 간주
        security_obj = max(matches, key=lambda x: len(x[1]))
        return security_obj[0], security_obj[1]
    
    return None, None

def parse_js_object_keys(obj_str):
    """JavaScript 객체에서 키 목록 추출"""
    # "키": 또는 키: 패턴으로 키 추출
    key_pattern = r'["\']?([a-zA-Z0-9_]+)["\']?\s*:'
    keys = re.findall(key_pattern, obj_str)
    return sorted(set(keys))

def parse_js_object_key_values(obj_str):
    """JavaScript 객체에서 키-값 쌍 추출 (값의 앞부분만)"""
    # 키:값 패턴 추출 (값은 처음 50자만)
    kv_pattern = r'["\']?([a-zA-Z0-9_]+)["\']?\s*:\s*["\']?([^,}\n]{1,50})'
    matches = re.findall(kv_pattern, obj_str)
    
    result = {}
    for key, value in matches:
        # 값이 너무 길면 자르기
        if len(value) > 50:
            value = value[:47] + "..."
        # 따옴표 제거
        value = value.strip('"\'')
        result[key] = value
    
    return result

def analyze_date_folder_detailed(folder_path):
    """특정 날짜 폴더의 모든 스냅샷 상세 분석"""
    html_files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
    html_files.sort()
    
    results = []
    for filename in html_files:
        filepath = os.path.join(folder_path, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        var_name, obj_str = extract_security_object_raw(content)
        if var_name and obj_str:
            keys = parse_js_object_keys(obj_str)
            key_values = parse_js_object_key_values(obj_str)
            
            results.append({
                'file': filename,
                'var_name': var_name,
                'keys': keys,
                'key_values': key_values,
                'obj_length': len(obj_str)
            })
    
    return results

def compare_detailed(date_results, date_name):
    """상세 비교 분석"""
    if not date_results:
        return
    
    print(f"📅 {date_name} ({len(date_results)}개 스냅샷)")
    
    # 변수명 확인
    var_names = set(r['var_name'] for r in date_results)
    print(f"  🏷️  변수명: {list(var_names)}")
    
    if len(date_results) == 1:
        result = date_results[0]
        print(f"  🔑 키 개수: {len(result['keys'])}")
        print(f"  📝 키 목록: {result['keys'][:10]}{'...' if len(result['keys']) > 10 else ''}")
        return
    
    # 키 구조 비교
    first_keys = set(date_results[0]['keys'])
    keys_identical = all(set(r['keys']) == first_keys for r in date_results[1:])
    
    print(f"  🔑 키 개수: {len(first_keys)}")
    print(f"  📝 키 구조 동일: {'✅' if keys_identical else '❌'}")
    
    if not keys_identical:
        for i, result in enumerate(date_results):
            print(f"    {result['file']}: {len(result['keys'])}개 키")
    
    # 값 변화 분석 (첫 번째와 마지막 비교)
    if len(date_results) >= 2:
        first_kv = date_results[0]['key_values']
        last_kv = date_results[-1]['key_values']
        
        changed_keys = []
        unchanged_keys = []
        
        for key in first_keys:
            if key in first_kv and key in last_kv:
                if first_kv[key] != last_kv[key]:
                    changed_keys.append(key)
                else:
                    unchanged_keys.append(key)
        
        print(f"  🔄 값 변화: {len(changed_keys)}개 키 변경, {len(unchanged_keys)}개 키 동일")
        
        if changed_keys:
            print(f"  📊 변경된 키들: {changed_keys[:5]}{'...' if len(changed_keys) > 5 else ''}")
            
            # 몇 개 키의 변화 예시 보여주기
            for key in changed_keys[:3]:
                first_val = first_kv.get(key, '')[:20]
                last_val = last_kv.get(key, '')[:20]
                print(f"    {key}: '{first_val}...' → '{last_val}...'")

def main():
    """메인 함수"""
    date_folders = [d for d in os.listdir('.') if d.startswith('snapshots_2025-')]
    date_folders.sort()
    
    print("🔍 보안 객체 상세 분석\n")
    
    for folder in date_folders:
        if os.path.isdir(folder):
            date_results = analyze_date_folder_detailed(folder)
            compare_detailed(date_results, folder)
        print()

if __name__ == "__main__":
    main()