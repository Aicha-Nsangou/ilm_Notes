from supabase import create_client
import streamlit as st


def get_power():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
    )
