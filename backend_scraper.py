import time
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def lancer_recherche_live(ville, activite):
    print(f"🕵️‍♂️ Démarrage du scan furtif pour {ville}...")

    options = webdriver.ChromeOptions()
    
    # --- 1. LES RÉGLAGES CLOUD (OBLIGATOIRES) ---
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080") # Important pour voir la liste

    # --- 2. LE MASQUE (ANTI-DÉTECTION) ---
    # On se fait passer pour un vrai Chrome sur Windows 10
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    options.add_argument(f'user-agent={user_agent}')
    # On désactive le drapeau "AutomationControlled" qui crie "Je suis un robot"
    options.add_argument("--disable-blink-features=AutomationControlled")

    # --- 3. DÉTECTION DU DRIVER (CLOUD vs PC) ---
    if os.path.exists("/usr/bin/chromium"):
        options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")
    else:
        service = Service(ChromeDriverManager().install())

    try:
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"❌ Crash Chrome : {e}")
        return pd.DataFrame()

    # --- 4. NAVIGATION ---
    try:
        query = f"{activite} {ville}"
        url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
        driver.get(url)
        
        # Pause de sécurité pour laisser charger (le cloud est parfois lent)
        time.sleep(3)

        # --- AJOUTE CA ICI ---
        print("📸 Clic-clac ! Photo de l'écran en cours...")
        driver.save_screenshot("debug_view.png")

        # Gestion Cookies (On tente de cliquer, si ça rate c'est pas grave)
        try:
            bouton = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Tout refuser')]")))
            bouton.click()
            time.sleep(1)
        except:
            # Parfois le sélecteur change ou le bouton n'est pas là
            pass

        # --- DEBUG VISUEL (OPTIONNEL) ---
        # Si ça ne marche toujours pas, décommente la ligne ci-dessous pour voir ce que le robot voit
        driver.save_screenshot("debug_view.png") 

        # Scroll pour charger les résultats
        try:
            # On cherche la zone de scroll (role='feed')
            feed = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']")))
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)
            time.sleep(2)
        except:
            pass # Si pas de scroll, on prend les premiers résultats

        # Extraction des liens
        elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/maps/place/']")
        
        resultats = []
        limit = 10 # On limite pour que ce soit rapide
        
        for i, elem in enumerate(elements):
            if i >= limit: break
            try:
                nom = elem.get_attribute("aria-label")
                if nom:
                    resultats.append({
                        "Nom": nom,
                        "Ville": ville,
                        "Activité": activite,
                        "État": "✅ Disponible"
                    })
            except:
                continue

        driver.quit()
        return pd.DataFrame(resultats)

    except Exception as e:
        print(f"❌ Erreur pendant le script : {e}")
        driver.quit()
        return pd.DataFrame()

if __name__ == "__main__":
    # Test local
    print(lancer_recherche_live("Paris", "Boulangerie"))