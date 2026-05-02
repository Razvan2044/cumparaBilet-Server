import os
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DB_NAME = "bilete_bot.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nume = update.message.from_user.first_name
    mesaj = f"Salutare, {nume}! 👋\n\nSunt radarul tau pentru bilete in Bucuresti.\n\n"
    mesaj += "🟢 Foloseste: /adauga nume eveniment\n"
    mesaj += "🔴 Foloseste: /stop nume eveniment\n"
    await update.message.reply_text(mesaj)

async def adauga_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)
    
    if not context.args:
        await update.message.reply_text("Te rog sa scrii si numele. Ex: /adauga subcarpati")
        return
        
    # Unim cuvintele (in caz ca scrie "/adauga stand up comedy")
    keyword = " ".join(context.args).lower().strip()

    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificam daca il cauta deja
    cursor.execute("SELECT id FROM trackers WHERE user_id = ? AND keyword = ?", (user_id, keyword))
    if cursor.fetchone():
        await update.message.reply_text(f"⚠️ Urmaresti deja evenimentul: {keyword.title()}")
    else:
        cursor.execute("INSERT INTO trackers (user_id, keyword) VALUES (?, ?)", (user_id, keyword))
        conn.commit()
        await update.message.reply_text(f"✅ Am inceput sa caut: 🎭 {keyword.title()}\nTe anunt imediat ce apare pe pagina!")
        
    conn.close()

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)
    
    if not context.args:
        await update.message.reply_text("Te rog sa scrii numele evenimentului pe care vrei sa-l opresti. Ex: /stop subcarpati")
        return
        
    keyword = " ".join(context.args).lower().strip()

    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM trackers WHERE user_id = ? AND keyword = ?", (user_id, keyword))
    if cursor.rowcount > 0:
        await update.message.reply_text(f"🛑 Am oprit cautarea pentru: {keyword.title()}")
    else:
        await update.message.reply_text(f"❌ Nu am gasit '{keyword.title()}' in lista ta activa.")
        
    conn.commit()
    conn.close()

def main():
    print("Se porneste botul de Telegram...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("adauga", adauga_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.run_polling()

if __name__ == "__main__":
    main()