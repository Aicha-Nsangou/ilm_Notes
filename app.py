# Ilm Notes – MVP Streamlit App
# ---------------------------------
# Objectif : Organiser, réviser et partager des notes de sciences islamiques
# Auteur : Aicha Nsangou
# Intention : خدمة العلم – au service de la science

import streamlit as st
from auth import signup, login, logout, is_logged_in
from supalogic import (
    page_accueil,
    page_ajouter_note,
    page_organisation_recherche,
    page_revision,
    page_progression_notes,
    page_demo,
    custom_footer,
    custom_header,
    page_admin
    
)
from supadb import is_admin


# -----------------------------
# Configuration générale
# -----------------------------
st.set_page_config(
    page_title="Ilm Notes",
    page_icon="📘",
    layout="centered"
)


# Custom header
custom_header()

# Add padding to avoid overlap with fixed footer
st.markdown(
    """
    <style>
    .main .block-container {
        padding-bottom: 60px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Sidebar – Navigation
# -----------------------------
st.sidebar.title("📚 Ilm Notes")

with st.sidebar:
    if not is_logged_in():
        with st.expander("🔐 Connexion"):
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            if st.button("Se connecter"):
                login(email, password)
                
        with st.expander("👤 Créer un compte"):
            full_name = st.text_input("Nom complet")
            email2 = st.text_input("Email pour inscription")
            password2 = st.text_input("Mot de passe", type="password", key="signup")
            if st.button("S'inscrire"):
                signup(email2, password2, full_name)
    else:
        st.subheader(f"Marhaban !")
        st.button("Se déconnecter", on_click=logout)
# Initialiser la page par défaut
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏡 Accueil"

st.sidebar.divider()
page = st.sidebar.radio(
    "Navigation",
    ["🏡 Accueil", "📝 Ajouter une note", "🗂️ Organisation", "🔁 Révision", "📊 Progression","📘 Demo", "🛡️ Admin"]
)

# Afficher la page d'accueil par défaut
if page == "🏡 Accueil":
    page_accueil()

elif page == "📝 Ajouter une note":
    # Demander le nom d'utilisateur si pas connecté
    if is_logged_in():
        page_ajouter_note(st.session_state['user'].id)
    else:
        st.info("Connectez-vous pour accéder à vos notes.")

elif page == "🗂️ Organisation":
    if is_logged_in():
        page_organisation_recherche(st.session_state['user'].id)
    else:
        st.info("Connectez-vous pour accéder à vos notes.")

elif page == "🔁 Révision":
    if is_logged_in():
         page_revision(st.session_state['user'].id)
    else:
        st.info("Connectez-vous pour accéder à vos notes.")

elif page == "📊 Progression":
    if is_logged_in():
         page_progression_notes(st.session_state['user'].id)
    else:
        st.info("Connectez-vous pour accéder à vos notes.")
elif page == "📘 Demo":
    page_demo()
    
elif page == "🛡️ Admin":
    if is_logged_in():
        if not is_admin(st.session_state['user'].id):
            st.error("Accès interdit")
            st.stop()
        page_admin(st.session_state['user'].id)
    else:
        st.info("Connectez-vous pour accéder à vos notes.")
    
st.sidebar.divider()
st.sidebar.markdown("""
    <div style="text-align:center; margin-top: 20px;">
        <a href="https://wa.me/237698491583?text=Assalamu%20alaykum%2C%20j%27utilise%20Ilm%20Notes%20et%20voici%20mon%20avis%20:" 
            target="_blank"
            style="
                display: inline-block;
                padding: 10px 20px;
                background-color: #25D366;
                color: white;
                border-radius: 8px;
                text-decoration: none;
                font-weight: bold;
       ">
           🧠 Mon avis 
        </a>
    </div>
""", unsafe_allow_html=True)

# -----------------------------
# Pied de page
# -----------------------------

custom_footer()
