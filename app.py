import streamlit as st
import pandas as pd
from backend_scraper import lancer_recherche_live 

# --- CONFIGURATION ---
st.set_page_config(page_title="LeadSeer Pro", page_icon="🚀", layout="wide") # Layout wide pour faire "Pro"

# --- RÉGLAGES ---
LIEN_ABONNEMENT = "https://buy.stripe.com/TON_NOUVEAU_LIEN_RECURRENT"
CODE_SECRET = "LEAD2026" # Le mot de passe que tu donnes après paiement

# --- GESTION DE LA SESSION (Pour rester connecté) ---
if "est_connecte" not in st.session_state:
    st.session_state["est_connecte"] = False

# --- SIDEBAR (ESPACE MEMBRE) ---
with st.sidebar:
    st.title("💎 Espace Membre")
    
    if not st.session_state["est_connecte"]:
        st.info("Vous avez un abonnement ? Entrez votre code ici.")
        input_code = st.text_input("Code d'accès", type="password")
        if st.button("Se connecter"):
            if input_code == CODE_SECRET:
                st.session_state["est_connecte"] = True
                st.rerun() # On recharge la page pour débloquer
            else:
                st.error("Code incorrect.")
        
        st.markdown("---")
        st.markdown("### Pas encore membre ?")
        st.write("Accédez à des leads illimités pour 29€/mois.")
        st.link_button("👉 S'ABONNER MAINTENANT", LIEN_ABONNEMENT)
    
    else:
        st.success("✅ Vous êtes connecté (PRO)")
        if st.button("Se déconnecter"):
            st.session_state["est_connecte"] = False
            st.rerun()

# --- CORPS PRINCIPAL ---
st.title("🚀 LeadSeer")
st.markdown("#### Le moteur de recherche de clients pour agences & freelances.")

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    ville = st.text_input("Ville cible", placeholder="Ex: Marseille")
with col2:
    activite = st.text_input("Activité", placeholder="Ex: Serrurier")
with col3:
    st.write("") # Espacement
    st.write("") 
    bouton = st.button("🔎 SCANN", type="primary", use_container_width=True)

# --- LOGIQUE D'AFFICHAGE ---
if bouton:
    if ville and activite:
        with st.spinner("📡 Interception des données en cours..."):
            
            # Appel Backend
            df, _ = lancer_recherche_live(ville, activite)
            
            if not df.empty:
                # ---------------------------------------------------------
                # CAS 1 : UTILISATEUR ABONNÉ (PRO)
                # ---------------------------------------------------------
                if st.session_state["est_connecte"]:
                    st.balloons()
                    st.success(f"💎 MODE PRO ACTIVÉ : {len(df)} leads récupérés.")
                    
                    # Tableau complet
                    st.dataframe(df, use_container_width=True)
                    
                    # Bouton d'export Excel (La fonctionnalité tueuse)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 TÉLÉCHARGER LA LISTE (CSV)",
                        data=csv,
                        file_name=f"leads_{ville}_{activite}.csv",
                        mime="text/csv",
                        type="primary"
                    )

                # ---------------------------------------------------------
                # CAS 2 : UTILISATEUR GRATUIT (LIMITÉ)
                # ---------------------------------------------------------
                else:
                    st.warning(f"Version Gratuite : {len(df)} leads trouvés, mais accès limité.")
                    
                    # Les 3 premiers
                    st.markdown("### 🔓 Aperçu Gratuit")
                    st.dataframe(df.head(3), use_container_width=True)
                    
                    # Le flou frustrant
                    reste = len(df) - 3
                    if reste > 0:
                        st.markdown(f"### 🔒 {reste} leads masqués...")
                        df_floute = df.iloc[3:].copy()
                        df_floute["Nom"] = "🔒 RÉSERVÉ MEMBRES PRO"
                        df_floute["État"] = "🔒 BLOQUÉ"
                        st.dataframe(df_floute, use_container_width=True)
                        
                        st.error("🛑 Vous devez être abonné pour voir les numéros et télécharger la liste.")
                        st.link_button(f"🔓 DÉBLOQUER TOUT (29€/mois)", LIEN_ABONNEMENT, type="primary")

            else:
                st.error("Aucun résultat trouvé.")
    else:
        st.info("Remplissez les champs pour lancer.")

st.markdown("---")
st.caption("LeadSeer SaaS © 2026")