import sqlite3
import os
from datetime import datetime, date

DB_PATH = os.getenv("DB_PATH", "storage_bot.db")


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                channel_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)
        self.conn.commit()

    def add_user(self, user_id: int, username: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        self.conn.commit()

    def save_file(self, user_id: int, message_id: int, file_name: str,
                  file_type: str, channel_id: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO files (user_id, message_id, file_name, file_type, channel_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, message_id, file_name, file_type, channel_id)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_user_files(self, user_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM files WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_file_by_id(self, file_id: int, user_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM files WHERE id = ? AND user_id = ?",
            (file_id, user_id)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def delete_file(self, file_id: int, user_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM files WHERE id = ? AND user_id = ?",
            (file_id, user_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def get_stats(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users")
        users = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM files")
        files = cursor.fetchone()['count']

        today = date.today().isoformat()
        cursor.execute(
            "SELECT COUNT(*) as count FROM users WHERE DATE(created_at) = ?",
            (today,)
        )
        today_users = cursor.fetchone()['count']

        return {"users": users, "files": files, "today_users": today_users}

    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT u.user_id, u.username,
                   COUNT(f.id) as file_count
            FROM users u
            LEFT JOIN files f ON u.user_id = f.user_id
            GROUP BY u.user_id
            ORDER BY u.created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
