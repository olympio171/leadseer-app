import streamlit as st
import pandas as pd
import os
from backend_scraper import lancer_recherche_live 

# Configuration de la page
st.set_page_config(page_title="LeadSeer DEBUG", layout="centered")
st.title("🕵️‍♂️ LeadSeer - Mode Diagnostic")

# Formulaire
ville = st.text_input("Ville", "Paris")
activite = st.text_input("Activité", "Plombier")

if st.button("LANCER LE TEST"):
    with st.spinner("Le robot travaille..."):
        
        # --- C'EST ICI QUE CA CHANGE ---
        # On récupère DEUX variables : le tableau (df) ET les journaux (logs)
        df, logs = lancer_recherche_live(ville, activite)
        
        # 1. AFFICHAGE DES LOGS (Pour comprendre ce qui se passe)
        with st.expander("📜 Voir le journal du robot (Logs)", expanded=True):
            for ligne in logs:
                if "❌" in ligne:
                    st.error(ligne)
                elif "✅" in ligne:
                    st.success(ligne)
                else:
                    st.write(ligne)

        # 2. AFFICHAGE DE LA PHOTO (Très important)
        if os.path.exists("debug_view.png"):
            st.write("### 📸 Ce que le robot a vu :")
            st.image("debug_view.png", caption="Capture d'écran du serveur")
        else:
            st.warning("⚠️ Pas d'image trouvée.")

        # 3. RÉSULTATS
        if not df.empty:
            st.write(f"### 🎉 {len(df)} Résultats trouvés :")
            st.dataframe(df)
        else:
            st.error("Aucun résultat dans le tableau.")