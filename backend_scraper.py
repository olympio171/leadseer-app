import time
import pandas as pd
import os
import shutil
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
    
    # Masque pour passer inaperçu
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
    logs.append(f"🚀 Scan précis (Tel) : {limit} {activite}s à {ville}...")
    
    driver = None
    try:
        driver = get_driver()
        
        query = f"{activite} {ville}"
        url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
        
        driver.get(url)
        time.sleep(3) 

        # Scroll pour charger la liste
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

                # 1. CLIC OBLIGATOIRE
                driver.execute_script("arguments[0].click();", elem)
                
                # 2. PAUSE CRITIQUE (Pour que le panneau de droite change !)
                time.sleep(1.5) 

                telephone = "Non trouvé"
                
                # 3. EXTRACTION CIBLÉE (On ne cherche QUE le bouton téléphone)
                try:
                    # Le sélecteur magique : Google met le numéro dans 'data-item-id'
                    # Ex: data-item-id="phone:tel:+33612345678"
                    bouton_tel = driver.find_element(By.CSS_SELECTOR, "button[data-item-id^='phone:tel:']")
                    raw_data = bouton_tel.get_attribute("data-item-id")
                    
                    # On nettoie pour ne garder que le numéro
                    if raw_data:
                        telephone = raw_data.replace("phone:tel:", "").strip()
                except:
                    # Si pas de bouton "phone:tel:", on cherche le bouton avec l'icône téléphone
                    try:
                        # Recherche par l'icône image (souvent le cas sur desktop)
                        imgs = driver.find_elements(By.TAG_NAME, "img")
                        for img in imgs:
                            src = img.get_attribute("src")
                            # L'icône téléphone de Google contient souvent ce lien
                            if src and "k52302" in src: 
                                # Le numéro est souvent dans le texte du parent
                                parent = img.find_element(By.XPATH, "./../..")
                                text = parent.text
                                # On vérifie vite fait si ça ressemble à un numéro
                                if any(char.isdigit() for char in text):
                                    telephone = text
                                    break
                    except:
                        pass

                # On n'ajoute que si on a au moins le nom
                resultats.append({
                    "Nom de l'entreprise": nom,
                    "Activité": activite,
                    "Ville": ville,
                    "Téléphone": telephone,
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