import time
import pandas as pd
import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def get_driver():
    """
    Cette fonction est le 'Cerveau' qui décide quel Chrome utiliser.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Masque Anti-Robot
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    chrome_options.add_argument(f'user-agent={user_agent}')

    # --- DÉTECTION INTELLIGENTE ---
    
    # 1. On cherche Chromium sur le système (cas du Cloud Streamlit)
    # Sur Debian (Streamlit Cloud), c'est souvent ici :
    chromium_path = shutil.which("chromium") or "/usr/bin/chromium"
    chromedriver_path = shutil.which("chromedriver") or "/usr/bin/chromedriver"

    # Si on trouve les deux fichiers système, on les utilise !
    if os.path.exists(chromium_path) and os.path.exists(chromedriver_path):
        print(f"☁️ Mode Cloud activé. Utilisation de : {chromium_path}")
        chrome_options.binary_location = chromium_path
        service = Service(chromedriver_path)
        return webdriver.Chrome(service=service, options=chrome_options)
    
    # 2. Sinon, on est sûrement sur ton PC Windows (Local)
    else:
        print("💻 Mode Local détecté. Téléchargement du driver...")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

def lancer_recherche_live(ville, activite):
    logs = []
    logs.append(f"🚀 Scan lancé pour {activite} à {ville}...")
    
    driver = None
    try:
        driver = get_driver()
        logs.append("✅ Navigateur ouvert avec succès.")
        
        # Navigation
        query = f"{activite} {ville}"
        url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
        logs.append(f"🌍 Connexion à Maps...")
        
        driver.get(url)
        time.sleep(3) # Pause vitale
        
        # Debug Photo
        driver.save_screenshot("debug_view.png")
        logs.append("📸 Photo de contrôle prise.")

        # Extraction simple
        elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/maps/place/']")
        logs.append(f"🎯 {len(elements)} éléments détectés brute.")
        
        resultats = []
        for i, elem in enumerate(elements[:10]):
            try:
                nom = elem.get_attribute("aria-label")
                if nom:
                    resultats.append({"Nom": nom, "Ville": ville, "État": "✅ Trouvé"})
            except:
                pass
        
        driver.quit()
        
        if not resultats:
             logs.append("⚠️ Aucun résultat extrait (blocage possible).")
             
        return pd.DataFrame(resultats), logs

    except Exception as e:
        logs.append(f"❌ CRASH : {str(e)}")
        if driver:
            driver.quit()
        return pd.DataFrame(), logs