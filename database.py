#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터베이스 관리 모듈
SQLite 데이터베이스와 관련된 모든 기능을 담당합니다.
"""

import sqlite3
from datetime import datetime
from config.config import DATABASE_PATH

def setup_database():
    """Initializes the database and creates the snapshots table if it doesn't exist."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            url TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            html_content TEXT NOT NULL,
            html_size INTEGER,
            change_detected BOOLEAN DEFAULT FALSE,
            change_details TEXT
        )
        """)
        conn.commit()

def get_latest_snapshot(url):
    """Retrieves the most recent snapshot for a given URL from the database."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT timestamp, content_hash, html_content, html_size FROM snapshots WHERE url = ? ORDER BY timestamp DESC LIMIT 1",
            (url,)
        )
        result = cursor.fetchone()
        if result:
            return {
                "timestamp": result[0],
                "hash": result[1],
                "html_content": result[2],
                "html_size": result[3]
            }
        return None

 