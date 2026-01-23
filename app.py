# Ilm Notes – MVP Streamlit App
# ---------------------------------
# Objectif : Organiser, réviser et partager des notes de sciences islamiques
# Auteur : Aicha Nsangou
# Intention : خدمة العلم – au service de la science

import streamlit as st
from db import create_user, user_exists
from logic import (
    page_accueil,
    page_ajouter_note,
    page_organisation_recherche,
    page_revision,
    page_progression_notes,
    page_admin,
    page_demo
)

# -----------------------------
# Configuration générale
# -----------------------------
st.set_page_config(
    page_title="Ilm Notes",
    page_icon="📘",
    layout="centered"
)

# Initialiser la page par défaut
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏡 Accueil"


# -----------------------------
# Sidebar – Navigation
# -----------------------------
st.sidebar.title("📚 Ilm Notes")

# Afficher le nom d'utilisateur si connecté
if st.session_state.get('username'):
    st.sidebar.markdown(f"**Marhaban {st.session_state.username}**")
    # Bouton de déconnexion
    if st.sidebar.button("🚪 Déconnexion"):
        del st.session_state.username
        st.rerun()

st.sidebar.divider()
page = st.sidebar.radio(
    "Navigation",
    ["🏡 Accueil", "📝 Ajouter une note", "🗂️ Organisation", "🔁 Révision", "📊 Progression","📘 Demo", "🔐 Admin"]
)

# Afficher la page d'accueil par défaut
if page == "🏡 Accueil":
    page_accueil()

elif page == "📝 Ajouter une note":
    # Demander le nom d'utilisateur si pas connecté
    if 'username' not in st.session_state:
        st.header("➕ Ajouter une nouvelle note")
        st.divider()
        
        name_input = st.text_input("Entrez votre nom d'utilisateur pour continuer")
        if name_input:
            if not user_exists(name_input):
                create_user(name_input)
                st.success("Compte créé avec succès!")
            else:
                st.info("Bienvenue!")
            st.session_state.username = name_input
            st.rerun()
    else:
        page_ajouter_note(st.session_state.username)

elif page == "🗂️ Organisation":
    if 'username' not in st.session_state:
        st.header("🗂️ Organisation & Recherche")
        st.divider()
        name_input = st.text_input("Entrez votre nom d'utilisateur pour continuer")
        if name_input:
            if not user_exists(name_input):
                create_user(name_input)
            st.session_state.username = name_input
            st.rerun()
    else:
        page_organisation_recherche()

elif page == "🔁 Révision":
    if 'username' not in st.session_state:
        st.header("🔁 Révision guidée")
        st.divider()
        name_input = st.text_input("Entrez votre nom d'utilisateur pour continuer")
        if name_input:
            if not user_exists(name_input):
                create_user(name_input)
            st.session_state.username = name_input
            st.rerun()
    else:
        page_revision()

elif page == "📊 Progression":
    if 'username' not in st.session_state:
        st.header("📊 Progression par catégorie")
        st.divider()
        name_input = st.text_input("Entrez votre nom d'utilisateur pour continuer")
        if name_input:
            if not user_exists(name_input):
                create_user(name_input)
            st.session_state.username = name_input
            st.rerun()
    else:
        page_progression_notes()

elif page == "📘 Demo":
    page_demo()
    
elif page == "🔐 Admin":
    page_admin()
    