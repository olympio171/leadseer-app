import streamlit as st
import pandas as pd
import io # <--- Nécessaire pour créer le fichier Excel en mémoire
from backend_scraper import lancer_recherche_live 

# --- CONFIGURATION ---
st.set_page_config(page_title="LeadSeer Pro", page_icon="🚀", layout="wide")

# --- RÉGLAGES ---
LIEN_ABONNEMENT = "https://buy.stripe.com/TON_LIEN_ICI"
CODE_SECRET = "LEAD2026" 

# --- SESSION ---
if "est_connecte" not in st.session_state:
    st.session_state["est_connecte"] = False

# --- SIDEBAR ---
with st.sidebar:
    st.title("💎 Espace Membre")
    if not st.session_state["est_connecte"]:
        input_code = st.text_input("Code d'accès", type="password")
        if st.button("Se connecter"):
            if input_code == CODE_SECRET:
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

# --- CORPS PRINCIPAL ---
st.title("🚀 LeadSeer")
st.markdown("#### Le moteur de recherche de clients pour agences.")

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    ville = st.text_input("Ville cible", placeholder="Ex: Lyon")
with col2:
    activite = st.text_input("Activité", placeholder="Ex: Plombier")
with col3:
    nb_leads = st.slider("Nombre de leads", min_value=5, max_value=50, value=10, step=5)

st.write("") 
bouton = st.button("🔎 LANCER LE SCAN", type="primary", use_container_width=True)

# --- FONCTION POUR CRÉER UN BEL EXCEL ---
def to_excel(df):
    output = io.BytesIO()
    # On utilise 'xlsxwriter' comme moteur
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Leads')
        workbook = writer.book
        worksheet = writer.sheets['Leads']
        
        # Format des en-têtes (Gras + Fond gris clair + Bordure)
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC', # Une petite couleur pro
            'border': 1
        })

        # On parcourt les colonnes pour ajuster la largeur (Auto-fit)
        for i, col in enumerate(df.columns):
            # On calcule la largeur max entre le nom de la colonne et le contenu le plus long
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            # On limite quand même à 50 pour pas que ce soit géant
            if max_len > 50: max_len = 50
            worksheet.set_column(i, i, max_len)
            
            # On applique le format joli aux en-têtes
            worksheet.write(0, i, col, header_format)
            
    return output.getvalue()

# --- LOGIQUE ---
if bouton:
    if ville and activite:
        message_attente = f"📡 Recherche de {nb_leads} leads à {ville}..."
        if nb_leads > 20:
            message_attente += " (Cela peut prendre jusqu'à 1 minute)"
            
        with st.spinner(message_attente):
            
            df, _ = lancer_recherche_live(ville, activite, limit=nb_leads)
            
            if not df.empty:
                # --- CAS PRO ---
                if st.session_state["est_connecte"]:
                    st.balloons()
                    st.success(f"💎 PRO : {len(df)} leads récupérés.")
                    st.dataframe(df, use_container_width=True)
                    
                    # GÉNÉRATION DU FICHIER EXCEL PROPRE
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
                    st.warning(f"Version Gratuite : {len(df)} leads trouvés.")
                    st.markdown("### 🔓 Aperçu (3 premiers)")
                    st.dataframe(df.head(3), use_container_width=True)
                    
                    reste = len(df) - 3
                    if reste > 0:
                        st.markdown(f"### 🔒 {reste} leads masqués...")
                        df_floute = df.iloc[3:].copy()
                        df_floute["Nom de l'entreprise"] = "🔒 RÉSERVÉ PRO"
                        df_floute["État"] = "🔒 BLOQUÉ"
                        st.dataframe(df_floute, use_container_width=True)
                        st.link_button(f"🔓 DÉBLOQUER TOUT", LIEN_ABONNEMENT, type="primary")

            else:
                st.error("Aucun résultat. Google Maps bloque peut-être, réessayez dans 1 minute.")
    else:
        st.info("Remplissez les champs.")

st.markdown("---")
st.caption("LeadSeer SaaS © 2026")