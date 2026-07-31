import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            language TEXT DEFAULT 'ar',
            balance REAL DEFAULT 0.0,
            status TEXT DEFAULT 'inactive',
            created_date TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            type TEXT,
            amount REAL,
            method TEXT,
            status TEXT DEFAULT 'pending',
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(telegram_id: int, username: str, password_raw: str, language: str = 'ar'):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    hashed_pwd = hash_password(password_raw)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT OR REPLACE INTO users (telegram_id, username, password, language, balance, status, created_date)
        VALUES (?, ?, ?, ?, 0.0, 'inactive', ?)
    ''', (telegram_id, username, hashed_pwd, language, now))
    conn.commit()
    conn.close()

def get_user(telegram_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id, username, password, language, balance, status, created_date FROM users WHERE telegram_id = ?", (telegram_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'telegram_id': row[0],
            'username': row[1],
            'password': row[2],
            'language': row[3],
            'balance': row[4],
            'status': row[5],
            'created_date': row[6]
        }
    return None

def set_user_language(telegram_id: int, lang: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET language = ? WHERE telegram_id = ?", (lang, telegram_id))
    conn.commit()
    conn.close()

def update_user_status(telegram_id: int, status: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = ? WHERE telegram_id = ?", (status, telegram_id))
    conn.commit()
    conn.close()

def update_user_balance(telegram_id: int, amount: float):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE telegram_id = ?", (amount, telegram_id))
    conn.commit()
    conn.close()

def add_transaction(telegram_id: int, tx_type: str, amount: float, method: str) -> int:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO transactions (telegram_id, type, amount, method, status, date)
        VALUES (?, ?, ?, ?, 'pending', ?)
    ''', (telegram_id, tx_type, amount, method, now))
    tx_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return tx_id

def update_transaction_status(tx_id: int, status: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE transactions SET status = ? WHERE id = ?", (status, tx_id))
    conn.commit()
    conn.close()

def get_transaction(tx_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, telegram_id, type, amount, method, status, date FROM transactions WHERE id = ?", (tx_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'telegram_id': row[1], 'type': row[2], 'amount': row[3], 'method': row[4], 'status': row[5], 'date': row[6]}
    return None

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id, username, balance, status FROM users")
    rows = cursor.fetchall()
    conn.close()
    return rows
  
