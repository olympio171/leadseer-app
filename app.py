import streamlit as st
import pandas as pd
import os # <--- Indispensable pour vérifier si la photo existe
from backend_scraper import lancer_recherche_live 

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="LeadSeer - Trouvez vos clients", page_icon="🕵️‍♂️", layout="centered")

# --- TITRE ET ACCROCHE ---
st.title("🕵️‍♂️ LeadSeer")
st.markdown("### Trouvez vos futurs clients sans site web en 1 clic.")
st.markdown("Remplissez les champs ci-dessous pour scanner votre zone.")

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.write("### 💎 Version Pro")
    st.write("Débloquez les numéros de téléphone et l'export Excel.")
    st.button("Passer Premium (29€/mois)")

# --- FORMULAIRE DE RECHERCHE ---
col1, col2 = st.columns(2)
with col1:
    ville = st.text_input("Ville cible", placeholder="Ex: Bordeaux")
with col2:
    activite = st.text_input("Activité", placeholder="Ex: Plombier, Coiffeur...")

bouton_recherche = st.button("🔍 LANCER LE SCAN", type="primary")

# --- LOGIQUE DE L'APPLICATION ---
if bouton_recherche:
    if ville and activite:
        # Barre de chargement
        with st.spinner(f"📡 Scan des {activite}s à {ville} en cours... Veuillez patienter..."):
            
            # 1. APPEL AU MOTEUR (BACKEND)
            # C'est ici que le robot part travailler et prend la photo
            df = lancer_recherche_live(ville, activite)
            
            # 2. AFFICHAGE DE LA PREUVE (DEBUG)
            # C'est ici qu'on regarde si le robot a ramené une photo
            if os.path.exists("debug_view.png"):
                st.warning("🕵️‍♂️ DEBUG - Vue du Robot :")
                st.image("debug_view.png", caption="Capture d'écran prise par le serveur")
            
            # 3. AFFICHAGE DES RÉSULTATS
            if not df.empty:
                st.success(f"✅ {len(df)} prospects trouvés !")
                
                # A. Les 3 premiers (GRATUIT)
                st.subheader("🔓 Résultats Gratuits (Aperçu)")
                df_gratuit = df.head(3)
                st.table(df_gratuit)
                
                # B. Le reste (FLOUTÉ / BLOQUÉ)
                st.subheader(f"🔒 {len(df) - 3} autres prospects détectés...")
                
                if len(df) > 3:
                    # On crée un faux dataframe flouté pour donner envie
                    df_floute = df.iloc[3:].copy()
                    df_floute["Nom"] = "🔒 PROSPECT PREMIUM ******"
                    df_floute["État"] = "🔒 BLOQUÉ"
                    
                    st.table(df_floute)
                    
                    # C. Le Bouton d'achat
                    st.warning("⚠️ Vous utilisez la version gratuite.")
                    st.markdown(f"**Il reste {len(df) - 3} prospects qualifiés dans cette liste.**")
                    if st.button(f"🔓 DÉBLOQUER LA LISTE COMPLÈTE ({ville})"):
                        st.info("Redirection vers le paiement sécurisé...")
            else:
                st.error("Aucun résultat trouvé. Regarde la capture d'écran ci-dessus pour comprendre pourquoi (Captcha ? Cookies ?).")
    else:
        st.warning("Veuillez remplir la ville et l'activité.")