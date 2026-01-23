# Ilm Notes – MVP Streamlit App
# ---------------------------------
# Objectif : Organiser, réviser et partager des notes de sciences islamiques
# Auteur : Aicha Nsangou
# Intention : خدمة العلم – au service de la science

import streamlit as st
from db import add_note, get_notes,create_user
from logic import (
    page_accueil,
    page_ajouter_note,
    page_organisation_recherche,
    page_revision,
    page_progression_notes
)

# -----------------------------
# Configuration générale
# -----------------------------
st.set_page_config(
    page_title="Ilm Notes",
    page_icon="📘",
    layout="centered"
)

# -----------------------------
# Gestion utilisateur simple
# -----------------------------

if 'username' not in st.session_state:
    name_input = st.text_input("Entrez votre nom d'utilisateur")
    if name_input:
        created = create_user(name_input)
        st.session_state.username = name_input
        if created:
            st.success("Marhaban! Compte créé avec succès.")
        else:
            st.warning("Connexion réussie")

# -----------------------------
# Sidebar – Navigation
# -----------------------------
st.sidebar.title("📚 Ilm Notes")
page = st.sidebar.radio(
    "Navigation",
    ["Accueil", "Ajouter une note", "Organisation", "Révision", "Progression"]
)


 
if st.session_state.get('username'):
    username = st.session_state.username
    st.sidebar.markdown(f"**Marhaban {username}**")
    # -----------------------------
    # Affichage des pages
    # -----------------------------
    if page == "Accueil":
        page_accueil()
    elif page == "Ajouter une note":
        page_ajouter_note(username)
    elif page == "Organisation":
        page_organisation_recherche()
    elif page == "Révision":
        page_revision()
    elif page == "Progression":
        page_progression_notes()
    