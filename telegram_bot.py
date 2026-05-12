import os
import sqlite3
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Incarcam variabilele de mediu
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DB_NAME = "iaBilet_SaaS.db"

# Configurare minima pentru logging in consola (pentru debug)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def get_connection():
    return sqlite3.connect(DB_NAME)

def log_system_event(event_msg):
    """
    Salveaza evenimentele de sistem in consola si poate fi extins 
    pentru baza de date, conform sectiunii de Telemetrie.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [SYSTEM] {event_msg}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nume = update.message.from_user.first_name
    mesaj = f"Salutare, {nume}! 👋\n\nSunt radarul tau centralizat [SaaS Ready].\n\n"
    mesaj += "🟢 /adauga nume eveniment\n"
    mesaj += "🔴 /stop nume eveniment"
    await update.message.reply_text(mesaj)

async def adauga_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)
    if not context.args:
        await update.message.reply_text("Te rog sa scrii si numele. Ex: /adauga subcarpati")
        return
        
    keyword = " ".join(context.args).lower().strip()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM trackers WHERE user_id = ? AND keyword = ?", (user_id, keyword))
    if cursor.fetchone():
        await update.message.reply_text(f"⚠️ Urmaresti deja: {keyword.title()}")
    else:
        cursor.execute("INSERT INTO trackers (user_id, keyword) VALUES (?, ?)", (user_id, keyword))
        conn.commit()
        await update.message.reply_text(f"✅ Am inceput monitorizarea pentru: 🎭 {keyword.title()}")
        
    conn.close()

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)
    if not context.args:
        await update.message.reply_text("Ex: /stop subcarpati")
        return
        
    keyword = " ".join(context.args).lower().strip()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM trackers WHERE user_id = ? AND keyword = ?", (user_id, keyword))
    if cursor.rowcount > 0:
        await update.message.reply_text(f"🛑 Am oprit cautarea pentru: {keyword.title()}")
    else:
        await update.message.reply_text(f"❌ Nu am gasit '{keyword.title()}' in lista ta.")
        
    conn.commit()
    conn.close()

def main():
    log_system_event("Initializare Bot Telegram...")
    
    app = Application.builder().token(TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("adauga", adauga_command))
    app.add_handler(CommandHandler("stop", stop_command))
    
    print("Se porneste botul de Telegram...")
    
    try:
        # Porneste botul si asculta pana la oprirea manuala
        app.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        # Aici prindem momentul in care apesi Ctrl+C
        log_system_event("⚠️ BOT OPRIT MANUAL (KeyboardInterrupt / Ctrl+C)[cite: 2]")
    except Exception as e:
        log_system_event(f"❌ EROARE CRITICA: {e}")
    finally:
        log_system_event("Inchidere conexiuni si curatare sesiune...[cite: 2]")

if __name__ == "__main__":
    main()