import base64
from streamlit_option_menu import option_menu
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from auth import signup, login, logout, is_logged_in,auto_login
from supadb import ( 
                can_add_note,
                get_user_plan,
                add_note,count_notes,
                get_categories,get_notes,
                delete_note,rename_custom_category,
                add_custom_category,
                get_custom_categories,
                delete_custom_category,
                update_note,get_note_by_id,
                get_note_counts_by_category,
                get_all_users_admin,
                upgrade_plan,count_user_pro,
                downgrade_plan,get_total_notes,is_admin
                
                )

# --- Export Note to PDF ---
def export_note_to_pdf(note: dict):
    styles = getSampleStyleSheet()
    file_name = f"{note['title']}.pdf"

    doc = SimpleDocTemplate(file_name, pagesize=A4)
    story = []

    story.append(Paragraph(f"<b>{note['title']}</b>", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(note['content'].replace('\n', '<br/>'), styles['BodyText']))
    story.append(Spacer(1, 12))

    if note.get("reference"):
        story.append(Paragraph(f"Référence : {note['reference']}", styles['Italic']))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Généré par Ilm Notes", styles['Normal']))

    doc.build(story)
    return file_name

#--- Format Note for WhatsApp ---
def format_for_whatsapp(note: dict):
    return (
        f"📘 *{note['title']}*\n\n"
        f"{note['content']}\n\n"
        f"📖 Réf : {note.get('reference','—')}\n"
        f"— partagé via Ilm Notes"
    )

# --- Set Background Image ---
def set_bg_local(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    .stApp {{
        font-family: 'Poppins', sans-serif !important;
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        background-color: rgba(255,255,255,0.85);
        backdrop-filter: blur(6px);

    }}
    input:focus,
    textarea:focus,
    select:focus {{
    outline: none !important;
    box-shadow: none !important;
    border: 1px solid rgba(0,0,0,0.15) !important;
    }}
    </style>
    <div class="overlay"></div>
    """,
    unsafe_allow_html=True
    )
    
#navbar
def navbar_custom():
    if "page" not in st.session_state:
        st.session_state.page = "Note"
    # --- CSS pour navbar fixe ---
    st.markdown("""
        <style>
        .main {
            padding-bottom: 90px;
        }
        div[data-testid="stVerticalBlock"]:has(.whatsapp-footer) {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            border-top: 1px solid #ddd;
            z-index: 1000;
            padding-top: 5px;
        }
        .whatsapp-footer .nav-link {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 12px !important;
            color: #444 !important;
        }
        .whatsapp-footer .icon {
            font-size: 20px !important;
            margin-bottom: 3px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="bottom-nav">', unsafe_allow_html=True)
    
    footer = st.container()
    with footer:
        selected = option_menu(
        menu_title=None,
        options= ["Note", "Organisation", "Révision", "Progression","Compte"],
        icons=["pencil-square", "folder2-open", "arrow-repeat", "bar-chart", "person", "shield-lock"],
        menu_icon="cast",
        default_index=["Note", "Organisation", "Révision", "Progression","Compte"].index(st.session_state.page),
        orientation="horizontal",
        styles={
            "container": { "padding": "0!important","background-color": "#f0f2f6", "border-radius": "5px"},
            "icon": {"color": "olive", "font-size": "20px"}, 
            "nav-link": {
                "font-size": "16px",
                "text-align": "center",
                "margin":"0px",
                "color": "black",
                "--hover-color": "#eee",
                "display":"flex",
                "flex-direction": "column",
                "justify-content":"start",
                "align-items":"center",
            },
            "nav-link-selected": {"border-bottom": "5px solid crimson", "background-color": "#f0f2f6", "border-radius": "1px","font-weight": "bold"},
        }
        )
        st.markdown('<div class="whatsapp-footer"></div>', unsafe_allow_html=True)
    st.session_state.page = selected
    return selected

# -----------------------------
# Accueil
# -----------------------------
def page_accueil():
    st.markdown(
        """
        <h2 style="text-align:center;"> ILM NOTES</h2>
        <p style="text-align:center; font-style:italic;">
        Un espace simple pour préserver et organiser la science islamique.
        </p>
        """,
        unsafe_allow_html=True
    )
    st.divider()
    with st.expander("📚 Qu’est-ce que Ilm Notes ?"):
        st.markdown("""
            **Ilm Notes** est un outil conçu pour les étudiants, enseignants et autodidactes
            en sciences islamiques.

            Il permet de :
            - prendre des notes rapidement  
            - les classer par catégories et thèmes  
            - retrouver facilement une information  
            - visualiser sur quoi tu travailles le plus
            - réviser efficacement
            - partager la science avec adab
    
        """)
    with st.expander("🎯 Pourquoi Ilm Notes ?"):
        st.markdown("""
            Parce que la science se perd facilement :
            - dans les carnets éparpillés  
            - dans les discussions WhatsApp  
            - dans les fichiers non organisés  

            **Ilm Notes t’aide à garder ton ‘ilm accessible et structuré.**
        """)
    
    with st.expander("📚 Dans quel contexte ?"):
        st.markdown(""" 
        Ilm Notes s’utilise :
        - pendant ou après un cours
        - lors de la lecture d’un livre
        - pour préparer un rappel ou un enseignement
        - sur téléphone ou ordinateur
    
        **L’objectif est d’avoir un espace calme, rapide et structuré.**
        """)

    with st.expander("▶️ Nos plans"):
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
                    st.session_state.next_page = "Note"
    
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
                        💳 Paiement Orange Money

                        📱 Numéro : 698 491 583 
                        💰 Montant : 2 000 FCFA / mois  
                        📝 Référence : Aicha Nsangou Mama Awouolou

                        📩 Envoyez le screenshot sur WhatsApp :
                        👉 https://wa.me/237698491583
                    """)

        st.markdown("✨ **Bien plus à venir In schaa Allah...**")
        st.markdown("**Restez à l'écoute pour les futures mises à jour et fonctionnalités!**")
        st.divider()
        with st.container(border=True):
            st.info("💡 Commencez gratuitement et passez au PRO quand vous êtes prêt!")
    with st.expander("🧠 Vos avis compte"):
        st.markdown("""
            <style>   
            .avis{
                display: inline-block;
                padding: 10px 20px;
                background-color: #25D366;
                color: white;
                border-radius: 8px;
                text-decoration: none;
                font-weight: bold;
                text-align:center;
                margin-top: 20px;
                }
            </style>


            <div class="avis">
                <a href="https://wa.me/237698491583?text=Assalamu%20alaykum%2C%20j%27utilise%20Ilm%20Notes%20et%20voici%20mon%20avis%20:" 
                target="_blank">
                    💬 Mon avis 
                </a>
            </div>
        """, unsafe_allow_html=True)
    st.info("🌱 Projet en phase de test (MVP) – Vos retours sont les bienvenus.")

    
    # Afficher les deux plans côte à côte dans des containers
    


# --- Page: Ajouter une Note ---
def page_ajouter_note(user_id):
    st.header("➕ Ajouter une nouvelle note")
    st.divider()
    try :
        plan = get_user_plan(user_id)
    except Exception as e:
        st.error(f"Erreur lors de la récupération du plan utilisateur : {e}")
        return

    if plan == "free":
        count = count_notes(user_id)
        st.info(f"Plan gratuit : {count}/10 notes utilisées")

        # 🔹 Catégories depuis Supabase
        categories = get_categories()
        category_name = {c["name"] for c in categories}
        all_categories = list(category_name)
    else:
        custom_cats = get_custom_categories(user_id)
        custom_cats_names = {c["name"] for c in custom_cats}
        all_categories = list(category_name) + list(custom_cats_names)
        # Gestion des catégories personnalisées pour les utilisateurs PRO
        with st.expander("⚙️ Gérer les catégories personnalisées"):
            custom_cats = get_custom_categories(user_id)
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
                            delete_custom_category(user_id, cat)
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
                                rename_custom_category(user_id, old_name, new_name)
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
                    result = add_custom_category(user_id, new_category.strip())
                if not result:
                    st.error("Limite de catégories atteinte (max 4 personnalisées)")  

            
    with st.form("add_note_form", clear_on_submit=True):
        title = st.text_input("Titre")
        content = st.text_area("Contenu")
        category = st.selectbox("Catégorie", all_categories)
        subtheme = st.text_input("Sous-thème")
        reference = st.text_input("Référence")

        submitted = st.form_submit_button("Enregistrer")

        if submitted:
            if not title or not content:
                st.error("Titre et contenu obligatoires")
                return

            ok = add_note(
                user_id=user_id,
                title=title,
                content=content,
                category=category,
                subtheme=subtheme,
                reference=reference
            )

            if ok:
                st.success("Note enregistrée")
                st.toast("👉 Vas sur **🗂️ Organisation** pour voir ta note. **>>**", icon="🕌")
            else:
                st.warning("Limite atteinte. Passez au plan PRO.")
             
            # Bouton Passer au PRO en dehors du formulaire
            if can_add_note(user_id) == False:
                if st.button("💳 Passer au PRO"):
                    st.info("""
                    💳 Paiement Orange Money

                    📱 Numéro : 698 491 583 
                    💰 Montant : 2 000 FCFA / mois  
                    📝 Référence : Aicha Nsangou Mama Awouolou

                    📩 Envoyez le screenshot sur WhatsApp :
                    👉 https://wa.me/237698491583
                """)


# --- Page: Organisation & Recherche ---
def page_organisation_recherche(user_id):
    st.header("🗂️ Organisation & Recherche")
    if "page_num" not in st.session_state:
        st.session_state.page_num = 1
    plan = get_user_plan(user_id)
    if plan == "free":
        cat = get_categories()
        category_name = {c["name"] for c in cat}
        all_categories = list(category_name)
        category = st.selectbox("Filtrer par catégorie", all_categories)
    else:
        cat = get_categories()
        custom_cats = get_custom_categories(user_id)
        custom_cats_names = [c["name"] for c in custom_cats]
        all_categories = list(cat) + list(custom_cats_names)
        category = st.selectbox("Filtrer par catégorie", all_categories)
    subtheme = st.text_input("Sous-thème")
    reference = st.text_input("Référence")

    notes = get_notes({
        "user_id": user_id,
        "category": category or None,
        "subtheme": subtheme or None,
        "reference": reference or None
    })
    st.divider()
    st.subheader(f"Résultats : {len(notes)} note(s) trouvée(s)")
    for note in notes:
        with st.expander(note["title"]):
            st.markdown(note["content"])
            st.caption(f"📖 {note.get('reference','—')}")

            col1, col2, col3,col4 = st.columns(4)

            with col1:
                pdf = export_note_to_pdf(note)
                with open(pdf, "rb") as f:
                    st.download_button("📄 PDF", f, file_name=pdf)

            with col2:
                if st.button("📋 Copier", key=f"copy_{note['id']}"):
                    st.code(format_for_whatsapp(note))
            with col3:
                if st.button("✏️ Modifier", key=f"edit_{note['id']}"):
                    st.session_state.edit_note_id = note["id"]
                    st.succes("Note mise a jour")
                    st.session_state.edit_note_id = None
                    st.rerun()
            with col4:
                if st.button("🗑️ Supprimer", key=f"del_{note['id']}"):
                    delete_note(note["id"])
                    st.rerun()
            
            if st.session_state.get('edit_note_id') == note["id"]:
                st.divider()
                st.subheader("Modifier la note")
                with st.form(f"edit_form_{note['id']}"):
                    new_title = st.text_input("Titre", value=note["title"])
                    new_content = st.text_area("Contenu", value=note["content"])
                    new_category = st.selectbox("Catégorie", ["Aqida", "Fiqh", "Tafsir", "Hadith", "Usul", "Akhlaq"], index=0)
                    new_subtheme = st.text_input("Sous-thème", value=note["subtheme"] if note["subtheme"] else "")
                    new_reference = st.text_input("Référence", value=note["reference"] if note["reference"] else "")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Sauvegarder"):
                            update_note(note["id"], new_title, new_content, new_category, new_subtheme, new_reference)
                            st.success("Note mise à jour")
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

#--- Page: Revision ---
def page_revision(user_id):
    st.header("🔁 Révision guidée")
    st.divider()
    notes = get_notes({"user_id": user_id})

    if not notes:
        st.info("Aucune note disponible pour la révision")
    else:
        if "index" not in st.session_state:
            st.session_state.index = 0

        note = notes[st.session_state.index]

        st.subheader(note["title"])
        st.markdown(note["content"])
        st.caption(f"📖 {note['reference']}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Précédent") and st.session_state.index > 0:
                st.session_state.index -= 1
        with col2:
            if st.button("Suivant ➡️") and st.session_state.index < len(notes) - 1:
                st.session_state.index += 1
                
# -------------------------
# Progression
def page_progression_notes(user_id):
    st.header("📊 Progression des notes")
    st.divider()
    if user_id in st.session_state:
        user_plan = get_user_plan(user_id)
        
        if user_plan == 'free':
            # Vérifier la date de création du premier compte (date du plus ancienne note)
            result = get_note_by_id(user_id)
            
            if result:
                first_note_date = datetime.fromisoformat(result['created_at'])
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
    data = get_note_counts_by_category(user_id) or []
    if not data:
        st.info("Aucune note enregistrée pour le moment.")
        return

    # DataFrame
    df = pd.DataFrame(data)
    # Comptage côté pandas
    df = df.groupby("category").size().reset_index(name="count")
    
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
    
def page_admin(user_id):
    st.header("🛡️ Panneau Administrateur")
    st.divider()
    
    # Tab for different admin actions
    admin_tab = st.selectbox("Sélectionnez une action", ["Gérer les plans utilisateurs", "Statistiques"])
    all_users = get_all_users_admin()
    
    if admin_tab == "Gérer les plans utilisateurs":
        st.subheader("📋 Gestion des Plans Utilisateurs")
        if not all_users:
            st.info("Aucun utilisateur enregistré")
            return
        
        # Create a dataframe for better display
        user_df = pd.DataFrame(all_users)
        user_df = user_df.groupby(["full_name", "plan"]).size().reset_index(name="Nombre d'utilisateurs")
        st.dataframe(user_df, width='stretch')
        
        st.divider()
        st.subheader("🔄 Modifier le plan d'un utilisateur")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            target_user = st.selectbox(
                "Sélectionnez un utilisateur",
                [user["full_name"] for user in all_users]
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
        
        
        total_users = len(all_users)
        
        # Nombre d'utilisateurs PRO
        pro_users = count_user_pro()
        
        # Nombre total de notes
        total_notes = get_total_notes()
        
        # Nombre de notes par utilisateur
        notes_per_user = count_notes(user_id)
        
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
        
        #st.subheader("📝 Notes par utilisateur")
        #if notes_per_user:
            #notes_df = pd.DataFrame(notes_per_user, columns=["Utilisateur", "Nombre de notes"])
            #st.dataframe(notes_df, width='stretch')
        #else:
            #st.info("Aucune note enregistrée")
#login page
def login_page():
    
    col1, col2 = st.columns([1,2])
    if is_logged_in() is False:
        with col1:
            with st.expander("🔐 Connexion"):
                with st.container(border=True):
                    email = st.text_input("Email")
                    password = st.text_input("Mot de passe", type="password")
                    if st.button("Se connecter"):
                        with st.spinner("Chargement..."):
                            res = login(email, password)
                            if res["ok"]:
                                st.session_state['user'] = auto_login()
                                st.success("Connexion réussie")
                            else:
                                st.error(res["message"])
                    if st.button("Nouveau compte"):
                        with col2:       
                            with st.expander("👤 Créer un compte"):
                                with st.container(border=True):
                                    full_name = st.text_input("Nom complet")
                                    email2 = st.text_input("Email pour inscription")
                                    password2 = st.text_input("Mot de passe", type="password", key="signup")
                                    if st.button("S'inscrire"):
                                        with st.spinner("Chargement..."):
                                            res = signup(email2, password2, full_name)
                                            if res["ok"]:
                                                st.success(res["message"])
                                            else:
                                                st.error(res["message"])
    else:
        st.subheader(f"Marhaban !")
        st.button("Se déconnecter", on_click=logout)
# -----------------------------
# Démo
# -----------------------------
def page_demo():
    tab1,tab2,tab3= st.tabs(["Comptes","A propos de Ilm Notes","Demo"])
    with tab1:
        login_page()
        st.divider()
        if is_admin(st.session_state["user"].id):
            page_admin(st.session_state["user"].id)
        
    with tab2:
        page_accueil()
        
    with tab3:
        st.header("🎬 Démo d'Ilm Notes")
        st.markdown("""
            Voici une presentation démontrant les principales fonctionnalités d'Ilm Notes:
    
            - Ajouter et organiser des notes
            - Réviser efficacement
            - Suivre la progression
            - Exporter et partager des notes
    
            *Vidéo à venir In schaa Allah...*
        """)
    
        st.divider()
        st.markdown("""
            **Ilm Notes** est un outil simple pour aider les étudiants en sciences islamiques
            à organiser, réviser et partager leurs notes بسهولة.
        """)

        with st.expander("1️⃣ Ajouter une note"):
            st.markdown("""
            - Choisis une **catégorie** (Fiqh, Aqida, Tafsir, Hadith, etc.)
            - Écris ta note
            - Ajoute une **référence** si nécessaire
            - Clique sur **Ajouter**
            - Va sur **Organisation** pour voir la note
            """)
    
        with st.expander("2️⃣ Organiser ses notes"):
            st.markdown("""
            - Utilise le **filtre par catégorie**
            - Retrouve facilement ce que tu as déjà étudié
            """)

        with st.expander("3️⃣ Suivre ta progression"):
            st.markdown("""
            - Le graphique montre **sur quelles catégories tu travailles le plus**
            - Plus tu ajoutes de notes, plus ta courbe évolue
            """)
    
        with st.expander("4️⃣ Partager une note"):
            st.markdown("""
            - Clique sur **Copier pour WhatsApp**
            - La note est formatée proprement
            - Tu peux la coller directement dans un groupe ou une chaîne
            """)
    
        with st.expander("5️⃣ Version gratuite et Pro"):
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
        </>

        <div class="ilm-footer">
            <strong>Ilm Notes</strong> 🌙<br>
            <em>
            اللهم علمنا ما ينفعنا وانفعنا بما علمتنا وزدنا علما
            </em>
        </div>
        """,
        unsafe_allow_html=True
    )

def custom_header():
    st.markdown(
    """
    <style>
        /* Cacher uniquement le lien GitHub */
        .stAppHeader{
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="text-align: center; padding: 10px 0; border-bottom: 1px solid #ddd; margin-bottom: 20px;">
            <strong> بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</strong>
        </div>
        """,
        unsafe_allow_html=True
    )