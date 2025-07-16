print('start')
import sqlite3
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM snapshots")
count = cursor.fetchone()[0]
print(f"snapshots 테이블에 저장된 행 개수: {count}")

conn.close() 