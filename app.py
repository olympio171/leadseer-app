import streamlit as st
import pandas as pd
import io 
from backend_scraper import lancer_recherche_live 

# --- CONFIGURATION ---
st.set_page_config(page_title="LeadSeer Pro", page_icon="🚀", layout="wide")

LIEN_ABONNEMENT = "https://buy.stripe.com/TON_LIEN_ICI"
CODE_SECRET = "LEAD2026" 

if "est_connecte" not in st.session_state:
    st.session_state["est_connecte"] = False

# --- SIDEBAR ---
with st.sidebar:
    st.title("💎 Espace Membre")
    if not st.session_state["est_connecte"]:
        st.write("Entrez votre code d'accès :")
        input_code = st.text_input("Code (ex: LEAD2026)", key="login_field")
        
        if st.button("Se connecter"):
            if input_code.strip() == CODE_SECRET:
                st.session_state["est_connecte"] = True
                st.rerun()
            else:
                st.error("Code incorrect.")
        st.markdown("---")
        st.write("Accès illimité pour 29€/mois.")
        st.link_button("👉 S'ABONNER", LIEN_ABONNEMENT)
    else:
        st.success("✅ Connecté (PRO)")
        if st.button("Se déconnecter"):
            st.session_state["est_connecte"] = False
            st.rerun()

# --- CORPS ---
st.title("🚀 LeadSeer")
st.markdown("#### Trouvez les numéros directs de vos futurs clients.")

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    ville = st.text_input("Ville cible", placeholder="Ex: Bordeaux")
with col2:
    activite = st.text_input("Activité", placeholder="Ex: Électricien")
with col3:
    nb_leads = st.slider("Nombre de leads", min_value=5, max_value=30, value=10, step=5)

st.write("") 
bouton = st.button("🔎 LANCER LE SCAN (AVEC TÉLÉPHONES)", type="primary", use_container_width=True)

# --- EXCEL ---
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Leads')
        workbook = writer.book
        worksheet = writer.sheets['Leads']
        header_format = workbook.add_format({'bold': True, 'fg_color': '#D7E4BC', 'border': 1})
        for i, col in enumerate(df.columns):
            worksheet.set_column(i, i, 25)
            worksheet.write(0, i, col, header_format)
    return output.getvalue()

# --- LOGIQUE ---
if bouton:
    if ville and activite:
        message = f"📡 Extraction des numéros pour {nb_leads} leads à {ville}..."
        
        with st.spinner(message):
            df, logs = lancer_recherche_live(ville, activite, limit=nb_leads)
            
            if not df.empty:
                # S'assurer que la colonne Téléphone existe pour éviter les bugs
                if "Téléphone" not in df.columns:
                    df["Téléphone"] = "Non trouvé"

                # --- CAS PRO ---
                if st.session_state["est_connecte"]:
                    st.balloons()
                    st.success(f"💎 PRO : {len(df)} leads qualifiés avec téléphone.")
                    st.dataframe(df, use_container_width=True)
                    
                    excel_data = to_excel(df)
                    st.download_button(
                        label="📥 TÉLÉCHARGER LE FICHIER EXCEL (.xlsx)",
                        data=excel_data,
                        file_name=f"LeadSeer_{ville}_{activite}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary"
                    )

                # --- CAS GRATUIT ---
                else:
                    st.warning(f"Version Gratuite : {len(df)} leads détectés.")
                    
                    # On copie et on masque
                    df_gratuit = df.copy()
                    df_gratuit["Téléphone"] = df_gratuit["Téléphone"].apply(lambda x: "🔒 06 ** ** ** **" if x != "Non trouvé" else "Non trouvé")
                    
                    st.markdown("### 🔓 Aperçu (Numéros masqués)")
                    st.dataframe(df_gratuit.head(3), use_container_width=True)
                    
                    reste = len(df) - 3
                    if reste > 0:
                        st.markdown(f"### 🔒 {reste} autres leads prêts...")
                        df_floute = df_gratuit.iloc[3:].copy()
                        df_floute["Nom de l'entreprise"] = "🔒 RÉSERVÉ PRO"
                        st.dataframe(df_floute, use_container_width=True)
                        st.link_button(f"🔓 DÉBLOQUER LES NUMÉROS", LIEN_ABONNEMENT, type="primary")

            else:
                st.error("Aucun résultat. Essayez une ville plus grande.")
    else:
        st.info("Remplissez les champs.")

st.markdown("---")
st.caption("LeadSeer SaaS © 2026")