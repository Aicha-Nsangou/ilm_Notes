from supabase_client import supabase
from datetime import datetime

# --- User Plans ---
def get_user_plan(user_id):
    res = (
        supabase
        .table("users")
        .select("plan")
        .eq("id", user_id)
        .execute()
    )
    return res.data[0]["plan"] if res.data else "free"

# --- Upgrade / Downgrade Plans ---
def upgrade_plan(user_id):
    supabase.table("users").update(
        {"plan": "pro"}
    ).eq("id", user_id).execute()


def downgrade_plan(user_id):
    supabase.table("users").update(
        {"plan": "free"}
    ).eq("id", user_id).execute()
    
# --- Get All Users ---
def get_all_users_admin():
    res = (
        supabase
        .table("users")
        .select("id, full_name, plan, created_at")
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []

# --- User Existence Check ---
def user_exists(user_id):
    res = supabase.table("users").select("id").eq("id", user_id).execute()
    return len(res.data) > 0

# --- Category Management ---
def get_categories():
    res = supabase.table("categories").select("name").order("name").execute()
    return res.data

def delete_custom_category(user_id, category_name):
    supabase.table("custom_categories").delete().eq("user_id", user_id).eq("category_name", category_name).execute()

def add_custom_category(user_id, category_name):
    MAX_CUSTOM = 4  # free

    res = (
        supabase
        .table("custom_categories")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .execute()
    )

    if res.count >= MAX_CUSTOM:
        return False

    try:
        supabase.table("custom_categories").insert({
            "user_id": user_id,
            "category_name": category_name
        }).execute()
        return True
    except Exception:
        return False

    
def get_custom_categories(user_id):
    res = supabase.table("custom_categories").select("category_name").eq("user_id", user_id).execute()
    return res.data

def rename_custom_category(user_id, old_name, new_name):
    try:
        supabase.table("custom_categories").update(
            {"category_name": new_name}
        ).eq("user_id", user_id).eq("category_name", old_name).execute()
        return True
    except Exception:
        return False

    
# --- Note Management ---
def delete_note(note_id):
    supabase.table("notes").delete().eq("id", note_id).execute()
    return True

def update_note(note_id, title, content, category, subtheme, reference):
    supabase.table("notes").update({
        "title": title,
        "content": content,
        "category": category,
        "subtheme": subtheme,
        "reference": reference
    }).eq("id", note_id).execute()
    return True

def get_note_by_id(user_id):
    res = supabase.table("notes").select("*").eq("user_id", user_id).single().execute()
    return res.data

def can_add_note(user_id):
    if get_user_plan(user_id) == "pro":
        return True

    res = (
        supabase
        .table("notes")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .execute()
    )
    return res.count < 10

def add_note(user_id, title, content, category, subtheme, reference):
    if not can_add_note(user_id):
        return False

    supabase.table("notes").insert({
        "user_id": user_id,
        "title": title,
        "content": content,
        "category": category,
        "subtheme": subtheme,
        "reference": reference,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    return True

def get_notes(filters=None, limit=10, offset=0):
    query = supabase.table("notes").select("*")

    if filters:
        if filters.get("user_id"):
            query = query.eq("user_id", filters["user_id"])
        if filters.get("category"):
            query = query.eq("category", filters["category"])
        if filters.get("subtheme"):
            query = query.ilike("subtheme", f"%{filters['subtheme']}%")
        if filters.get("reference"):
            query = query.ilike("reference", f"%{filters['reference']}%")

    res = (
        query
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )

    return res.data

def count_notes(user_id):
    res = supabase.table("notes").select("id", count="exact").eq("user_id", user_id).execute()
    return res.count or 0

def get_note_counts_by_category(user_id):
    res = supabase.table("notes").select("category").eq("user_id", user_id).execute()
    return res.data

def is_admin(user_id):
    res = (
        supabase
        .table("users")
        .select("is_admin")
        .eq("id", user_id)
        .single()
        .execute()
    )
    return res.data and res.data["is_admin"] is True

def get_total_notes():
    res = supabase.table("notes").select("id", count="exact").execute()
    return res.count or 0

#user pro
def count_user_pro():
    res = supabase.table("users").select("id", count="exact").eq("plan", "pro").execute()
    return res.count or 0
