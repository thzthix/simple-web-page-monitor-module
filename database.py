#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터베이스 관리 모듈
SQLite 데이터베이스와 관련된 모든 기능을 담당합니다.
"""

import sqlite3
from datetime import datetime
from config import DATABASE_PATH

def setup_database():
    """Initializes the database and creates the snapshots table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        url TEXT NOT NULL,
        content_hash TEXT NOT NULL,
        html_content TEXT NOT NULL,
        change_detected BOOLEAN DEFAULT FALSE,
        change_details TEXT
    )
    """)
    conn.commit()
    conn.close()

def get_latest_snapshot(url):
    """Retrieves the most recent snapshot for a given URL from the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp, content_hash, html_content FROM snapshots WHERE url = ? ORDER BY timestamp DESC LIMIT 1",
        (url,)
    )
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "timestamp": result[0],
            "hash": result[1],
            "html_content": result[2]
        }
    return None

def save_snapshot(url, content_hash, html_content, change_detected=False, change_details=None):
    """Saves a new snapshot to the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO snapshots (timestamp, url, content_hash, html_content, change_detected, change_details) VALUES (?, ?, ?, ?, ?, ?)",
        (timestamp, url, content_hash, html_content, change_detected, change_details)
    )
    conn.commit()
    conn.close()
    return timestamp 