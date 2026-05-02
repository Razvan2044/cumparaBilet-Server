import sqlite3

def init_db():
    conn = sqlite3.connect("bilete_bot.db")
    cursor = conn.cursor()

    # Tabelul care tine evidenta cautarilor
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trackers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            keyword TEXT,
            status TEXT DEFAULT 'ASTEPTARE',
            data_adaugare DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Noua baza de date (bazata pe cuvinte cheie) a fost creata!")

if __name__ == "__main__":
    init_db()