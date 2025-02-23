# database.py
import sqlite3

def init_db():
    conn = sqlite3.connect('chats.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            user_id INTEGER PRIMARY KEY,
            chat_data TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_chat(user_id, chat_data):
    conn = sqlite3.connect('chats.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO chats (user_id, chat_data) VALUES (?, ?)', (user_id, chat_data))
    conn.commit()
    conn.close()

def get_chat(user_id):
    conn = sqlite3.connect('chats.db')
    cursor = conn.cursor()
    cursor.execute('SELECT chat_data FROM chats WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else ""
