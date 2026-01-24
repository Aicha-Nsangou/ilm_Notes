from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import streamlit as st
from db import (add_note, get_notes, conn, can_add_note, get_user_plan, 
                upgrade_plan, downgrade_plan, get_all_users, delete_note, 
                update_note, add_val, add_custom_category, get_custom_categories,
                rename_category, delete_category)
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

def export_note_to_pdf(note):
    styles = getSampleStyleSheet()
    file_name = f"note_{note[0]}.pdf"
    doc = SimpleDocTemplate(file_name, pagesize=A4)
    story = []

    story.append(Paragraph(f"<b> {note[1]}</b>", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(note[2].replace('\n', '<br/>'), styles['BodyText']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f" Référence : {note[5]}", styles['Italic']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Généré par Ilm Notes : {note[6]}", styles['Normal']))

    doc.build(story)
    return file_name

def format_for_whatsapp(note):
    return f"📘 *{note[2]}*\n\n{note[3]}\n\n📖 Réf : {note[6]}\n— partagé via Ilm Notes"

# -----------------------------
# Accueil
# -----------------------------
def page_accueil():
    st.title("📘 Ilm Notes")
    st.divider()
    st.markdown("**Organiser, préserver et réviser la science**")
    st.markdown("""
    Ilm Notes est un outil simple destiné aux étudiants en sciences islamiques.
    Il vous aide à structurer vos notes, réviser efficacement et partager la science avec adab.
    """)
    
    st.divider()
    st.header("🎯 Choisissez votre plan")
    
    # Afficher les deux plans côte à côte dans des containers
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("### 📗 Plan GRATUIT")
            st.markdown("""
            ✅ Ajouter jusqu'à **10 notes**
            
            ✅ Organiser par catégories
            
            ✅ Rechercher et filtrer
            
            ✅ Réviser vos notes
            
            ✅ Exporter en PDF
            
            ✅ Partager via WhatsApp
            """)
            if st.button("▶️ Commencer GRATUIT", key="btn_free", use_container_width=True):
                st.session_state.next_page = "Ajouter une note"
                st.info("Cliquez sur 'Ajouter une note' dans le menu")
    
    with col2:
        with st.container(border=True):
            st.markdown("### ⭐ Plan PRO")
            st.markdown("""
            ✅ Notes **ILLIMITÉES**
            
            ✅ Ajouter des catégories
            
            ✅ Suivi de la progression
            
            ✅ Réviser vos notes
            
            ✅ Exporter en PDF
            
            ✅ Partager via WhatsApp
            
            """)
            if st.button("💎 Passer au PRO", key="btn_pro", use_container_width=True):
                st.warning("Contactez l'administrateur pour l'abonnement PRO")
                st.info("""
                📱 Whatsapp: https://wa.me/237698491583
                
                Obtenez l'accès illimité et débloquez toutes les fonctionnalités premium!
                """)
    st.markdown("✨ **Bien plus à venir In schaa Allah...**")
    st.markdown("**Restez à l'écoute pour les futures mises à jour et fonctionnalités!**")
    st.divider()
    with st.container(border=True):
        st.info("💡 Commencez gratuitement et passez au PRO quand vous êtes prêt!")


# -----------------------------
# Ajouter une note
# -----------------------------  
def page_ajouter_note(username):
    st.header("➕ Ajouter une nouvelle note")
    st.divider()
    c = conn.cursor()
    
    user_plan = get_user_plan(username)
    
    if user_plan == 'free':
        c.execute("SELECT COUNT(*) FROM notes WHERE created_by=?", (username,))
        count = c.fetchone()[0]
        st.info(f"Plan gratuit : {count}/10 notes utilisées")
    
    # Catégories par défaut
    default_categories = ["Aqida", "Fiqh", "Hadith"]
    
    # Si premium, ajouter les catégories personnalisées et gérer les catégories
    if user_plan == 'pro':
        custom_cats = get_custom_categories(username)
        all_categories = default_categories + custom_cats
        
        # Section de gestion des catégories pour PRO
        with st.expander("🏷️ Gérer mes catégories"):
            st.subheader("Catégories personnalisées (max 4)")
            st.caption(f"Vous avez {len(custom_cats)}/4 catégories personnalisées")
            
            # Afficher les catégories personnalisées
            if custom_cats:
                st.markdown("**Vos catégories:**")
                for idx, cat in enumerate(all_categories):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"• {cat}")
                    with col2:
                        if st.button("✏️", key=f"rename_{cat}", help="Renommer"):
                            st.session_state.rename_cat = cat
                    with col3:
                        if st.button("🗑️", key=f"del_{cat}", help="Supprimer"):
                            delete_category(username, cat)
                            st.success(f"Catégorie '{cat}' supprimée")
                            st.rerun()
                    st.divider()
                # Formulaire de renommage si nécessaire
                if st.session_state.get('rename_cat'):
                    st.divider()
                    old_name = st.session_state.rename_cat
                    new_name = st.text_input(f"Nouveau nom pour '{old_name}'")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Confirmer"):
                            if new_name and new_name.strip() and new_name != old_name:
                                rename_category(username, old_name, new_name)
                                st.success(f"Catégorie renommée en '{new_name}'")
                                del st.session_state.rename_cat
                                st.rerun()
                    with col2:
                        if st.button("❌ Annuler"):
                            del st.session_state.rename_cat
                            st.rerun()
            else:
                st.info("Aucune catégorie personnalisée pour le moment")
            new_category = st.text_input("➕ Ajouter une nouvelle catégorie (optionnel, max 4)")
            if st.button("Ajouter"):
                # Ajouter la nouvelle catégorie si fournie et premium
                if new_category and new_category.strip():
                    result = add_custom_category(username, new_category.strip())
                if not result:
                    st.error("Limite de catégories atteinte (max 4 personnalisées)")  
                
        
    else:
        all_categories = default_categories

    with st.form("add_note_form", clear_on_submit=True):
        title = st.text_input("Titre de la note")
        content = st.text_area("Contenu")
        category = st.selectbox("Catégorie", all_categories)
        subtheme = st.text_input("Sous-thème (optionnel)")
        reference = st.text_input("Référence (livre, savant, cours)")
        submitted = st.form_submit_button("Enregistrer")
                    
        if submitted:
            if title and content:
                if add_note(username, title, content, category, subtheme, reference):
                    st.success("Note enregistrée avec succès")
                else:
                    st.warning("Limite atteinte. Passez au plan PRO pour ajouter des notes illimitées.")
            else:
                st.error("Le titre et le contenu sont obligatoires")
    
    # Bouton Passer au PRO en dehors du formulaire
    if can_add_note(username) == False:
        if st.button("💳 Passer au PRO"):
            st.info(f"Redirection vers l'abonnement... contactez l'administrateur pour plus de détails.\n\n Whatsapp: https://wa.me/237698491583")
            
# -----------------------------
#Organisation & Recherche
# -----------------------------
def page_organisation_recherche():
    st.header("🗂️ Organisation & Recherche")
    st.divider()
    category = st.selectbox("Filtrer par catégorie", ["", "Aqida", "Fiqh", "Tafsir", "Hadith", "Usul", "Akhlaq"])
    subtheme = st.text_input("Filtrer par sous-thème")
    reference = st.text_input("Filtrer par référence")
    # Pagination
    notes_per_page = 10
    if "page_num" not in st.session_state:
        st.session_state.page_num = 1
    offset = (st.session_state.page_num - 1) * notes_per_page
    notes = get_notes({
        "category": category if category else None,
        "subtheme": subtheme,
        "reference": reference
    }, limit=notes_per_page, offset=offset)
    st.divider()
    st.subheader(f"Résultats de la recherche ({len(notes)} notes trouvées)")
    for note in notes:
            with st.expander(note[2]):
                st.markdown(note[3])
                st.caption(f"📖 {note[6]}")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    pdf_file = export_note_to_pdf(note)
                    with open(pdf_file, "rb") as f:
                        st.download_button("📄 Export PDF", f, file_name=pdf_file)
                with col_b:
                    if st.button("📋 Copier" , key=f"copy_{note[0]}"):
                        st.code(format_for_whatsapp(note))
                        st.success("Contenu prêt à être collé dans WhatsApp")
                with col_c:
                    if st.button("✏️ Modifier", key=f"edit_{note[0]}"):
                        st.session_state.edit_note_id = note[0]
                    if st.button("🗑️ Supprimer", key=f"delete_{note[0]}"):
                        delete_note(note[0])
                        st.success("Note supprimée")
                        st.rerun()
            
            # Afficher le formulaire de modification si cette note est sélectionnée
            if st.session_state.get('edit_note_id') == note[0]:
                st.divider()
                st.subheader("Modifier la note")
                with st.form(f"edit_form_{note[0]}"):
                    new_title = st.text_input("Titre", value=note[2])
                    new_content = st.text_area("Contenu", value=note[3])
                    new_category = st.selectbox("Catégorie", ["Aqida", "Fiqh", "Tafsir", "Hadith", "Usul", "Akhlaq"], index=0)
                    new_subtheme = st.text_input("Sous-thème", value=note[5] if note[5] else "")
                    new_reference = st.text_input("Référence", value=note[6] if note[6] else "")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Sauvegarder"):
                            update_note(note[0], new_title, new_content, new_category, new_subtheme, new_reference)
                            st.success("Note mise à jour")
                            del st.session_state.edit_note_id
                            st.rerun()
                    with col2:
                        if st.form_submit_button("❌ Annuler"):
                            del st.session_state.edit_note_id
                            st.rerun()

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Page précédente") and st.session_state.page_num > 1:
            st.session_state.page_num -= 1
    with col2:
        if st.button("Page suivante ➡️"):
            st.session_state.page_num += 1      


# -----------------------------
# Révision
# -----------------------------
def page_revision():
    st.header("🔁 Révision guidée")
    st.divider()
    notes = get_notes()

    if not notes:
        st.info("Aucune note disponible pour la révision")
    else:
        if "index" not in st.session_state:
            st.session_state.index = 0

        note = notes[st.session_state.index]

        st.subheader(note[1])
        st.markdown(note[2])
        st.caption(f"📖 {note[5]}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Précédent") and st.session_state.index > 0:
                st.session_state.index -= 1
        with col2:
            if st.button("Suivant ➡️") and st.session_state.index < len(notes) - 1:
                st.session_state.index += 1
          
# -----------------------------
# Progression des notes
# -----------------------------
def page_progression_notes():
    st.header("📊 Progression par catégorie (ajout de notes)")
    st.divider()
    
    # Vérifier le plan et la date pour les utilisateurs gratuits
    if 'username' in st.session_state:
        username = st.session_state.username
        user_plan = get_user_plan(username)
        
        if user_plan == 'free':
            # Vérifier la date de création du premier compte (date du plus ancienne note)
            cursor = conn.cursor()
            cursor.execute("SELECT created_at FROM notes WHERE created_by=? ORDER BY created_at ASC LIMIT 1", (username,))
            result = cursor.fetchone()
            
            if result:
                first_note_date = datetime.fromisoformat(result[0])
                week_ago = datetime.now() - timedelta(days=7)
                
                if first_note_date < week_ago:
                    st.warning("⏰ Votre période gratuite d'accès à la progression a expiré (7 jours)")
                    st.info("Passez au plan PRO pour continuer à suivre votre progression")
                    if st.button("💎 Passer au PRO"):
                        st.warning("Contactez l'administrateur pour l'abonnement PRO")
                        st.info("📱 Whatsapp: https://wa.me/237698491583")
                    return
            else:
                st.info("Aucune note créée. Commencez à ajouter des notes pour voir votre progression!")
                return

    # Récupérer le nombre de notes par catégorie
    cursor = conn.cursor()
    cursor.execute("SELECT category, COUNT(*) FROM notes GROUP BY category")
    data = cursor.fetchall()

    if not data:
        st.info("Aucune note enregistrée pour le moment.")
        return

    # DataFrame
    df = pd.DataFrame(data, columns=["category", "count"])

    # Graphique Altair - bar chart
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('category:N', sort='-y', title='Catégorie'),
        y=alt.Y('count:Q', title='Nombre de notes'),
        color='category:N',
        tooltip=['category', 'count']
    ).properties(
        width=700,
        height=400
    )

    st.altair_chart(chart, width='stretch')


# -----------------------------
# Admin Panel
# -----------------------------
def page_admin():
    st.header("🔐 Panneau Administrateur")
    st.divider()
    
    # Admin authentication with password
    admin_password = st.text_input("Mot de passe admin", type="password")
    
    if admin_password != "Aicha-2025":  # Change this to a secure password
        if admin_password:
            st.error("Mot de passe incorrect")
        return
    
    st.success("✅ Connecté en tant qu'administrateur")
    st.divider()
    
    # Tab for different admin actions
    admin_tab = st.selectbox("Sélectionnez une action", ["Gérer les plans utilisateurs", "Statistiques"])
    
    if admin_tab == "Gérer les plans utilisateurs":
        st.subheader("📋 Gestion des Plans Utilisateurs")
        
        all_users = get_all_users()
        
        if not all_users:
            st.info("Aucun utilisateur enregistré")
            return
        
        # Create a dataframe for better display
        user_df = pd.DataFrame(all_users, columns=["Username", "Plan"])
        
        st.dataframe(user_df, width='stretch')
        
        st.divider()
        st.subheader("🔄 Modifier le plan d'un utilisateur")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            target_user = st.selectbox(
                "Sélectionnez un utilisateur",
                [user[0] for user in all_users]
            )
        
        with col2:
            new_plan = st.selectbox(
                "Nouveau plan",
                ["free", "pro"]
            )
        
        with col3:
            add_cat = st.selectbox(
                "New feature",
                ["categorie",]
                )
            
        if st.button("✅ Appliquer le changement"):
            if add_cat == "categorie":
                add_val(3)
                st.success(f"✅ {target_user} est passé a 10 categories")
            if new_plan == "pro":
                upgrade_plan(target_user)
                st.success(f"✅ {target_user} est passé au plan PRO")
            else:
                downgrade_plan(target_user)
                st.success(f"✅ {target_user} est revenu au plan GRATUIT")
            st.rerun()
    
    elif admin_tab == "Statistiques":
        st.subheader("📊 Statistiques Globales")
        
        cursor = conn.cursor()
        
        # Nombre total d'utilisateurs
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Nombre d'utilisateurs PRO
        cursor.execute("SELECT COUNT(*) FROM users WHERE plan='pro'")
        pro_users = cursor.fetchone()[0]
        
        # Nombre total de notes
        cursor.execute("SELECT COUNT(*) FROM notes")
        total_notes = cursor.fetchone()[0]
        
        # Nombre de notes par utilisateur
        cursor.execute("SELECT created_by, COUNT(*) as count FROM notes GROUP BY created_by ORDER BY count DESC")
        notes_per_user = cursor.fetchall()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Utilisateurs totaux", total_users)
        
        with col2:
            st.metric("Utilisateurs PRO", pro_users)
        
        with col3:
            st.metric("Utilisateurs GRATUIT", total_users - pro_users)
        
        with col4:
            st.metric("Notes totales", total_notes)
        
        st.divider()
        
        st.subheader("📝 Notes par utilisateur")
        if notes_per_user:
            notes_df = pd.DataFrame(notes_per_user, columns=["Utilisateur", "Nombre de notes"])
            st.dataframe(notes_df, width='stretch')
        else:
            st.info("Aucune note enregistrée")
            
# -----------------------------
# Démo
# -----------------------------
def page_demo():
    st.header("🎬 Démo d'Ilm Notes")
    st.divider()
    st.markdown("""
    Voici une presentation démontrant les principales fonctionnalités d'Ilm Notes:
    
    - Ajouter et organiser des notes
    - Réviser efficacement
    - Suivre la progression
    - Exporter et partager des notes
    
    *Vidéo à venir In schaa Allah...*
    """)
    
    st.divider()
    st.title("📘 Comment utiliser Ilm Notes")

    st.markdown("""
    **Ilm Notes** est un outil simple pour aider les étudiants en sciences islamiques
    à organiser, réviser et partager leurs notes بسهولة.
    """)

    st.divider()

    st.subheader("1️⃣ Ajouter une note")
    st.markdown("""
    - Choisis une **catégorie** (Fiqh, Aqida, Tafsir, Hadith, etc.)
    - Écris ta note
    - Ajoute une **référence** si nécessaire
    - Clique sur **Ajouter**
    """)

    st.subheader("2️⃣ Organiser ses notes")
    st.markdown("""
    - Utilise le **filtre par catégorie**
    - Retrouve facilement ce que tu as déjà étudié
    """)

    st.subheader("3️⃣ Suivre ta progression")
    st.markdown("""
    - Le graphique montre **sur quelles catégories tu travailles le plus**
    - Plus tu ajoutes de notes, plus ta courbe évolue
    """)

    st.subheader("4️⃣ Partager une note")
    st.markdown("""
    - Clique sur **Copier pour WhatsApp**
    - La note est formatée proprement
    - Tu peux la coller directement dans un groupe ou une chaîne
    """)

    st.subheader("5️⃣ Version gratuite et Pro")
    st.markdown("""
    **Gratuit**
    - Jusqu’à 10 notes

    **Pro**
    - Notes illimitées
    - Accès complet
    """)

    st.divider()

    st.markdown("""
    > *Qu’Allah mette la baraka dans ce savoir  
    et le rende bénéfique pour celui qui l’apprend et le partage.*
    """)
    
def custom_footer():
    st.markdown(
        """
        <style>
        .ilm-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #fafafa;
            text-align: center;
            padding: 8px 0;
            font-size: 13px;
            color: #444;
            border-top: 1px solid #ddd;
        }
        </style>

        <div class="ilm-footer">
            <strong>Ilm Notes</strong> 🌙<br>
            <em>
            اللهم علمنا ما ينفعنا وانفعنا بما علمتنا وزدنا علما
            </em>
        </div>
        """,
        unsafe_allow_html=True
    )



