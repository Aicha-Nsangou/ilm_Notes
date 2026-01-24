from supabase_client import supabase

supabase.table("categories").insert({
    "name": "Fiqh"
}).execute()
