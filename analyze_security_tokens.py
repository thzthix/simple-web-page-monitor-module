#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
각 날짜별 스냅샷들의 보안 객체 키와 값 일치성을 분석하는 스크립트
"""

import os
import re
import json
from collections import defaultdict

def extract_security_object(html_content):
    """HTML에서 보안 객체를 추출"""
    # var 객체명 = {내용} 패턴 찾기
    pattern = r'var\s+([a-zA-Z0-9]+)\s*=\s*(\{[^}]+\})'
    matches = re.findall(pattern, html_content)
    
    if matches:
        # 가장 긴 객체를 보안 객체로 간주 (보통 보안 객체가 가장 큼)
        security_obj = max(matches, key=lambda x: len(x[1]))
        var_name = security_obj[0]
        
        # JSON 파싱 시도
        try:
            # JavaScript 객체를 JSON으로 변환하기 위한 간단한 처리
            obj_str = security_obj[1]
            # 키에 따옴표가 없으면 추가
            obj_str = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+):', r'\1"\2":', obj_str)
            obj_data = json.loads(obj_str)
            return var_name, obj_data
        except:
            # JSON 파싱 실패 시 원본 문자열 반환
            return var_name, security_obj[1]
    
    return None, None

def analyze_date_folder(folder_path):
    """특정 날짜 폴더의 모든 스냅샷 분석"""
    html_files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
    html_files.sort()  # 시간순 정렬
    
    results = []
    for filename in html_files:
        filepath = os.path.join(folder_path, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        var_name, obj_data = extract_security_object(content)
        results.append({
            'file': filename,
            'var_name': var_name,
            'obj_data': obj_data,
            'obj_keys': list(obj_data.keys()) if isinstance(obj_data, dict) else None
        })
    
    return results

def compare_within_date(date_results):
    """같은 날짜 내 스냅샷들 비교"""
    if not date_results:
        return
    
    # 변수명 비교
    var_names = [r['var_name'] for r in date_results]
    unique_var_names = set(var_names)
    
    print(f"  변수명: {unique_var_names}")
    if len(unique_var_names) == 1:
        print("  ✅ 모든 스냅샷이 동일한 변수명 사용")
    else:
        print("  ❌ 변수명이 다름!")
        for i, result in enumerate(date_results):
            print(f"    {result['file']}: {result['var_name']}")
    
    # 키 구조 비교 (dict인 경우만)
    dict_results = [r for r in date_results if isinstance(r['obj_data'], dict)]
    if dict_results:
        first_keys = set(dict_results[0]['obj_keys'])
        keys_identical = True
        
        for result in dict_results[1:]:
            if set(result['obj_keys']) != first_keys:
                keys_identical = False
                break
        
        print(f"  키 개수: {len(first_keys)}")
        print(f"  키 목록: {sorted(first_keys)}")
        
        if keys_identical:
            print("  ✅ 모든 스냅샷이 동일한 키 구조 사용")
        else:
            print("  ❌ 키 구조가 다름!")
            for result in dict_results:
                print(f"    {result['file']}: {sorted(result['obj_keys'])}")
        
        # 값 비교 (첫 번째와 마지막만)
        if len(dict_results) > 1:
            first_obj = dict_results[0]['obj_data']
            last_obj = dict_results[-1]['obj_data']
            
            values_identical = True
            different_keys = []
            
            for key in first_keys:
                if first_obj.get(key) != last_obj.get(key):
                    values_identical = False
                    different_keys.append(key)
            
            if values_identical:
                print("  ✅ 첫 번째와 마지막 스냅샷의 모든 값이 동일")
            else:
                print(f"  ❌ {len(different_keys)}개 키의 값이 다름: {different_keys}")

def main():
    """메인 함수"""
    date_folders = [d for d in os.listdir('.') if d.startswith('snapshots_2025-')]
    date_folders.sort()
    
    print("📊 날짜별 보안 객체 분석\n")
    
    for folder in date_folders:
        print(f"📅 {folder}:")
        if os.path.isdir(folder):
            date_results = analyze_date_folder(folder)
            compare_within_date(date_results)
        print()

if __name__ == "__main__":
    main()