import streamlit as st
import pandas as pd
from backend_scraper import lancer_recherche_live 

# --- CONFIGURATION ---
st.set_page_config(page_title="LeadSeer", page_icon="⚡", layout="centered")

# Lien de paiement (On le changera à l'étape 2)
LIEN_STRIPE = "https://buy.stripe.com/TON_LIEN_ICI" 

# --- HEADER ---
st.title("⚡ LeadSeer")
st.caption("L'outil secret des agences pour trouver des clients hors-radar.")

st.markdown("---")

# --- FORMULAIRE ---
col1, col2 = st.columns(2)
with col1:
    ville = st.text_input("Ville cible", placeholder="Ex: Lyon")
with col2:
    activite = st.text_input("Activité", placeholder="Ex: Plombier")

bouton = st.button("🔍 LANCER LE SCAN (GRATUIT)", type="primary")

# --- RÉSULTATS ---
if bouton:
    if ville and activite:
        with st.spinner(f"🛰️ Satellites orientés sur {ville}... Analyse en cours..."):
            
            # On appelle ton moteur (qui marche enfin !)
            # On ignore les logs ici, on veut juste le tableau 'df'
            df, _ = lancer_recherche_live(ville, activite)
            
            if not df.empty:
                st.success(f"🎯 {len(df)} prospects identifiés à {ville} !")
                st.balloons() # Petit effet wow
                
                # 1. LES GRATUITS (Les 3 premiers)
                st.markdown("### 🔓 Résultats débloqués (Aperçu)")
                st.dataframe(df.head(3), use_container_width=True)
                
                # 2. LES PAYANTS (Le reste)
                reste = len(df) - 3
                if reste > 0:
                    st.markdown(f"### 🔒 {reste} autres prospects haute qualité détectés...")
                    
                    # On crée un faux tableau flouté pour donner envie
                    df_floute = df.iloc[3:].copy()
                    df_floute["Nom"] = "████████████" # Effet censuré
                    df_floute["État"] = "🔒 RÉSERVÉ PREMIUM"
                    
                    st.dataframe(df_floute, use_container_width=True)
                    
                    # 3. LE CALL TO ACTION (L'argent)
                    st.warning(f"⚠️ Vous consultez la version gratuite. Il reste {reste} leads inexploités.")
                    
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <a href="{LIEN_STRIPE}" target="_blank">
                            <button style="
                                background-color: #FF4B4B; 
                                color: white; 
                                padding: 15px 32px; 
                                text-align: center; 
                                text-decoration: none; 
                                display: inline-block; 
                                font-size: 18px; 
                                margin: 4px 2px; 
                                cursor: pointer; 
                                border-radius: 8px; 
                                border: none;">
                                🔓 DÉBLOQUER LA LISTE COMPLÈTE (9€)
                            </button>
                        </a>
                        <p style="font-size: 12px; margin-top: 10px;">Paiement sécurisé via Stripe • Accès immédiat</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            else:
                st.error("Aucun résultat trouvé. Essayez une ville plus grande.")
    else:
        st.info("Entrez une ville et une activité pour commencer.")

# --- FOOTER ---
st.markdown("---")
st.markdown("*LeadSeer v1.0 • Propulsé par l'IA*")