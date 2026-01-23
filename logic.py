from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import streamlit as st
from db import add_note, get_notes,conn,can_add_note,create_user,get_user_plan,upgrade_plan
import pandas as pd
import altair as alt

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
    return f"📘 *{note[1]}*\n\n{note[2]}\n\n📖 Réf : {note[5]}\n— partagé via Ilm Notes"

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

# -----------------------------
# Ajouter une note
# -----------------------------  
def page_ajouter_note(username):
    st.header("➕ Ajouter une nouvelle note")
    st.divider()
    c = conn.cursor()
    if get_user_plan(username) == 'free':
        c.execute("SELECT COUNT(*) FROM notes WHERE created_by=?", (username,))
        count = c.fetchone()[0]
        st.info(f"Plan gratuit : {count}/10 notes utilisées")

    with st.form("add_note_form", clear_on_submit=True):
        title = st.text_input("Titre de la note")
        content = st.text_area("Contenu")
        category = st.selectbox("Catégorie", ["Aqida", "Fiqh", "Tafsir", "Hadith", "Usul", "Akhlaq"])
        subtheme = st.text_input("Sous-thème (optionnel)")
        reference = st.text_input("Référence (livre, savant, cours)")
        submitted = st.form_submit_button("Enregistrer")
                    
        if submitted:
            if title and content:
                if add_note(username, title, content, category, subtheme, reference):
                    st.success("Note enregistrée avec succès")
                else:
                    st.warning("Limite atteinte. Passez au plan PRO pour ajouter des notes illimitées.")
                if st.button("💳 Passer au PRO"):
                    st.info("Redirection vers le paiement... contactez l'administrateur pour plus de détails.\n\n Whatsapp: https://wa.me/237698491583")
                    # après paiement réussi :
                    # upgrade_plan(username)
            else:
                st.error("Le titre et le contenu sont obligatoires")
            
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
            with st.expander(note[1]):
                st.markdown(note[2])
                st.caption(f"📖 {note[5]}")
                col_a, col_b = st.columns(2)
                with col_a:
                    pdf_file = export_note_to_pdf(note)
                    with open(pdf_file, "rb") as f:
                        st.download_button("📄 Export PDF", f, file_name=pdf_file)
                with col_b:
                    if st.button("📋 Copier" , key=f"copy_{note[0]}"):
                        st.code(format_for_whatsapp(note))
                        st.success("Contenu prêt à être collé dans WhatsApp")           
                (format_for_whatsapp(note))

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

    st.altair_chart(chart, use_container_width=True)
