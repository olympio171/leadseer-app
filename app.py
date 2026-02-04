import streamlit as st
import pandas as pd
from backend_scraper import lancer_recherche_live # On importe ton moteur

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="LeadSeer - Trouvez vos clients", page_icon="🕵️‍♂️", layout="centered")

# --- TITRE ET ACCROCHE ---
st.title("🕵️‍♂️ LeadSeer")
st.markdown("### Trouvez vos futurs clients sans site web en 1 clic.")
st.markdown("Remplissez les champs ci-dessous pour scanner votre zone.")

# --- BARRE LATÉRALE (OPTIONNEL) ---
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
        # Barre de chargement pour faire patienter l'utilisateur
        with st.spinner(f"📡 Scan des {activite}s à {ville} en cours... Veuillez patienter..."):
            
            # APPEL AU BACKEND (Ton script Python)
            df = lancer_recherche_live(ville, activite)
            
            if not df.empty:
                st.success(f"✅ {len(df)} prospects trouvés !")
                
                # --- LA STRATÉGIE FREEMIUM (Le Floutage) ---
                
                # 1. Les 3 premiers (GRATUIT)
                st.subheader("🔓 Résultats Gratuits (Aperçu)")
                df_gratuit = df.head(3)
                st.table(df_gratuit)
                
                # 2. Le reste (FLOUTÉ / BLOQUÉ)
                st.subheader(f"🔒 {len(df) - 3} autres prospects détectés...")
                
                if len(df) > 3:
                    # On crée un faux dataframe flouté
                    df_floute = df.iloc[3:].copy()
                    # On remplace les noms par des étoiles ou du flou
                    df_floute["Nom de l'entreprise"] = "🔒 PROSPECT PREMIUM ******"
                    df_floute["État"] = "🔒 BLOQUÉ"
                    
                    st.table(df_floute)
                    
                    # --- LE GROS BOUTON D'APPEL À L'ACTION ---
                    st.warning("⚠️ Vous utilisez la version gratuite.")
                    st.markdown(f"**Il reste {len(df) - 3} prospects qualifiés dans cette liste.**")
                    if st.button(f"🔓 DÉBLOQUER LA LISTE COMPLÈTE ({ville})"):
                        st.info("Ici, on redirigera vers ta page de paiement Stripe !")
            else:
                st.error("Aucun résultat trouvé. Essayez une autre ville.")
    else:
        st.warning("Veuillez remplir la ville et l'activité.")

# Dans app.py
df = lancer_recherche_live(ville, activite)

# --- DEBUG : AFFICHER LA PREUVE ---
import os
if os.path.exists("debug_view.png"):
    st.image("debug_view.png", caption="Ce que le robot a vu")