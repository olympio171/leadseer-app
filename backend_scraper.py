import time
import pandas as pd
import os
import shutil
import re # <--- NOUVEAU : Pour détecter les motifs de numéros
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    chrome_options.add_argument(f'user-agent={user_agent}')

    chromium_path = shutil.which("chromium") or "/usr/bin/chromium"
    chromedriver_path = shutil.which("chromedriver") or "/usr/bin/chromedriver"

    if os.path.exists(chromium_path) and os.path.exists(chromedriver_path):
        chrome_options.binary_location = chromium_path
        service = Service(chromedriver_path)
        return webdriver.Chrome(service=service, options=chrome_options)
    else:
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

def lancer_recherche_live(ville, activite, limit=10):
    logs = []
    logs.append(f"🚀 Scan approfondi (Tel) : {limit} {activite}s à {ville}...")
    
    driver = None
    try:
        driver = get_driver()
        
        query = f"{activite} {ville}"
        url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
        
        driver.get(url)
        time.sleep(3) 

        # Scroll
        try:
            feed = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']")))
            nb_scrolls = int(limit / 5) + 1
            for _ in range(nb_scrolls):
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)
                time.sleep(1)
        except:
            pass

        elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/maps/place/']")
        logs.append(f"🎯 {len(elements)} fiches détectées.")
        
        resultats = []
        
        for i, elem in enumerate(elements):
            if len(resultats) >= limit:
                break
            
            try:
                nom = elem.get_attribute("aria-label")
                if not nom: continue

                # On clique
                driver.execute_script("arguments[0].click();", elem)
                time.sleep(2) # On attend bien que le texte charge

                telephone = "Non trouvé"
                
                # --- NOUVELLE MÉTHODE : SCAN GLOBAL DU TEXTE ---
                try:
                    # On prend tout le texte de la page visible
                    body_text = driver.find_element(By.TAG_NAME, "body").text
                    
                    # On cherche un motif de numéro français (01 à 09 suivi de 8 chiffres, avec espaces ou points)
                    # Regex : 0[1-9] suivi de 4 groupes de 2 chiffres séparés par espace, point ou tiret
                    match = re.search(r"(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}", body_text)
                    
                    if match:
                        telephone = match.group(0)
                except:
                    pass

                # On ajoute TOUJOURS la colonne téléphone, même si vide
                resultats.append({
                    "Nom de l'entreprise": nom,
                    "Activité": activite,
                    "Ville": ville,
                    "Téléphone": telephone, # Cette clé existe toujours maintenant
                    "État": "✅ Qualifié"
                })
                
            except Exception as e:
                continue
        
        driver.quit()
        return pd.DataFrame(resultats), logs

    except Exception as e:
        logs.append(f"❌ CRASH : {str(e)}")
        if driver: driver.quit()
        return pd.DataFrame(), logs