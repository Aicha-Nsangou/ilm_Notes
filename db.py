# -----------------------------
# Base de données
# -----------------------------
import sqlite3
from datetime import datetime

conn = sqlite3.connect("ilm_notes.db", check_same_thread=False)
c = conn.cursor()
import traceback

c.execute('''
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_by TEXT,
    title TEXT,
    content TEXT,
    category TEXT,
    subtheme TEXT,
    reference TEXT,
    created_at TEXT
)
''')

# If migrating from an older DB without created_by, try to add the column.
try:
    c.execute("ALTER TABLE notes ADD COLUMN created_by TEXT")
except Exception:
    pass

# Table users
c.execute('''
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
plan TEXT DEFAULT 'free' -- free ou pro
)
''')

# Table custom categories
c.execute('''
CREATE TABLE IF NOT EXISTS custom_categories (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
category_name TEXT,
UNIQUE(username, category_name)
)
''')

conn.commit()

# -----------------------------
# Fonctions utilitaires
# -----------------------------


# --- Users ---

def create_user(username):
    try:
        c.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()
        return True         
    except sqlite3.IntegrityError:
        return False
    except Exception:
        with open("db_error.log", "a") as f:
            f.write(traceback.format_exc())
            f.write("\n")
        return False

def get_user_plan(username):    
    c.execute("SELECT plan FROM users WHERE username=?", (username,))
    res = c.fetchone()
    return res[0] if res else 'free'

def upgrade_plan(username):
    c.execute("UPDATE users SET plan='pro' WHERE username=?", (username,))
    conn.commit()

def downgrade_plan(username):
    c.execute("UPDATE users SET plan='free' WHERE username=?", (username,))
    conn.commit()

def get_all_users():
    c.execute("SELECT username, plan FROM users ORDER BY username")
    return c.fetchall()

def user_exists(username):
    c.execute("SELECT username FROM users WHERE username=?", (username,))
    return c.fetchone() is not None

def delete_note(note_id):
    c.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    return True

def update_note(note_id, title, content, category, subtheme, reference):
    c.execute("UPDATE notes SET title=?, content=?, category=?, subtheme=?, reference=? WHERE id=?",
              (title, content, category, subtheme, reference, note_id))
    conn.commit()
    return True

def get_note_by_id(note_id):
    c.execute("SELECT * FROM notes WHERE id=?", (note_id,))
    return c.fetchone()

def add_val(val = 0):
    return val

def add_custom_category(username, category_name):
    val = 4 + add_val()
    
    try:
        # Vérifier le nombre de catégories (max 10 total = 6 défaut + 4 custom)
        custom_count = c.execute("SELECT COUNT(*) FROM custom_categories WHERE username=?", (username,)).fetchone()[0]
        if custom_count >= val:
            return False  # Limite atteinte
        
        c.execute("INSERT INTO custom_categories (username, category_name) VALUES (?, ?)", 
                  (username, category_name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_custom_categories(username):
    c.execute("SELECT category_name FROM custom_categories WHERE username=?", (username,))
    return [row[0] for row in c.fetchall()]

def rename_category(username, old_name, new_name):
    try:
        c.execute("UPDATE custom_categories SET category_name=? WHERE username=? AND category_name=?", 
                  (new_name, username, old_name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def delete_category(username, category_name):
    c.execute("DELETE FROM custom_categories WHERE username=? AND category_name=?", 
              (username, category_name))
    conn.commit()
    return True
    
# --- Notes ---
def can_add_note(username):
    plan = get_user_plan(username)
    if plan == 'pro':
        return True
    c.execute("SELECT COUNT(*) FROM notes WHERE created_by=?", (username,))
    count = c.fetchone()[0]
    return count < 10

def add_note(username, title, content, category, subtheme, reference):
    if not can_add_note(username):
        return False
    c.execute("INSERT INTO notes (created_by, title, content, category, subtheme, reference, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
(username, title, content, category, subtheme, reference, datetime.now().isoformat())
)
    conn.commit()
    return True

def get_notes(filters=None,limit=10, offset=0):
    query = "SELECT * FROM notes WHERE 1=1"
    params = []

    if filters:
        if filters.get("category"):
            query += " AND category=?"
            params.append(filters["category"])
        if filters.get("subtheme"):
            query += " AND subtheme LIKE ?"
            params.append(f"%{filters['subtheme']}%")
        if filters.get("reference"):
            query += " AND reference LIKE ?"
            params.append(f"%{filters['reference']}%")

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    return c.execute(query, params).fetchall()