import sqlite3
import json
from datetime import datetime
from typing import Optional
from src.domain.entities.access_key import AccessKey
from src.domain.interfaces.key_repository import KeyRepository

class SQLiteKeyRepository(KeyRepository):
    def __init__(self, db_path: str = "acessos.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS access_keys (
                    email TEXT NOT NULL,
                    key TEXT PRIMARY KEY,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    ip TEXT
                )
            ''')
    
    def save(self, key: AccessKey) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO access_keys (email, key, created_at, expires_at, used, ip)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                key.email, key.key, key.created_at.isoformat(),
                key.expires_at.isoformat(), key.used, key.ip
            ))
    
    def find_by_key(self, key: str) -> Optional[AccessKey]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT email, key, created_at, expires_at, used, ip
                FROM access_keys WHERE key = ?
            ''', (key,))
            row = cursor.fetchone()
            
        if row:
            return AccessKey(
                email=row[0],
                key=row[1],
                created_at=datetime.fromisoformat(row[2]),
                expires_at=datetime.fromisoformat(row[3]),
                used=bool(row[4]),
                ip=row[5]
            )
        return None
    
    def find_valid_by_email(self, email: str) -> Optional[AccessKey]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT email, key, created_at, expires_at, used, ip
                FROM access_keys 
                WHERE email = ? AND used = 0 AND datetime(expires_at) > datetime('now')
                ORDER BY expires_at DESC LIMIT 1
            ''', (email,))
            row = cursor.fetchone()
            
        if row:
            return AccessKey(
                email=row[0],
                key=row[1],
                created_at=datetime.fromisoformat(row[2]),
                expires_at=datetime.fromisoformat(row[3]),
                used=bool(row[4]),
                ip=row[5]
            )
        return None