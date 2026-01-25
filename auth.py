import streamlit as st
from supabase_client import supabase

# -------------------------
# SIGNUP
# -------------------------
def signup(email, password, full_name):
    try:
        # Création utilisateur Supabase Auth
        user_resp = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        user = user_resp.user
        if not user:
            st.error("Impossible de créer le compte. Vérifie l'email ou le mot de passe.")
            return None

        # Création du profil dans table 'users'
        supabase.table("users").insert({
            "id": user.id,
            "full_name": full_name,
        }).execute()

        st.success(f"Compte créé | Marhaban {full_name}")
        st.session_state['user'] = user
        st.session_state['full_name'] = full_name
        return user

    except Exception as e:
        st.error(f"Erreur signup : {e}")
        return None


# -------------------------
# LOGIN
# -------------------------
def login(email, password):
    try:
        user_resp = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        user = user_resp.user
        if not user:
            st.error("Email ou mot de passe incorrect.")
            return None

        # Stocker l'utilisateur dans session_state
        st.session_state['user'] = user
        st.success(f"Marhaban !")
        return user

    except Exception as e:
        st.error(f"Erreur login : {e}")
        return None


# -------------------------
# LOGOUT
# -------------------------
def logout():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass  # ignore si déjà déconnecté

    if 'user' in st.session_state:
        del st.session_state['user']
    st.success("Déconnecté !")


# -------------------------
# UTILITAIRE : vérifier si connecté
# -------------------------
def is_logged_in():
    return 'user' in st.session_state
