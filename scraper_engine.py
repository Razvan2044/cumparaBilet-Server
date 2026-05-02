import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import sqlite3
import time
import random
import math

DB_NAME = "bilete_bot.db"

def get_connection():
    """Conectare la seiful SQLite."""
    return sqlite3.connect(DB_NAME)

def human_delay(mean=2.0, sd=0.5):
    """Functia noastra geniala de Log-Normal Jitter din JavaScript, tradusa in Python!"""
    u = 1.0 - random.random()
    v = random.random()
    z = math.sqrt(-2.0 * math.log(u)) * math.cos(2.0 * math.pi * v)
    delay = math.exp(mean + sd * z)
    return max(1.0, delay)

def setup_browser():
    """Pregatim browser-ul anti-detect."""
    print("🤖 Se incalzeste motorul invizibil (Chrome Stealth)...")
    options = uc.ChromeOptions()
    # options.add_argument('--headless') # Daca scoti '#', browserul va rula 100% in fundal
    options.add_argument('--disable-popup-blocking')
    
    # Pornim browser-ul
    driver = uc.Chrome(options=options, version_main=147)
    driver.set_window_size(1280, 800)
    return driver

def check_event(driver, url):
    """Scaneaza pagina exact cum o facea v4.21."""
    print(f"🔍 Navighez catre: {url}")
    try:
        driver.get(url)
        # Asteptam sa se incarce natural (Log-Normal Delay)
        time.sleep(human_delay(2.5, 0.4)) 
        
        # Extragem tot textul vizibil din pagina, normalizat la litere mici
        page_text = driver.execute_script("return document.body.innerText").lower()

        # 1. Verificam daca e epuizat (Regula din v4.21)
        if "stoc de bilete epuizat" in page_text or "acest eveniment a fost anulat" in page_text:
            return "EPUIZAT"

        # 2. Verificam daca gasim cuvintele magice
        if "comanda bilete" in page_text or "cumpara bilete" in page_text or "ia bilet" in page_text:
            return "DISPONIBIL"

        # 3. Verificam iFrame-urile de ticketing hibride
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            src = iframe.get_attribute("src")
            if src and not any(x in src.lower() for x in ["youtube", "facebook", "google", "doubleclick"]):
                return "DISPONIBIL" # Am gasit un widget de bilete!

        return "ASTEPTARE" # Nu s-a gasit butonul, deci biletele inca nu au aparut
        
    except Exception as e:
        print(f"⚠️ Eroare la accesarea {url}: {e}")
        return "EROARE"

def run_scraper():
    """Bucla infinita care monitorizeaza 24/7."""
    driver = setup_browser()
    
    try:
        while True:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Cautam in baza de date link-urile pe care utilizatorii vor sa le monitorizam
            cursor.execute("SELECT id, title, url FROM events")
            events = cursor.fetchall()
            
            if not events:
                print("💤 Nu am nicio comanda in baza de date. Astept 10 secunde...")
                time.sleep(10)
            else:
                for event_id, title, url in events:
                    status = check_event(driver, url)
                    print(f"📊 Status [{title}]: {status}")
                    
                    # Actualizam statusul in baza de date
                    cursor.execute("UPDATE events SET status = ?, last_checked = CURRENT_TIMESTAMP WHERE id = ?", (status, event_id))
                    conn.commit()
                    
                    # Pauza umana inainte de a trece la urmatorul link din lista
                    pauza = human_delay(2.0, 0.5)
                    print(f"⏳ Anti-detect pauza: {pauza:.2f}s...")
                    time.sleep(pauza)
                    
            conn.close()
            
            # Pauza masiva la finalul ciclului (Pentru a proteja IP-ul tau de Cloudflare Ban)
            print("🔄 Ciclu terminat. Pauza de 2 minute inainte de runda urmatoare...")
            time.sleep(120) 
            
    except KeyboardInterrupt:
        print("\n🛑 Scraper oprit manual de catre admin.")
    finally:
        driver.quit()

# O cerinta obligatorie pentru undetected-chromedriver in Windows
if __name__ == '__main__':
    run_scraper()