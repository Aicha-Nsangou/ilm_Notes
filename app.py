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
    page_admin,
    set_bg_local,
    navbar_custom,
    login_page
    
)
from supadb import is_admin


# -----------------------------
# Configuration générale
# -----------------------------
st.set_page_config(
    page_title="Ilm Notes",
    page_icon="📘",
    layout="wide"
)
st.markdown("""
    <style>

        /* 🧾 Inputs */
        input:focus, textarea:focus, select:focus {
            border: 1px solid #2e7d32 !important;
            outline:none;
        }
        /* 🔘 Boutons */
        button {
            border: none;
        }

    </style>
""", unsafe_allow_html=True)

# add bg image fixed
set_bg_local("./ilm3.jpg")
if "started" not in st.session_state:
    st.session_state["started"] = False

# Custom header
custom_header()

# Initialiser la page par défaut
if "page" not in st.session_state:
    st.session_state.page = " Accueil"


col1,col2 = st.columns([1,2])
# Barre de navigation
with col1 :
    selected = navbar_custom()
    page = selected
    st.session_state.page = page
with col2:
#lien avec les pages
    if selected == "Accueil":
        page_accueil()
    elif selected == "Note":
        if is_logged_in():
            page_ajouter_note(st.session_state['user']['id'])
        else:
            st.info("Connectez-vous pour accéder à vos notes.")
    elif selected == "Organisation":
        if is_logged_in():
            page_organisation_recherche(st.session_state['user']['id'])
        else:
            st.info("Connectez-vous pour accéder à vos notes.")
    elif selected == "Révision":
        if is_logged_in():
            page_revision(st.session_state['user']['id'])
        else:
            st.info("Connectez-vous pour accéder à vos notes.")
    elif selected == "Progression":
        if is_logged_in():
         page_progression_notes(st.session_state['user']['id'])
        else:
            st.info("Connectez-vous pour accéder à vos notes.")
    elif selected == "Demo":
        page_demo()
    elif selected == "Admin":
        if is_logged_in():
            if not is_admin(st.session_state['user']['id']):
                st.error("Accès interdit")
                st.stop()
            page_admin(st.session_state['user']['id'])
        else:
            st.info("Connectez-vous pour accéder à vos notes.")
    elif selected == "Se connecter":
        login_page()


# -----------------------------
# Pied de page
# -----------------------------

#custom_footer()
