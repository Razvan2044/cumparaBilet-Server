import sqlite3
import os

# Numele fisierului bazei de date (va aparea in folderul tau)
DB_NAME = "bilete_bot.db"

def get_connection():
    """Deschide o conexiune catre seiful SQLite."""
    return sqlite3.connect(DB_NAME)

def init_db():
    """Construieste tabelele (arhitectura) daca nu exista deja."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Tabela EVENTS (Tine evidenta link-urilor unice pe care le scaneaza robotul)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'NEVERIFICAT',
            last_checked DATETIME
        )
    ''')

    # 2. Tabela USERS (Tine evidenta clientilor tai de pe Telegram)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            chat_id TEXT PRIMARY KEY,
            nume TEXT,
            data_inregistrare DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Tabela SUBSCRIPTIONS (Leaga clientul de evenimentul pe care il urmareste)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id TEXT,
            event_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(chat_id),
            FOREIGN KEY(event_id) REFERENCES events(id),
            PRIMARY KEY (user_id, event_id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Baza de date SQLite a fost initializata cu succes!")

# Acest bloc ruleaza doar cand dai Run la acest fisier
if __name__ == "__main__":
    print("Se construieste baza de date...")
    init_db()