#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 파일 비교 유틸리티
"""

import difflib
import re

def read_html_file(filename):
    """HTML 파일을 읽어서 내용을 반환"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        # print(f"파일 읽기 오류 {filename}: {e}") # 로그로 대체
        return None

def find_differences(html1, html2, label1, label2):
    """두 HTML 내용의 차이점을 찾아서 문자열로 반환"""
    diff_output = []
    diff_output.append(f"\n=== {label1} vs {label2} 비교 ===")
    
    if html1 == html2:
        diff_output.append("완전히 동일합니다.")
        return "\n".join(diff_output)
    
    # 라인별로 분할
    lines1 = html1.splitlines()
    lines2 = html2.splitlines()
    
    # unified diff 생성
    diff = list(difflib.unified_diff(
        lines1, lines2, 
        fromfile=label1, tofile=label2, 
        lineterm='', n=3
    ))
    
    if diff:
        diff_output.append("차이점 발견:")
        for line in diff[:50]:  # 처음 50줄만 출력
            diff_output.append(line)
        if len(diff) > 50:
            diff_output.append(f"... (총 {len(diff)}개 라인 중 처음 50개만 표시)")
    else:
        diff_output.append("라인별 차이는 없지만 전체 내용이 다릅니다.")
    
    # 문자 단위 차이점 찾기
    if len(html1) != len(html2):
        diff_output.append(f"길이 차이: {label1}={len(html1)} vs {label2}={len(html2)}")

    return "\n".join(diff_output)

def extract_dynamic_elements(html):
    """동적 요소들을 추출해서 표시"""
    # 타임스탬프 패턴
    timestamps = re.findall(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}', html)
    
    # 세션 ID나 토큰 패턴 (예시)
    session_patterns = re.findall(r'session[_-]?id["\s]*[:=]["\s]*([a-zA-Z0-9]+)', html, re.IGNORECASE)
    token_patterns = re.findall(r'token["\s]*[:=]["\s]*([a-zA-Z0-9]+)', html, re.IGNORECASE)
    
    # CSRF 토큰
    csrf_patterns = re.findall(r'csrf[_-]?token["\s]*[:=]["\s]*([a-zA-Z0-9]+)', html, re.IGNORECASE)
    
    return {
        'timestamps': timestamps,
        'sessions': session_patterns,
        'tokens': token_patterns,
        'csrf': csrf_patterns
    }