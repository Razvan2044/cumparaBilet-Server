import undetected_chromedriver as uc
import sqlite3
import time
import random
import requests
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DB_NAME = "bilete_bot.db"
PAGINA_TINTA = "https://www.iabilet.ro/bilete-in-bucuresti/"

def get_connection():
    return sqlite3.connect(DB_NAME)

def trimite_notificare(chat_id, keyword):
    mesaj = f"🚨 ALARMA DE BILETE! 🚨\n\n🎭 A aparut: {keyword.title()}\n🎟️ Fugi si verifica pagina:\n{PAGINA_TINTA}"
    url_api = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url_api, json={"chat_id": chat_id, "text": mesaj})
    except Exception as e:
        print(f"Eroare Telegram: {e}")

def setup_browser():
    print("🤖 Se incalzeste motorul invizibil...")
    options = uc.ChromeOptions()
    options.add_argument('--disable-popup-blocking')
    driver = uc.Chrome(options=options, version_main=147)
    return driver

def run_scraper():
    driver = setup_browser()
    
    try:
        while True:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Luam toate cautarile active
            cursor.execute("SELECT id, user_id, keyword FROM trackers WHERE status = 'ASTEPTARE'")
            cautari_active = cursor.fetchall()
            
            if not cautari_active:
                print("💤 Nimeni nu cauta nimic momentan. Astept...")
                time.sleep(10)
            else:
                print(f"🔍 Scanez pagina uriasa pentru {len(cautari_active)} cuvinte cheie...")
                
                # 1. Incarcam pagina O SINGURA DATA
                driver.get(PAGINA_TINTA)
                
                # Scroll in jos ca sa fim siguri ca se incarca toate evenimentele ascunse (Lazy load)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3) # Asteptam sa apara textul
                
                # Luam absolut tot textul din pagina
                page_text = driver.execute_script("return document.body.innerText").lower()
                
                # 2. Verificam fiecare cuvant
                for row_id, user_id, keyword in cautari_active:
                    if keyword in page_text:
                        print(f"🎉 BINGO! Am gasit '{keyword}' pe pagina!")
                        trimite_notificare(user_id, keyword)
                        
                        # Il marcam ca GASIT ca sa nu il mai spameze cu mesaje
                        cursor.execute("UPDATE trackers SET status = 'GASIT' WHERE id = ?", (row_id,))
                        conn.commit()
                
            conn.close()
            
            print("🔄 Ciclu terminat. Pauza de 1 minut pentru siguranta...")
            time.sleep(60) 
            
    except KeyboardInterrupt:
        print("\n🛑 Oprit.")
    finally:
        driver.quit()

if __name__ == '__main__':
    run_scraper()