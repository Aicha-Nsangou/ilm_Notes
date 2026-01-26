import streamlit as st
from supabase_client import supabase
from datetime import datetime

def signup(email: str, password: str, full_name: str) -> dict:
    """
    Crée un compte Supabase (auth.users)
    L'utilisateur doit confirmer son email.
    """
    try:
        res = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name
                }
            }
        })

        if not res.user:
            return {
                "ok": False,
                "message": "Erreur lors de l'inscription"
            }
        return {
            "ok": True,
            "message": f"📩 {full_name},Un email de confirmation vous a été envoyé"
        }
        
    except Exception as e:
        return {
            "ok": False,
            "message": f"Erreur signup : {e}"
        }


# -------------------------
# Login
# -------------------------
def login(email: str, password: str) -> dict:
    """
    Connexion utilisateur.
    Bloque l'accès si email non confirmé.
    S'assure que le user existe dans public.users.
    """
    
    try:
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        user = res.user
           
        if not user:
            return {
                "ok": False,
                "message": "Identifiants invalides"
            }

        
           
        # ⛔ Email non confirmé
        if user.email_confirmed_at is None:
            supabase.auth.sign_out()
            return {
                "ok": False,
                "message": "⚠️ Veuillez confirmer votre email avant de continuer"
            }

        # ✅ Vérifier / créer user dans public.users
        profile = supabase.table("users") \
            .select("id, plan") \
            .eq("id", user.id) \
            .execute()

        if not profile.data:
            supabase.table("users").insert({
                "id": user.id,
                "full_name": user.user_metadata.get("full_name", ""),
                "plan": "free",
                "created_at": datetime.utcnow().isoformat()
            }).execute()

            plan = "free"
        else:
            plan = profile.data[0]["plan"]

        return {
            "ok": True,
            "user": {
                "id": user.id,
                "full_name": user.user_metadata.get("full_name", ""),
                "plan": plan
            }
        }

    except Exception as e:
        return {
            "ok": False,
            "message": f"Erreur login : {e}"
        }


# -------------------------
# Logout
# -------------------------
def logout():
    try:
        supabase.auth.sign_out()
    except Exception as e:
        st.error(f"Erreur de déconnexion : {e}")
    
    if 'user' in st.session_state:
        del st.session_state['user']
    st.success("Déconnecté avec succès")

# -------------------------
# UTILITAIRE : vérifier si connecté
# -------------------------
def is_logged_in():
    return 'user' in st.session_state
