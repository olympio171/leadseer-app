import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Fonction qui sera appelée par ton site
def lancer_recherche_live(ville, activite):
    # --- CONFIGURATION HEADLESS (INVISIBLE) ---
    # Pour un SaaS, on ne veut pas voir la fenêtre Chrome s'ouvrir
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") # Active ça pour ne pas voir le navigateur
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=fr")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # On construit la recherche
    query = f"{activite} {ville}"
    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
    
    print(f"🕵️‍♂️ LeadSeer cherche : {query}")
    driver.get(url)
    
    # Gestion Cookies (Bourrin mais rapide)
    try:
        WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Tout refuser')]"))).click()
    except:
        pass

    # On attend que la liste charge
    try:
        # On attend la barre latérale
        feed = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']")))
        # Petit scroll pour en avoir au moins 15-20
        for _ in range(2): 
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", feed)
            time.sleep(1)
    except:
        pass # Si pas de scroll, on prend ce qu'il y a

    # Extraction
    elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/maps/place/']")
    
    resultats = []
    
    # On limite à 20 résultats pour la démo (pour que ça aille vite)
    limit = 20 
    
    for i, elem in enumerate(elements):
        if i >= limit: break
        
        try:
            nom = elem.get_attribute("aria-label")
            if not nom: continue
            
            # Pour la démo rapide, on ne clique pas sur chaque fiche (trop lent pour du live)
            # On prend juste le nom pour l'instant. 
            # Si tu veux le TEL, il faut cliquer, mais ça ralentira l'expérience utilisateur.
            # Pour le MVP V1 : on montre qu'on a les NOMS, c'est suffisant pour le "Wow effect".
            
            resultats.append({
                "Nom de l'entreprise": nom,
                "Ville": ville,
                "Activité": activite,
                "État": "✅ Disponible"
            })
        except:
            continue
            
    driver.quit()
    
    # Retourne un DataFrame Pandas
    return pd.DataFrame(resultats)

if __name__ == "__main__":
    # Test rapide si tu lances ce fichier seul
    print(lancer_recherche_live("Lyon", "Plombier"))