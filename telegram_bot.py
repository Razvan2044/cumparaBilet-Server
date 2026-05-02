import os
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Incarcam secretele din fisierul .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_CHAT_ID")

DB_NAME = "bilete_bot.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Raspunde cand un user da /start."""
    user_id = str(update.message.chat_id)
    nume = update.message.from_user.first_name

    # Inregistram userul in baza de date (sau ignoram daca exista deja)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO users (chat_id, nume) VALUES (?, ?)", (user_id, nume))
        conn.commit()
    except Exception as e:
        print(f"Eroare la inregistrare user: {e}")
    finally:
        conn.close()

    mesaj = f"Salutare, {nume}! 👋\n\nEu sunt asistentul tau VIP pentru bilete.\n\n"
    mesaj += "Foloseste comanda /adauga <URL_iaBilet> pentru a monitoriza un eveniment."
    
    await update.message.reply_text(mesaj)

async def adauga_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comanda pentru a adauga un link de iabilet la monitorizare."""
    user_id = str(update.message.chat_id)
    
    if not context.args:
        await update.message.reply_text("Te rog sa trimiti si link-ul. Ex: /adauga https://www.iabilet.ro/bilete-...")
        return
        
    url_primit = context.args[0]
    
    if "iabilet.ro" not in url_primit:
        await update.message.reply_text("Te rog sa trimiti un link valid de pe iaBilet.ro.")
        return

    # Aici adaugam logica de salvare in DB. Pentru moment, doar extragem un titlu generic.
    titlu_provizoriu = url_primit.split('/')[-2].replace('-', ' ').title() if url_primit.endswith('/') else url_primit.split('/')[-1].replace('-', ' ').title()

    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Bagam evenimentul in tabela 'events' (daca nu exista deja)
        cursor.execute("INSERT OR IGNORE INTO events (title, url) VALUES (?, ?)", (titlu_provizoriu, url_primit))
        
        # Luam ID-ul evenimentului (fie ca abia a fost inserat, fie ca exista deja)
        cursor.execute("SELECT id FROM events WHERE url = ?", (url_primit,))
        event_id = cursor.fetchone()[0]

        # 2. Legam userul de acest eveniment in tabela 'subscriptions'
        cursor.execute("INSERT OR IGNORE INTO subscriptions (user_id, event_id) VALUES (?, ?)", (user_id, event_id))
        
        conn.commit()
        await update.message.reply_text(f"✅ Am adaugat la monitorizare:\n🎭 {titlu_provizoriu}\n\nVei fi notificat cand apar bilete!")
    except Exception as e:
        await update.message.reply_text("❌ A aparut o eroare la salvarea in baza de date.")
        print(f"Eroare adaugare DB: {e}")
    finally:
        conn.close()

def main():
    """Functia principala care porneste botul."""
    print("Se porneste botul de Telegram... (Asteapta comenzi)")
    
    # Construim aplicatia botului
    app = Application.builder().token(TOKEN).build()

    # Adaugam handler-ele pentru comenzi
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("adauga", adauga_command))

    # Pornim bucla (Long Polling)
    app.run_polling()

if __name__ == "__main__":
    main()