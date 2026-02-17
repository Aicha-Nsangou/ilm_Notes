# Ilm Notes – MVP Streamlit App
# ---------------------------------
# Objectif : Organiser, réviser et partager des notes de sciences islamiques
# Auteur : Aicha Nsangou
# Intention : خدمة العلم – au service de la science

import streamlit as st
from auth import  is_logged_in,auto_login
from supalogic import *
from supadb import is_admin


# -----------------------------
# Configuration générale
# -----------------------------
st.set_page_config(
    page_title="Ilm Notes",
    page_icon="📘",
    layout="centered"
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
if "user" not in st.session_state:
    user = auto_login()
    if user:
        st.session_state["user"] = user

def get_current_user():
    if "user" in st.session_state and st.session_state["user"]:
        return st.session_state["user"]
    return None

# Custom header
custom_header()
# Initialiser la page par défaut
user = get_current_user()
col1,col2 = st.columns([2,1])
# Barre de navigation
with col2 :
    selected = navbar_custom()
    page = selected

with col1:

    if user:
        user_id = user.id
    else:
        user_id = None

#lien avec les pages
    if selected == "Note":
        if is_logged_in():
            page_ajouter_note(user_id)
        else:
           login_page()

    elif selected == "Organisation":
        if is_logged_in():
            page_organisation_recherche(user_id)
        else:
           login_page()

    elif selected == "Révision":
        if is_logged_in():
            page_revision(user_id)
        else:
           login_page()

    elif selected == "Progression":
        if is_logged_in():
         page_progression_notes(user_id)
        else:
            login_page()

    elif selected == "Compte":
        page_demo()
    elif selected == "Admin":
        if is_logged_in():
            if not is_admin(user_id):
                st.error("Accès interdit")
                st.stop()
            page_admin(user_id)
        else:
            login_page()

# -----------------------------
# Pied de page
# -----------------------------

#custom_footer()
